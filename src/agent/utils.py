import os
from logging import getLogger
from fastapi import File, UploadFile
from src.config.config_client import get_config
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

logger = getLogger(__name__)

DOCUMENT_ANSWER_PROMPT = """Use the following pieces of context to answer the question at the end.
 If you don't know the answer, just say  Oops! We are unable to find any relevant information from the documents to answer your question, don't try to make up an answer.

Context:
{context}

Instructions:
1. You always answer the with markdown formatting. You will be penalized if you do not answer with markdown when it would be possible. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes.
2. Don't mention markdown or ``` in the response.
3. Highlight important sections in the Answer in Bold.
4. Use bullets to format the long answers.
5..Your response should be comprehensive and not contradicted with the following context if they are relevant. Otherwise, ignore them if they are not relevant.

Question: {question}

Answer:
"""


def get_embeddings_model():
    from src.main import sentence_encoder_models

    return sentence_encoder_models["SBERT"]


def save_upload_file(uploaded_file: UploadFile = File(...), overwrite: bool = False):
    file_location = f"{get_config().get('DOWNLOAD_FOLDER', 'download_data/')}/{uploaded_file.filename}"
    if os.path.exists(file_location) and overwrite:
        logger.info(f"The file '{file_location}' exists., Overwriting It")
        os.remove(file_location)
        with open(file_location, "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        return True
    elif os.path.exists(file_location):
        logger.info(f"The file '{file_location}' exists.")
        return False
    else:
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        logger.info(f"info: file {uploaded_file.filename}, saved _at : {file_location}")
        return True


def get_documents(documents, file_path, splitter):
    copilot_documents = []
    for doc in documents:
        content = doc.page_content
        content = content.replace("-", "")
        content = content.replace("_", "")
        doc_meta_data = doc.metadata
        doc_meta_data.pop("Creator", None)
        doc_meta_data.pop("ModDate", None)
        doc_meta_data.pop("Producer", None)
        doc_meta_data.pop("CreationDate", None)
        doc_meta_data["agent"] = "Document"
        doc_meta_data["file_path"] = file_path
        document = Document(page_content=content, metadata=doc_meta_data)
        split_documents = splitter.split_documents([document])
        copilot_documents.extend(split_documents)
    return copilot_documents


class AgentException(Exception):
    """
        Class for Agent related exceptions
    """

    def __init__(self,
                 code,
                 message="",
                 display_message=''):
        self.code = code
        self.message = message
        self.displayMessage = display_message
        super().__init__(self.message)
