from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class StudentBase(SQLModel):
    nim: str
    nama: str
    jenis_kelamin: str
    prodi: str
    angkatan: str
    foto_url: str


class Student(StudentBase, table=True):
    nim: str = Field(primary_key=True)


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nim: str = Field(foreign_key="student.nim")
    check_in: datetime = Field(default_factory=datetime.now)
    check_out: Optional[datetime] = None


class AttendanceRequest(SQLModel):
    nim: str


class AttendanceResponseBase(SQLModel):
    id: int
    nim: str
    nama: str
    jenis_kelamin: str
    prodi: str
    angkatan: str
    foto_url: str


class AttendanceCheckInResponse(AttendanceResponseBase):
    check_in: datetime


class AttendanceCheckOutResponse(AttendanceResponseBase):
    check_out: datetime


class AttendanceHistory(AttendanceResponseBase):
    check_in: datetime
    check_out: Optional[datetime] = None


class AdminAuth(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str


class AdminAuthRequest(SQLModel):
    username: str
    password: str


class AdminAuthResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
