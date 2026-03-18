from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original uploaded filename")
    status: str = Field(..., description="accepted | cached | failed")
    message: str = Field(..., description="Human-readable upload status")
    trace_id: str = Field(..., description="Request trace identifier")
