from fastapi import FastAPI

app = FastAPI(title="Land of Airdrop API")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
