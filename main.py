from middlewares.logger import middlewareAddProcessLogger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from api.source.v1.all import API_ROUTER

app = FastAPI(
    title='API de Extração de Informações de Boletos Bancários de Seguradoras'
    ,version='1.0.0'
    ,summary='Esta API permite o envio de múltiplos boletos bancários em formato digital, facilitando a extração automatizada de dados relevantes. Projetada para otimizar a gestão de documentos financeiros, a ferramenta realiza a leitura e interpretação dos boletos, retornando as informações de forma estruturada e acessível.'
    ,openapi_url='/api/v1/openapi.json'
    ,docs_url='/api/v1/docs'
    ,redoc_url='/api/v1/redoc'
    ,root_path='/finance'
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