from pydantic import BaseModel









# Pydantic BaseModel
class Membership(BaseModel):
    name: str
    age: int
    is_active: bool


    # Dit zorgt ervoor dat Pydantic data uit de SQLAlchemy ORM-modellen kan lezen
    class Config:
        from_attributes = True