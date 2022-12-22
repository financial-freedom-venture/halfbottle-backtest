from fastapi import FastAPI
from backend.delivery import intradayBacktester
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
    intradayBacktester.router,
    prefix="/intraday",
    tags=["intraday backtester"],
)


@app.get("/")
async def root():
    return {"message": "backtest_api"}
