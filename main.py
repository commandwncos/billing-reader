from middlewares.logger import middlewareAddProcessLogger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from api.source.v1.all import API_ROUTER


app = FastAPI(
    title='API Documentation'
    ,version='1.0.0'
)


app.include_router(API_ROUTER)
app.add_middleware(
    BaseHTTPMiddleware
    ,dispatch=middlewareAddProcessLogger
)






if __name__=='__main__':
    from uvicorn import run
    run(
        app='main:app',
        host='0.0.0.0',
        port=3000,
        reload=True,
        log_level='trace'
    )