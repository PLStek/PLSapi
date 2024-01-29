from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import announcements, charbons, courses, exercise_topics, exercises

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="PLSapi", redoc_url=None, docs_url="/")
app.include_router(charbons.router)
app.include_router(announcements.router)
app.include_router(exercise_topics.router)
app.include_router(courses.router)
app.include_router(exercises.router)

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
