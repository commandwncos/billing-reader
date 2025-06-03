from models.all import Clone, Document, ResponseModel
from asyncio import Semaphore, gather
from dotenv import load_dotenv as ld
from fastapi import HTTPException
from openai import AzureOpenAI
from os import getenv as genv
from asyncio import sleep
from typing import List
from fastapi import (
    UploadFile,
    status,
    HTTPException
)
from api.source.utils.functions.line import calcula_linha
from pyzbar.pyzbar import decode
from pdf2image import convert_from_bytes
from base64 import b64encode
from PIL import Image
from io import BytesIO
from re import search
ld()


# lenght of document
def lenght(array: List[UploadFile], number: int):
    if len(array) > number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 20 files allowed",
        )
    return array

# check size
async def check_size(file: UploadFile, size: int):
    if file.size > size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Check file size: allow {size} bytes'
        )
    return file

# return image list
async def convert_pdf_to_images(file: UploadFile, dpi: int, fmt:str, encode:str):
    images = convert_from_bytes(await file.read(), dpi=dpi, fmt=fmt)
    for image in images:
        buffer = BytesIO()
        image.save(buffer, format=fmt)
        buffer.seek(0)
        barcode_data = decode(Image.open(buffer))
        image_base64 = b64encode(buffer.getvalue()).decode(encode)  
        if barcode_data:
            barcode = barcode_data[0].data.decode(encoding=encode)
            line = calcula_linha(barcode)
            match = search(r'(\d{10})$', line)
            boleto_value = None
            if match:
                value = match.group(1)
                value = value.lstrip('0')
                if len(value) > 2:
                    integer_part = value[:-2]
                    decimal_part = value[-2:]
                    boleto_value = f"{int(integer_part):,}.{decimal_part}"
                    boleto_value = boleto_value.replace(',', '.')
                    boleto_value = boleto_value.replace('.', ',', 1)
                elif len(value) == 2:
                    boleto_value = f"0,{value}"
                elif len(value) == 1:
                    boleto_value = f"0,0{value}"
            return Document(
                filename=file.filename,
                barcode=barcode,
                line=line,
                value=round(int(value) / 100, 2),
                # image_base64=image_base64
            )

# process single document
async def process_single_document_with_azure(client: AzureOpenAI, document: Document, semaphore):
    
    # Define documents for classification  
    document_types = ['Boleto Bancario Seguradora']
    
    async with semaphore:
        messages = [  
            {
                "role": "system",
                "content": f"Para cada documento classifique o tipo de documento. Atenha-se a lista: {document_types}" 
            },
            {
                "role": "user",
                "content": 
                [{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{document.image_base64}"}}]
            }
        ]  
  
        for attempt in range(5):
            try:  
                response = client.beta.chat.completions.parse(  
                    model=genv("MODEL_NAME"),  
                    temperature=0,  
                    max_tokens=10000,  
                    response_format=Clone,  
                    messages=messages  
                )  
                response = response.choices[0].message.parsed

                return ResponseModel(
                    nome_arquivo=document.filename,
                    cedente=response.cedente,
                    sacado=response.sacado,
                    codigo_barras=document.barcode,
                    linha_digitavel=document.line,
                    apolice=response.apolice,
                    data_vencimento=response.data_vencimento,
                    valor=document.value
                ) 
  
            except Exception as e:
                if "429" in str(e):
                    wait_time = 2 ** attempt
                    await sleep(wait_time)  
                    continue
                else:  
                    raise HTTPException(status_code=500, detail=str(e))

# process with azure openai
async def process_documents_with_azure(documents: List[Document]):  
    client = AzureOpenAI(
        api_version=genv("API_VERSION")
        ,azure_endpoint=genv("AZURE_ENDPOINT"),
        api_key=genv("API_KEY")  # gpt-4o-mini
    ) 
  
    semaphore = Semaphore(5)  # Limitar a 5 requisições simultâneas  
    tasks = [process_single_document_with_azure(client, document, semaphore) for document in documents]  
      
    all_responses = await gather(*tasks)  
      
    return all_responses





# 