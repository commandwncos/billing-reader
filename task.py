
from openai import AzureOpenAI
from models.all import DocumentGeral




from os import getenv
from dotenv import load_dotenv as ld

# Carrega as variáveis de ambiente do arquivo .env  
ld()

def background_task(messages: list):
    client = AzureOpenAI(
        api_version=getenv("API_VERSION")
        ,azure_endpoint=getenv("AZURE_ENDPOINT"),
        api_key=getenv("API_KEY")  # gpt-4o-mini
        )

    response = client.beta.chat.completions.parse(
                model=getenv("MODEL_NAME"),
                temperature=0,
                max_tokens=5000,
                response_format=DocumentGeral,
                messages=messages
    )
    documents = response.choices[0].message.parsed
    return documents