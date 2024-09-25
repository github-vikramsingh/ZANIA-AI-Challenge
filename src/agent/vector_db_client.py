import os
import time
import uuid
from collections import Counter

import weaviate
import weaviate.classes as wvc
from weaviate.gql.get import HybridFusion
from fastapi.logger import logger
from langchain_core.documents.base import Document
from langchain_weaviate import WeaviateVectorStore
from retrying import retry
from stop_words import get_stop_words

from src.config.config_client import get_config
from src.agent.utils import get_embeddings_model
from src.startup_constants import EMBEDDINGS_MODEL_NOT_AVAILABLE

weaviate_http_host = get_config().get("WEAVIATE_HTTP_HOST", "localhost")
weaviate_http_port = get_config().get("WEAVIATE_HTTP_PORT", "8080")
weaviate_grpc_host = get_config().get("WEAVIATE_GRPC_HOST", "localhost")
weaviate_grpc_port = get_config().get("WEAVIATE_GRPC_PORT", "50051")
cachedStopWords = get_stop_words("english")
stopwords_dict = Counter(cachedStopWords)


@retry(stop_max_attempt_number=3, wait_fixed=2000, wrap_exception=True)
def get_vector_db_client():
    profile = os.getenv("ENVIRONMENT_NAME")
    if profile != "local":
        return weaviate.connect_to_custom(http_host=weaviate_http_host, http_port=weaviate_http_port,
                                          grpc_host=weaviate_grpc_host, grpc_port=weaviate_grpc_port,
                                          http_secure=False, grpc_secure=False,
                                          additional_config=weaviate.config.AdditionalConfig(startup_period=10,
                                                                                             timeout=(30, 300),
                                                                                             ),
                                          skip_init_checks=True)
    else:
        return weaviate.connect_to_embedded(persistence_data_path="data_weaviate", binary_path="data_weaviate/cache")


def is_schema_exists(index_name):
    with get_vector_db_client() as client:
        return client.collections.exists(index_name)


def get_row_count(index_name):
    with get_vector_db_client() as client:
        index_name = index_name.lower()
        collection = client.collections.get(index_name)
        if collection:
            response = collection.aggregate.over_all(total_count=True)
            row_count = response.total_count
            return row_count


def get_vector_store(client, collection_name, embeddings):
    copilot_vectorstore = WeaviateVectorStore(
        client,
        index_name=collection_name.lower(),
        embedding=embeddings,
        text_key="text"
    )
    return copilot_vectorstore


def get_index_name(project_id, collection_name):
    return f"{project_id.lower()}_{collection_name.lower()}"


def __get_meta_data(prop):
    return str(prop) if isinstance(prop, uuid.UUID) else prop


def __populate_result__(response, similarity_score):
    metadata = {}
    string_encode = ''
    for prop in response.properties:
        if prop != "text":
            metadata[prop] = __get_meta_data(response.properties.get(prop))
        else:
            string_encode = response.properties.get("text").encode("ascii", "ignore")
    metadata["score"] = f'{similarity_score:.2f}'
    metadata["id"] = str(response.uuid)
    string_decode = string_encode.decode()
    return Document(
        page_content=string_decode,
        metadata=metadata,
    )


def __parse_hybrid_search_response__(responses):
    results = []
    for resp in responses.objects:
        result = __populate_result__(resp, resp.metadata.score)
        if result:
            results.append(result)
    return results


def __parse_vector_search_response__(responses):
    results = []
    for resp in responses.objects:
        result = __populate_result__(resp, resp.metadata.distance)
        if result:
            results.append(result)
    return results


# https://weaviate.io/developers/weaviate/search/hybrid
# You can use the alpha argument to weight the keyword (bm25) or vector search results.
# An alpha of 1 is for a pure vector search and 0 is for a pure keyword search. The default is 0.75.
def execute_hybrid_search_with_filters(query, index_name, limit, filters, alpha=1):
    with get_vector_db_client() as client:
        embeddings = get_embeddings_model()
        embedded_query = embeddings.embed_query(query)
        collection = client.collections.get(index_name)
        response = collection.query.hybrid(
            query=query,
            vector=embedded_query,
            alpha=alpha,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(score=True),
            filters=filters
        )

        return __parse_hybrid_search_response__(response)


def execute_hybrid_search_without_filters(query, index_name, limit, alpha=1):
    with get_vector_db_client() as client:
        embeddings = get_embeddings_model()
        if query:
            if not embeddings:
                raise RuntimeError(EMBEDDINGS_MODEL_NOT_AVAILABLE)
            embedded_query = embeddings.embed_query(query)
            collection = client.collections.get(index_name)
            logger.info(f"Search Query: {query}")
            response = collection.query.hybrid(
                query=query,
                query_properties=["source^2", "text"],
                vector=embedded_query,
                alpha=alpha,
                fusion_type=HybridFusion.RELATIVE_SCORE,
                auto_limit=limit,
                return_metadata=wvc.query.MetadataQuery(score=True)
            )

            return __parse_hybrid_search_response__(response)
    return []


def execute_pure_vector_search_with_filters(query, index_name, search_limit, query_filters):
    embeddings = get_embeddings_model()
    if not embeddings:
        raise RuntimeError(EMBEDDINGS_MODEL_NOT_AVAILABLE)
    embedded_query = embeddings.embed_query(query)
    with get_vector_db_client() as client:
        collection = client.collections.get(index_name)
        response = collection.query.near_vector(near_vector=embedded_query, limit=search_limit, filters=query_filters,
                                                return_metadata=wvc.query.MetadataQuery(distance=True))

        return __parse_vector_search_response__(response)


def execute_pure_vector_search_without_filters(query, index_name, search_limit):
    embeddings = get_embeddings_model()
    if not embeddings:
        raise RuntimeError(EMBEDDINGS_MODEL_NOT_AVAILABLE)
    embedded_query = embeddings.embed_query(query)
    with get_vector_db_client() as client:
        collection = client.collections.get(index_name)
        response = collection.query.near_vector(near_vector=embedded_query, limit=search_limit,
                                                return_metadata=wvc.query.MetadataQuery(distance=True))

        return __parse_vector_search_response__(response)


def delete_documents_by_ids(ids, index_name):
    with get_vector_db_client() as client:
        if ids is None:
            raise ValueError("No ids provided to delete.")
        for doc_id in ids:
            collection = client.collections.get(index_name)
            collection.data.delete_by_id(doc_id)


def delete_collection(collection_name, project_id):
    index_name = get_index_name(project_id, collection_name)
    with get_vector_db_client() as client:
        client.collections.delete(index_name)


def add_embeddings(docs, embeddings, collection_name, project_id):
    index_name = get_index_name(project_id, collection_name)
    with get_vector_db_client() as client:
        copilot_vectorstore = get_vector_store(client, index_name, embeddings)
        copilot_vectorstore.add_documents(docs)
    row_count = get_row_count(index_name)
    logger.info(f"After Adding documents to index {index_name} row-count={row_count}")
