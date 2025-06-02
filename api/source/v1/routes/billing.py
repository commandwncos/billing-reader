from fastapi import (APIRouter, UploadFile, File, status)
from fastapi.responses import JSONResponse
from models.all import ResponseModel
from asyncio import gather
from typing import List
from api.source.utils.functions.background import (
    check_size,
    convert_pdf_to_images,
    lenght,
    process_documents_with_azure
)

router = APIRouter(
    default_response_class = JSONResponse
    ,include_in_schema=True
)

# parameters
mime_type: str='application/pdf'
dpi:int=300
format:str='JPEG'
encoding='utf-8'

@router.post('/upload',
             response_model=List[ResponseModel],
             summary='Endpoint para upload dos documentos bancarios',
             status_code=status.HTTP_202_ACCEPTED,
             response_description='Accepted'
)
async def billing_extract(files: List[UploadFile] = File(...)):
    files = lenght(files, 30)
    files = await gather(*(check_size(file, 654003) for file in files if file.content_type == mime_type))
    documents = await gather(*(convert_pdf_to_images(file, dpi, format, encoding) for file in files))
    response = await process_documents_with_azure(documents=documents)
    return documents


