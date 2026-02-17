from datetime import datetime

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import (
    Attendance,
    AttendanceCheckInResponse,
    AttendanceCheckOutResponse,
    AttendanceHistory,
    AttendanceRequest,
    AttendanceResponseBase,
    Student,
)
from sqlalchemy import join
from sqlmodel import Session, select

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/search", response_model=list[AttendanceResponseBase], status_code=200)
async def search_students(q: str, db: Session = Depends(get_session)):
    stmt = (
        select(Student)
        .where(
            Student.nim.contains(q)
            | Student.nama.contains(q)
            | Student.prodi.contains(q)
        )
        .order_by(Student.nim)
    )

    results = db.exec(stmt).all()

    if not results:
        return []

    return [
        AttendanceResponseBase(
            id=0,
            nim=s.nim,
            nama=s.nama,
            jenis_kelamin=s.jenis_kelamin,
            prodi=s.prodi,
            angkatan=s.angkatan,
            foto_url=s.foto_url,
        )
        for s in results
    ]


@router.post("/checkin", response_model=AttendanceCheckInResponse, status_code=201)
async def checkin(req: AttendanceRequest, db: Session = Depends(get_session)):
    existing_session = db.exec(
        select(Attendance).where(
            Attendance.nim == req.nim, Attendance.check_out == None
        )
    ).first()

    if existing_session:
        raise HTTPException(status_code=400, detail="You haven't checked out yet!")

    mhs = db.get(Student, req.nim)
    if not mhs:
        raise HTTPException(status_code=404, detail="Student not found!")

    new_attendance = Attendance(nim=req.nim)

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return AttendanceCheckInResponse(
        id=new_attendance.id,
        nim=mhs.nim,
        nama=mhs.nama,
        jenis_kelamin=mhs.jenis_kelamin,
        prodi=mhs.prodi,
        angkatan=mhs.angkatan,
        foto_url=mhs.foto_url,
        check_in=new_attendance.check_in,
    )


@router.patch("/checkout", response_model=AttendanceCheckOutResponse, status_code=200)
async def checkout(req: AttendanceRequest, db: Session = Depends(get_session)):
    attendance = db.exec(
        select(Attendance).where(
            Attendance.nim == req.nim, Attendance.check_out == None
        )
    ).first()

    if not attendance:
        raise HTTPException(status_code=404, detail="No active check-in session found!")

    mhs = db.get(Student, req.nim)
    if not mhs:
        raise HTTPException(status_code=404, detail="Student not found!")

    attendance.check_out = datetime.now()

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return AttendanceCheckOutResponse(
        id=attendance.id,
        nim=mhs.nim,
        nama=mhs.nama,
        jenis_kelamin=mhs.jenis_kelamin,
        prodi=mhs.prodi,
        angkatan=mhs.angkatan,
        foto_url=mhs.foto_url,
        check_out=attendance.check_out,
    )


@router.get("/history", response_model=list[AttendanceHistory], status_code=200)
async def get_history(db: Session = Depends(get_session)):
    stmt = (
        select(Attendance, Student)
        .join(Student, Attendance.nim == Student.nim)
        .order_by(Attendance.check_in.desc())
    )

    results = db.exec(stmt).all()

    if not results:
        return []

    return [
        AttendanceHistory(
            id=a.id,
            nim=s.nim,
            nama=s.nama,
            jenis_kelamin=s.jenis_kelamin,
            prodi=s.prodi,
            angkatan=s.angkatan,
            foto_url=s.foto_url,
            check_in=a.check_in,
            check_out=a.check_out,
        )
        for a, s in results
    ]

