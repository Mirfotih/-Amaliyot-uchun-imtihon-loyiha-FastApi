from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="EXAM Api")


from routers import auth
from routers import posts

app.include_router(auth.router)
app.include_router(posts.router)


# app.mount("/media", StaticFiles(directory="media"), name="media")