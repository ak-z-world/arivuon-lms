from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.base import Base
from app.database.session import engine
from app.modules.users.router import router as users_router
from app.modules.courses.router import router as courses_router
from app.modules.batches.router import router as batches_router
from app.modules.schedules.router import router as schedules_router
from app.modules.auth.router import router as auth_routers



app = FastAPI(title="AI LMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(batches_router)
app.include_router(schedules_router)
app.include_router(auth_routers)
