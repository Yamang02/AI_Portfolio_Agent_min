from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    request_id: str
