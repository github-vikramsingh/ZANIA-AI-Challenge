import os
import pathlib
from contextlib import asynccontextmanager
from random import seed

import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi_pagination import add_pagination
from langchain_community.embeddings import SentenceTransformerEmbeddings

from src.config.config_client import config
from src.routes import document_router as document
from src.schemas.pydantic_models import SBertConfig

from src.agent.utils import AgentException as SourceException
from src.middleware import add_process_time, source_exception_handler

import warnings

warnings.filterwarnings("ignore")

os.environ["ENVIRONMENT_NAME"] = "local"

sentence_encoder_models = {}


def load_embeddings_model(system_config):
    sbert_encoder_config = SBertConfig(**system_config.get("SBERT_CONFIG"))
    sbert_encoder_version = sbert_encoder_config.version
    logger.info(f"Sentence Embeddings Model loaded version: {sbert_encoder_version}")
    sentence_encoder_model = SentenceTransformerEmbeddings(model_name=sbert_encoder_config.model_path)
    return sentence_encoder_model, sbert_encoder_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML models
    sbert_encoder_model, sbert_encoder_model_version = load_embeddings_model(config)
    sentence_encoder_models['SBERT'] = sbert_encoder_model
    sentence_encoder_models['SBERT_VERSION'] = sbert_encoder_model_version

    yield
    # Clean up the ML models and release the resources
    sentence_encoder_models.clear()


seed(42)


def get_openapi_tags():
    return [
        document.tags_metadata
    ]


def create_app() -> FastAPI:
    fastapi_app = FastAPI(title="Document Agent",
                          description="Document Agent implementation",
                          version="1.0.0",
                          lifespan=lifespan,
                          openapi_tags=get_openapi_tags()
                          )
    # Middleware Settings
    fastapi_app.middleware("http")(add_process_time)
    fastapi_app.add_exception_handler(SourceException, source_exception_handler)

    fastapi_app.include_router(document.router)

    return fastapi_app


app = create_app()
add_pagination(app)

if __name__ == "__main__":
    cwd = pathlib.Path(__file__).parent.resolve()
    uvicorn.run("src.main:app", host="0.0.0.0", port=9002)
