import requests

API_URL = "http://localhost:8000/clientes/"
API_TOKEN = "AhuAk87&%&Ajha%ahga$2851S6hdma"

clientes = [
    {
        "tipo_pessoa": "jurídica",
        "documento": "00000000000101",
        "nome": "Feira Gutierrez (Terça Feira)",
        "email": "feira1@example.com",
        "endereco": "Rua Marechal Hermes c/ André Cavalcanti - Bairro Gutierrez"
    },
    {
        "tipo_pessoa": "jurídica",
        "documento": "00000000000102",
        "nome": "Feira Domingos Vieira (Quarta Feira)",
        "email": "feira2@example.com",
        "endereco": "Rua Domingos Vieira c/ Grão Pará - Bairro Funcionários"
    },
    {
        "tipo_pessoa": "jurídica",
        "documento": "00000000000103",
        "nome": "Feira Carandaí (Quinta Feira)",
        "email": "feira3@example.com",
        "endereco": "Rua Carandaí c/ Rua Ceará - Bairro Funcionários"
    },
    {
        "tipo_pessoa": "jurídica",
        "documento": "00000000000104",
        "nome": "Feira Bernardo Guimarães (Sexta Feira)",
        "email": "feira4@example.com",
        "endereco": "Rua Bernardo Guimarães c/ Rua Piauí - Bairro Funcionários"
    },
    {
        "tipo_pessoa": "jurídica",
        "documento": "00000000000105",
        "nome": "Feira Santo Antônio (Sábado)",
        "email": "feira5@example.com",
        "endereco": "Rua São Domingos do Prata Esquina c/ Leopoldina Bairro Santo Antônio"
    }
]

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "x-token": API_TOKEN,
}

for cliente in clientes:
    try:
        response = requests.post(API_URL, json=cliente, headers=headers)
        if response.status_code == 200:
            print(f"✅ Cliente '{cliente['nome']}' criado com sucesso.")
        else:
            print(f"❌ Erro ao criar cliente '{cliente['nome']}': {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Erro de exceção ao criar cliente '{cliente['nome']}': {str(e)}")
