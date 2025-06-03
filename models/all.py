from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4

class Document(BaseModel):  
    filename: str  
    barcode: str  
    line: str  
    value: float  
    # image_base64: str  
  
class Clone(BaseModel):  
    cedente: str = Field(description='Empresa emissora do boleto')  
    sacado: str = Field(description='Empresa/Cliente pagador do boleto')  
    data_vencimento: str = Field(description='ano-mes-dia')  
    apolice: str = Field(description='Número da apólice de seguro associada ao boleto') 

class ResponseModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    nome_arquivo: str  
    cedente: str  
    sacado: str  
    codigo_barras: str  
    linha_digitavel: str  
    apolice: str  
    data_vencimento: str  
    valor: float

    @field_validator('cedente', 'sacado')  
    def formatar_primeiras_letras(cls, params):  
        return params.title()