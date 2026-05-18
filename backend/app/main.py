"""FastAPI application entry point for LapVisualizer."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    """Return a basic greeting payload."""
    return {"message": "Hello World"}
