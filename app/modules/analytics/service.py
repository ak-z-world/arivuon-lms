# app/modules/analytics/service.py
"""
Dashboard service — aggregates data from Users, Batches, Sessions,
Attendance, and Courses into dashboard payloads for each role.
No new DB models required; queries run against existing tables.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException

# ── Model imports from existing modules ──
from app.modules.users.models     import User, StudentProfile, TrainerProfile
from app.modules.batches.models   import Batch, BatchStudent
from app.modules.schedules.models  import BatchSession, SessionAttendance
from app.modules.courses.models   import Course
from app.modules.attendance.models import AttendanceRecord, AttendanceSession

from . import schemas


# ══════════════════════════════════════════════════════
#  Helper queries
# ══════════════════════════════════════════════════════

def _get_user_or_404(db: Session, user_uuid: str) -> User:
    user = db.query(User).filter(User.uuid == user_uuid).first()
    print(f'user not found: {user}')
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def _get_student_or_404(db: Session, user_uuid: str) -> tuple[User, StudentProfile]:
    
    student = db.query(User).filter(User.uuid == user_uuid).first()
    print(f'student query: {student}')
    if not student:
        raise HTTPException(status_code=404, detail="User not found")

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student.id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return student, student_profile

def _user_mini(u: User) -> schemas.UserMini:
    return schemas.UserMini(id=u.id, uuid=u.uuid, name=u.name, email=u.email)


def _course_mini(c: Course | None) -> schemas.CourseMini | None:
    if not c:
        return None
    return schemas.CourseMini(id=c.id, uuid=c.uuid, title=c.title, level=c.level)


def _batch_mini(b: Batch) -> schemas.BatchMini:
    return schemas.BatchMini(
        id=b.id, uuid=b.uuid, name=b.name, status=b.status,
        start_date=b.start_date, end_date=b.end_date,
        course=_course_mini(b.course) if b.course else None,
    )


def _upcoming_session(s: BatchSession) -> schemas.UpcomingSession:
    return schemas.UpcomingSession(
        uuid=s.uuid, title=s.title,
        session_number=s.session_number,
        session_date=s.session_date,
        start_time=s.start_time,
        end_time=s.end_time,
        status=s.status,
        meeting_link=s.meeting_link,
        batch_name=s.batch.name if s.batch else None,
        course_title=s.batch.course.title if (s.batch and s.batch.course) else None,
    )


def _attendance_stat(db: Session, session_ids: list[int]) -> schemas.AttendanceStat:
    """Aggregate attendance counts across a list of batch_session IDs."""
    if not session_ids:
        return schemas.AttendanceStat(total=0, present=0, absent=0, late=0, pct=0.0)

    rows = (
        db.query(
            AttendanceRecord.status,
            func.count(AttendanceRecord.id).label("cnt"),
        )
        .join(AttendanceSession,
              AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .filter(AttendanceSession.batch_session_id.in_(session_ids))
        .group_by(AttendanceRecord.status)
        .all()
    )
    counts = {r.status: r.cnt for r in rows}
    present = counts.get("present", 0)
    absent  = counts.get("absent", 0)
    late    = counts.get("late", 0)
    excused = counts.get("excused", 0)
    total   = present + absent + late + excused
    pct     = round((present + late) / total * 100, 1) if total else 0.0
    return schemas.AttendanceStat(total=total, present=present, absent=absent, late=late, pct=pct)


# ══════════════════════════════════════════════════════
#  TRAINER DASHBOARD
# ══════════════════════════════════════════════════════

def get_trainer_dashboard(db: Session, trainer_uuid: str) -> schemas.TrainerDashboard:
    trainer = _get_user_or_404(db, trainer_uuid)

    # All batches assigned to this trainer
    batches = (
        db.query(Batch)
        .options(
            joinedload(Batch.course),
            joinedload(Batch.students),
        )
        .filter(Batch.trainer_id == trainer.id)
        .all()
    )

    batch_ids = [b.id for b in batches]
    active_batches = [b for b in batches if b.status == "active"]

    # All sessions for this trainer
    all_sessions = (
        db.query(BatchSession)
        .options(joinedload(BatchSession.batch).joinedload(Batch.course))
        .filter(BatchSession.trainer_id == trainer.id)
        .all()
    )

    today = date.today()
    today_sessions  = [s for s in all_sessions if s.session_date == today]
    upcoming        = sorted(
        [s for s in all_sessions
         if s.session_date >= today and s.status in ("scheduled", "live")],
        key=lambda x: (x.session_date, x.start_time or datetime.min.time())
    )[:5]
    recent_completed = sorted(
        [s for s in all_sessions if s.status == "completed"],
        key=lambda x: x.session_date, reverse=True
    )[:5]

    all_session_ids = [s.id for s in all_sessions]

    # Build per-batch summaries
    batch_summaries = []
    for b in batches:
        b_sessions    = [s for s in all_sessions if s.batch_id == b.id]
        b_session_ids = [s.id for s in b_sessions]
        completed     = len([s for s in b_sessions if s.status == "completed"])
        total         = len(b_sessions)
        prog_pct      = round(completed / total * 100, 1) if total else 0.0
        att_stat      = _attendance_stat(db, b_session_ids)

        batch_summaries.append(schemas.TrainerBatchSummary(
            batch=_batch_mini(b),
            student_count=len(b.students),
            session_count=total,
            completed_sessions=completed,
            progress_pct=prog_pct,
            attendance_avg=att_stat.pct,
        ))

    # Overall attendance
    overall_att = _attendance_stat(db, all_session_ids)

    # Total unique students across all batches
    all_student_ids = set()
    for b in batches:
        all_student_ids.update(bs.student_id for bs in b.students)

    return schemas.TrainerDashboard(
        trainer=_user_mini(trainer),
        total_batches=len(batches),
        active_batches=len(active_batches),
        total_students=len(all_student_ids),
        total_sessions=len(all_sessions),
        sessions_today=len(today_sessions),
        upcoming_sessions=[_upcoming_session(s) for s in upcoming],
        batch_summaries=batch_summaries,
        overall_attendance=overall_att,
        recent_sessions=[_upcoming_session(s) for s in recent_completed],
    )


# ══════════════════════════════════════════════════════
#  STUDENT DASHBOARD
# ══════════════════════════════════════════════════════

def get_student_dashboard(db: Session, student_uuid: str) -> schemas.StudentDashboard:
    student, student_profile = _get_student_or_404(db, student_uuid)
    print(f'student: {student}')
    print(f'student profile: {student_profile}')
    # Batches the student is enrolled in
    enrolments = (
        db.query(BatchStudent)
        .options(
            joinedload(BatchStudent.batch)
            .joinedload(Batch.course),
        )
        .filter(BatchStudent.student_id == student.id)
        .all()
    )
    batch_ids = [e.batch_id for e in enrolments]

    # All sessions for those batches
    all_sessions = (
        db.query(BatchSession)
        .options(joinedload(BatchSession.batch).joinedload(Batch.course))
        .filter(BatchSession.batch_id.in_(batch_ids))
        .all()
    ) if batch_ids else []

    today = date.today()
    upcoming = sorted(
        [s for s in all_sessions
         if s.session_date >= today and s.status in ("scheduled", "live")],
        key=lambda x: (x.session_date, x.start_time or datetime.min.time())
    )[:5]

    # Attendance records for this student
    att_records = (
        db.query(AttendanceRecord)
        .join(AttendanceSession,
              AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .options(
            joinedload(AttendanceRecord.attendance_session)
            .joinedload(AttendanceSession.batch_session)
        )
        .filter(AttendanceRecord.student_id == student.id)
        .order_by(AttendanceRecord.checked_in_at.desc())
        .all()
    )

    present_count = len([r for r in att_records if r.status == "present"])
    late_count    = len([r for r in att_records if r.status == "late"])
    total_att     = len(att_records)
    att_pct       = round((present_count + late_count) / total_att * 100, 1) if total_att else 0.0

    # Per-batch progress
    course_progress = []
    for enrolment in enrolments:
        b = enrolment.batch
        b_sessions = [s for s in all_sessions if s.batch_id == b.id]
        b_session_ids = [s.id for s in b_sessions]

        # Attendance sessions for this batch's sessions
        att_session_ids = [
            a.id for a in db.query(AttendanceSession.id)
            .filter(AttendanceSession.batch_session_id.in_(b_session_ids))
            .all()
        ]
        attended = len([
            r for r in att_records
            if r.attendance_session_id in att_session_ids
               and r.status in ("present", "late")
        ])
        total = len(b_sessions)
        last_session_date = max(
            (s.session_date for s in b_sessions if s.status == "completed"),
            default=None,
        )
        course_progress.append(schemas.StudentCourseProgress(
            batch=_batch_mini(b),
            sessions_attended=attended,
            total_sessions=total,
            attendance_pct=round(attended / total * 100, 1) if total else 0.0,
            last_session_date=last_session_date,
        ))

    recent_att = [
        {
            "uuid":         r.uuid,
            "status":       r.status,
            "checked_in_at": str(r.checked_in_at) if r.checked_in_at else None,
            "session_title": r.attendance_session.batch_session.title
                             if r.attendance_session and r.attendance_session.batch_session
                             else "—",
        }
        for r in att_records[:10]
    ]

    return schemas.StudentDashboard(
        student=_user_mini(student),
        enrolled_batches=len(enrolments),
        sessions_attended=present_count + late_count,
        total_sessions=len(all_sessions),
        attendance_pct=att_pct,
        course_progress=course_progress,
        upcoming_sessions=[_upcoming_session(s) for s in upcoming],
        recent_attendance=recent_att,
    )


# ══════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════════════

def get_admin_dashboard(db: Session) -> schemas.AdminDashboard:
    today = date.today()

    total_students = db.query(func.count(User.id)).filter(User.role == "student").scalar() or 0
    total_trainers = db.query(func.count(User.id)).filter(User.role == "trainer").scalar() or 0
    total_courses  = db.query(func.count(Course.id)).scalar() or 0
    total_batches  = db.query(func.count(Batch.id)).scalar() or 0
    active_batches = db.query(func.count(Batch.id)).filter(Batch.status == "active").scalar() or 0

    sessions_today = (
        db.query(func.count(BatchSession.id))
        .filter(BatchSession.session_date == today)
        .scalar() or 0
    )

    # Revenue from student profiles
    rev_row = db.query(
        func.sum(StudentProfile.amount_paid).label("collected"),
        func.sum(StudentProfile.course_fee).label("total_fee"),
    ).first()
    collected = float(rev_row.collected or 0)
    total_fee  = float(rev_row.total_fee or 0)
    pending    = max(0.0, total_fee - collected)

    # Upcoming sessions (next 5)
    upcoming = (
        db.query(BatchSession)
        .options(joinedload(BatchSession.batch).joinedload(Batch.course))
        .filter(BatchSession.session_date >= today,
                BatchSession.status.in_(["scheduled", "live"]))
        .order_by(BatchSession.session_date, BatchSession.start_time)
        .limit(5)
        .all()
    )

    # Recent users (last 10)
    recent_users = (
        db.query(User)
        .order_by(User.id.desc())
        .limit(10)
        .all()
    )

    # Overall platform attendance
    all_session_ids = [r[0] for r in db.query(BatchSession.id).all()]
    overall_att = _attendance_stat(db, all_session_ids)

    return schemas.AdminDashboard(
        total_students=total_students,
        total_trainers=total_trainers,
        total_courses=total_courses,
        total_batches=total_batches,
        active_batches=active_batches,
        sessions_today=sessions_today,
        overall_attendance=overall_att,
        revenue_collected=collected,
        revenue_pending=pending,
        recent_users=[_user_mini(u) for u in recent_users],
        upcoming_sessions=[_upcoming_session(s) for s in upcoming],
    )

