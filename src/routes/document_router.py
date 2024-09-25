from typing import Optional, List
from fastapi import Query, APIRouter, UploadFile, File
from src.agent.controller import DocumentAgent

router = APIRouter(
    prefix="/agent-document",
    tags=["agent"],
)

tags_metadata = {
    "name": "agent",
    "description": "Document Agent Knowledge Base",
}


@router.post("/execute",
             tags=["agent"],
             status_code=200,
             summary="Generate the Embeddings and Use the Document Space to answer the question"
             )
async def answer_question_using_documents_space(
        questions: List[str] = Query(
            default=None,
            description="List of questions to answer"
        ),
        override: Optional[bool] = Query(
            default=False,
            description="Override the existing embeddings if exists for the given project"
        ),
        file: UploadFile = File(None)
):
    agent = DocumentAgent(queries=questions, file=file, override=override)
    response = await agent.execute()
    return response
