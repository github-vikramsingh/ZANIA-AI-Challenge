from fastapi.logger import logger
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, NLTKTextSplitter
from src.agent.utils import get_embeddings_model, get_documents
from src.config.config_client import config
from src.agent.vector_db_client import get_vector_db_client, get_vector_store


class GenerateEmbedding:
    raw_data_path = config.get("DOWNLOAD_FOLDER", "download_data")
    collection_name = "zania"

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def load_documents(self):
        document_loader = PyPDFDirectoryLoader(self.raw_data_path)
        return document_loader.lazy_load()

    def data_splitting(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False,
        )
        # text_splitter = NLTKTextSplitter(
        #     chunk_size=config.get("PDF_CHUNK_SIZE", 500)
        # )
        # return text_splitter.split_documents(documents)
        copilot_documents = get_documents(documents, self.collection_name, text_splitter)
        return copilot_documents

    @staticmethod
    def vectorstore_db_insertion(docs):
        embeddings = get_embeddings_model()
        with get_vector_db_client() as client:
            copilot_vectorstore = get_vector_store(client=client, embeddings=embeddings, collection_name="zania")
            for count, doc in enumerate(docs):
                logger.debug(f"Persisting batch {count}")
                copilot_vectorstore.add_documents([doc])

    def execute(self):
        documents = self.load_documents()
        chunks = self.data_splitting(documents=documents)
        self.vectorstore_db_insertion(chunks)
