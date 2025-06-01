from pydantic import BaseModel, Field
from typing import List


class Output(BaseModel):
    type: str
    task_id: str
    cedente: str = Field(description='Empresa emissora do boleto')
    sacado: str = Field(description='Empresa/Cliente pagador do boleto')
    linha_digitavel: str
    codigo_barras: str
    data_vencimento: str = Field(description='ano-mes-dia')
    apolice: str = Field(description='Número da apólice de seguro associada ao boleto: Apólice, Endosso, Numero do Documento, Documento, Referencia de emissão apólice ou Identificação da Parcela.')
    valor: float = Field(description='Valor do boleto')

# General: define document type
class DocumentGeral(BaseModel):  
    documents: List[Output]

