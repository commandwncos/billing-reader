from pdf2image.exceptions import PDFPageCountError 
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes
from task import background_task
from pyzbar.pyzbar import decode
from base64 import b64encode
from asyncio import gather
from typing import List
from PIL import Image
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    status,
    HTTPException,
    BackgroundTasks,
    
)
from uuid import uuid4
from api.source.utils.functions.line import calcula_linha
from io import BytesIO
from models.all import DocumentGeral
from re import search


router = APIRouter(
    default_response_class = JSONResponse
    ,include_in_schema=True
)

# parameters
mime_type: str='application/pdf'
dpi:int=300
format:str='JPEG'
encoding='utf-8'
task_id = uuid4()

# return with open ai
@router.post("/uploadfile/", status_code=status.HTTP_202_ACCEPTED, response_model=DocumentGeral)
async def create_upload_file(background: BackgroundTasks, files: List[UploadFile] = File(...)):  

    if len(files) > 10:  
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only 20 files allowed")  
  
    async def save_pdf_as_jpeg(file: UploadFile):  
        if file.size > 654003:  
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Check file size: allow 654003 bytes')  
  
        try:  
            images = convert_from_bytes(await file.read(), dpi=dpi, fmt=format)  
            buffers = []  
            for image in images:  
                buffer = BytesIO()  
                image.save(buffer, format=format)  
                buffer.seek(0)  # Reset buffer position to the beginning  
                buffers.append(buffer)  # Append only the buffer to the list  
            return buffers  
        except PDFPageCountError as e:  
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{file.filename}: {str(e)}")  
  
    async def read_file(buffer: BytesIO):  
        contents = buffer.getvalue()  # Get the bytes from the buffer
        
        bs64_image = b64encode(contents).decode(encoding=encoding)  
        return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{bs64_image}"}}  
  
    async def read_barcode(buffer: BytesIO):  
        buffer.seek(0)  # Reset buffer position to the beginning  
        image = Image.open(buffer)  
        barcode_data = decode(image)  
        if barcode_data:
            barcode = barcode_data[0].data.decode(encoding=encoding)  
            line = calcula_linha(barcode)  # Assuming this function is defined elsewhere  
            return {"type": "text", "text": f"Considere o código de barras ({barcode}) e a linha digitavel ({line})"}  
        return None  
  
    # Process all PDF files and keep images in memory  
    buffers = await gather(*(save_pdf_as_jpeg(file) for file in files if file.content_type == mime_type))  
  
    content_tasks = []  
    barcode_tasks = []  
  
    # Process the buffers for reading images and barcodes  
    for buffer_list in buffers: 
        for buffer in buffer_list:
            content_tasks.append(read_file(buffer))  # Read the image from the buffer  
            barcode_tasks.append(read_barcode(buffer))  # Read the barcode from the buffer  
  
    # Process content and barcodes  
    content = await gather(*content_tasks)  
    content = [valor for valor in content if valor is not None]
    
    barcodes = await gather(*barcode_tasks) 
    barcodes = [valor for valor in barcodes if valor is not None]
  
  
    # Define documents for classification  
    documents = ['Boleto Bancario Seguradora']
  
    messages = [  
        {"role": "system", "content": f"Para cada documento classifique o tipo de documento. Atenha-se a lista: {documents}. e repasse a task id: {task_id}"},  
        {"role": "user", "content": barcodes},
        {"role": "user", "content": content} 
    ]  
  
    # background.add_task(background_task, messages)
    document = background_task(messages)

    # return {"task_id": str(task_id)}  
    return document


@router.post("/validator/", status_code=status.HTTP_200_OK)
async def barcode_validator(barcode: str):
    
    return {
        "linha digitavel": calcula_linha(barcode)
    }

# return without openai
@router.post("/extract/", status_code=status.HTTP_200_OK)  
async def extract(files: List[UploadFile]):  
    documents = []
    for file in files:  
        if file.size > 654003:  
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Check file size: allow 654003 bytes')  
          
        try:  
            images = convert_from_bytes(await file.read(), dpi=dpi, fmt=format)  
        except Exception as e:  
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{file.filename}: {str(e)}")  
          
        for image in images:  
            buffer = BytesIO()  
            image.save(buffer, format=format)  
            buffer.seek(0)  # Reset buffer position to the beginning  
              
            # Lê o código de barras  
            buffer.seek(0)  # Reset buffer position to the beginning  
            img = Image.open(buffer)  
            barcode_data = decode(img)  
            if barcode_data:  
                barcode = barcode_data[0].data.decode(encoding='utf-8')  
                line = calcula_linha(barcode)  # Assumindo que essa função está definida em outro lugar  
  
                # Extrai o valor do boleto do último campo da linha digitável  
                match = search(r'(\d{10})$', line)  # Ajuste o regex conforme o formato da linha digitável  
                boleto_value = None  

                if match:  
                    value = match.group(1)  # Captura os últimos 10 dígitos  
                    # Remove os zeros à esquerda  
                    value = value.lstrip('0')  
                    # Formata o valor como desejado  
                    if len(value) > 2:  
                        integer_part = value[:-2]  # Parte inteira  
                        decimal_part = value[-2:]   # Parte decimal  
                        boleto_value = f"{int(integer_part):,}.{decimal_part}"  # Formata como "valor,centavos"  
                        boleto_value = boleto_value.replace(',', '.')  # Troca a vírgula por ponto  
                        boleto_value = boleto_value.replace('.', ',', 1)  # Troca o primeiro ponto por vírgula  
                    elif len(value) == 2:  
                        boleto_value = f"0,{value}"  # Caso o valor seja menor que 1 real  
                    elif len(value) == 1:  
                        boleto_value = f"0,0{value}"  # Caso o valor seja menor que 10 centavos  
  
                documents.append({  
                    "filename": file.filename,  
                    "barcode": barcode,  
                    "line": line,  
                    "value": boleto_value
                })
    return {"documents": documents}
