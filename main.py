from fastapi import FastAPI

import models
from database import engine
from routers import announcements, charbons

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="PLSapi", docs_url=None, redoc_url="/docs")
app.include_router(charbons.router)
app.include_router(announcements.router)
