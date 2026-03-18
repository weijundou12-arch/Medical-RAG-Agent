from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    document_id: str = Field(..., description="Document identifier returned at upload")
    question: str = Field(..., min_length=3, description="User question")
    top_k: int = Field(5, ge=1, le=10, description="Number of chunks to retrieve")
