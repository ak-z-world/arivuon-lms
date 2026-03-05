from fastapi import FastAPI
from app.database.base import Base
from app.database.session import engine
from app.modules.users.router import router as users_router
from app.modules.courses.router import router as courses_router
from app.modules.batches.router import router as batches_router
from app.modules.schedules.router import router as schedules_router

app = FastAPI(title="AI LMS")
Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(batches_router)
app.include_router(schedules_router)
