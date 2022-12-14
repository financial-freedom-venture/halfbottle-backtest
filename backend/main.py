from fastapi import FastAPI
from backend.delivery import optionsBacktestOrchestrator
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    optionsBacktestOrchestrator.router,
    prefix="/backtest",
    tags=["strategy backtester"],
)


@app.get("/")
async def root():
    return {"message": "backtest_api"}
