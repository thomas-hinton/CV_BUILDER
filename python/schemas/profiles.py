from pydantic import BaseModel


class ModifyNameRequest(BaseModel):
    name: str
