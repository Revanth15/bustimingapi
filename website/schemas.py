from pydantic import BaseModel

class UserDetailsUpdate(BaseModel):
    ban: bool
    requestban: bool