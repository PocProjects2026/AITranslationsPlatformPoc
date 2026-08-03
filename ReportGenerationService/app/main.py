from fastapi import FastAPI


app = FastAPI(
    title="Report Generation Service",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}