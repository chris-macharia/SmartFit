from fastapi import FastAPI

app = FastAPI(
    title="SmartFit API",
    description="Backend API for the SmartFit Virtual Fitting System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SmartFit API",
        "status": "running"
    }