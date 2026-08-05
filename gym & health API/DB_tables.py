from sqlalchemy import Column, Integer, String, Boolean
from motorForDB import base







class GymMemberDB(base):

    __tablename__ = "gym_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    is_active = Column(Boolean)