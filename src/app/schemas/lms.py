from datetime import datetime
from pydantic import BaseModel, EmailStr


class Course(BaseModel):
    id: int
    title: str
    teacher: str
    group_name: str
    progress: int
    modules: int
    status: str
    updated_at: datetime | None = None


class VisitLeadIn(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str


class VisitLeadOut(BaseModel):
    id: str
    created_at: datetime
