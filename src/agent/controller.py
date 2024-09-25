import asyncio
import warnings
from fastapi.logger import logger
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.agent.utils import *
from src.startup_constants import *
from src.config.config_client import config
from src.agent.embedding_generation import GenerateEmbedding
from src.agent.vector_db_client import execute_pure_vector_search_without_filters

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


class DocumentAgent:
    collection_name = "zania"
    vector_db_path = config.get('VECTOR_DB_PATH', 'data_weaviate')
    raw_data_path = config.get("DOWNLOAD_FOLDER", "download_data")
    alpha = config.get("HYBRID_ALPHA", "0.8")
    top_k = config.get("TOP_K", "2")
    min_distance = config.get("MIN_DISTANCE", "0.40")
    max_documents = config.get("MAX_DOCUMENTS", "10")

    def __init__(self, queries: list, file: UploadFile = File(None), override: bool = False):
        self.queries = queries
        self.file = file
        self.override = override
        self.format_response: list[dict] = []

    def __generate_embedding_function__(self):
        try:
            upload = save_upload_file(uploaded_file=self.file, overwrite=self.override)
            if upload or self.override or not os.path.exists(f"{self.vector_db_path}/{self.collection_name}"):
                GenerateEmbedding().execute()
            else:
                logger.info("Embedding already exist, No updation done.")
        except Exception as e:
            logger.info(f"Failed while embedding generation")
            logger.error(e, exc_info=True)

    async def __get_documents__(self, query_text):
        try:
            if docs_and_scores := execute_pure_vector_search_without_filters(query=query_text,
                                                                             index_name=self.collection_name,
                                                                             search_limit=self.top_k):
                documents = [dict(page_content=doc.page_content, metadata=doc.metadata) for doc in docs_and_scores]
                self.format_response.append(dict(question=query_text, answer="", documents=documents))
                context_text = "\n\n---\n\n".join([doc.page_content for doc in docs_and_scores])
                return context_text
        except Exception as e:
            logger.info(f"Failed while retrieving documents for question {query_text}")
            logger.error(e, exc_info=True)
            return None

    async def __generate_summary__(self):
        try:
            # Creating OpenAI Model Instance
            model_type = config.get("DOCUMENT_AGENT_LLM_TYPE", "OPENAI_GPT_4o_MINI")
            openai_keys = config.get(model_type, {})
            model = ChatOpenAI(
                openai_api_key=openai_keys.get("OPENAI_API_KEY"),
                model_name=openai_keys.get("MODEL_NAME"),
                temperature=openai_keys.get("TEMPERATURE")
            )

            ## Iterating over Questions to create async task, which can be further executed all at once.
            async_tasks = []
            prompt_template = ChatPromptTemplate.from_template(DOCUMENT_ANSWER_PROMPT)
            for query in self.queries:
                context_info = await self.__get_documents__(query_text=query)
                if not context_info:
                    logger.info(f"Failed while retrieving documents for question {query}")
                    continue

                prompt = prompt_template.format(context=context_info, question=query)
                async_tasks.append(asyncio.create_task(coro=model.ainvoke(prompt), name=query))

            ## Calling Async Task
            llm_response = await asyncio.gather(*async_tasks)
            if not llm_response:
                logger.error("Received empty response from LLM async call, raising assertion error")
                raise AgentException(code=400, display_message=GENERIC_ERROR,
                                     message="Received empty response from LLM")

            for k, resp in enumerate(llm_response):
                if not resp.content:
                    del self.format_response[k]
                    continue
                self.format_response[k].update({"answer": resp.content})

        except Exception as e:
            logger.error(f"Error while generating LLM response")
            logger.error(e, exc_info=True)

    async def execute(self):
        try:
            self.__generate_embedding_function__()
            await self.__generate_summary__()
            if not self.format_response:
                raise AgentException(code=400, display_message=GENERIC_ERROR,
                                     message="Document Agent execution failed while formatting the response")
            return self.format_response
        except Exception as e:
            logger.info(f"Document Agent execution failed")
            logger.error(e, exc_info=True)
            return AgentException(code=400, display_message=GENERIC_ERROR,
                                  message="Received empty response from LLM").__dict__
