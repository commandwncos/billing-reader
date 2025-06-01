from api.source.utils.logger import logger,  INFO
from fastapi import Request
from time import time
from datetime import datetime

async def middlewareAddProcessLogger(request: Request, callNext) -> dict:
    start = time()
    response = await callNext(request)
    finish = time()-start
    logger.info({
        'DATETIME': datetime.now().strftime('%Y:%m:%d %H:%M:%S')
        ,'URL': request.url.path
        ,'DURATION': finish
        ,'LOG-LEVEL': INFO
    })
    return response
