from pydantic import BaseModel


class EmployeeBase(BaseModel):
    slug: str
    fullname: str
    active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    slug: str | None = None
    fullname: str | None = None
    active: bool | None = None


class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True