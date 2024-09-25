from typing import Optional, Any
from src.schemas.base import CoPilotBaseModel


class SBertConfig(CoPilotBaseModel):
    model_path: str
    version: str


class DocumentResult(CoPilotBaseModel):
    id: Optional[str] = None
    content: str
    score: Optional[float] = None
    metadata: Optional[Any] = None


class SystemMessage(CoPilotBaseModel):
    code: int
    message: str
    displayMessage: str
