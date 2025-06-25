from fastapi import FastAPI
from routers import portfolio

app = FastAPI()

app.include_router(portfolio.router)

@app.get("/")
def read_root():
    return {"message": "🚀 BitPanel API is live!"}