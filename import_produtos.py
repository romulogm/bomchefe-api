import requests

# URL da API e token
URL = "http://localhost:8000/produtos/"
TOKEN = "AhuAk87&%&Ajha%ahga$2851S6hdma"

# Lista de produtos (adicione os seus objetos aqui)
produtos = [
          {
      "nome": "Oito",
      "descricao": "Produto com custo de R$25,00 por KG. Produção semanal: 6 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Rosquinha da Mamãe",
      "descricao": "Produto com custo de R$25,00 por KG. Produção semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Aveinha",
      "descricao": "Produto com custo de R$25,00 por KG. Produção semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Queijadinha",
      "descricao": "Produto com custo de R$25,00 por KG. Produção semanal: 3 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Palito de Limão",
      "descricao": "Produto com custo de R$23,00 por KG. Venda semanal: 4 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Rosca de Coco",
      "descricao": "Produto com custo de R$25,00 por KG. Venda semanal: 3 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Casadinho Goiabinha",
      "descricao": "Produto com custo de R$30,00 por KG. Venda semanal: 3 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 60.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Gravatinha Goiabinha",
      "descricao": "Produto com custo de R$30,00 por KG. Venda semanal: 5 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Beijinho de Freira",
      "descricao": "Produto com custo de R$28,00 por KG. Venda semanal: 4 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Trancinha de Laranja",
      "descricao": "Produto com custo de R$23,00 por KG. Venda semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Medalhão Tradicional",
      "descricao": "Produto com custo de R$40,00 por KG. Venda semanal: 8 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 84.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Argolinha de Parmesão",
      "descricao": "Produto com custo de R$36,00 por KG. Venda semanal: 6 a 8 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 84.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Argolinha de Chia",
      "descricao": "Produto com custo de R$36,00 por KG. Venda semanal: 6 a 8 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 84.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Palitinho de Pimenta",
      "descricao": "Produto com custo de R$36,00 por KG. Venda semanal: 1,5 a 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 84.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Vaidosa",
      "descricao": "Produto com custo de R$42,00 por KG. Venda semanal: 4 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 78.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Biscoito de Amendoim",
      "descricao": "Produto com custo de R$42,00 por KG. Venda semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 78.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Biscoito de Milho",
      "descricao": "Produto com custo de R$42,00 por KG. Venda semanal: 1 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 78.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Torradinha de Alho",
      "descricao": "Produto com custo de R$42,00 por KG. Venda semanal: 1,5 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 78.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Champanhota de Canela",
      "descricao": "Produto com custo de R$42,00 por KG. Venda semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 78.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Quebra Quebra de Coco",
      "descricao": "Produto com custo de R$29,00 por KG. Venda semanal: 2 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Rosquinha de Leite Condensado",
      "descricao": "Produto com custo de R$24,00 por KG. Venda semanal: 4 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Biscoito de Natinha",
      "descricao": "Produto com custo de R$24,00 por KG. Venda semanal: 1,5 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Biscoito de Natinha c/ Granulado de Chocolate",
      "descricao": "Produto com custo de R$24,00 por KG. Venda semanal: 1 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 56.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    },
    {
      "nome": "Pimentinha Mexicana",
      "descricao": "Produto com custo de R$13,00 por KG. Venda semanal: 3 KG.",
      "categoria": "Biscoito",
      "preco_unitario": 46.00,
      "peso_gramas": 1000,
      "data_criacao": "2025-05-18",
      "status": true
    }
    {
        "nome": "Biscoito de Natinha c/ Granulado de Chocolate",
        "descricao": "Produto com custo de R$24,00 por KG. Venda semanal: 1 KG.",
        "categoria": "Biscoito",
        "preco_unitario": 56.00,
        "peso_gramas": 1000,
        "data_criacao": "2025-05-18",
        "status": True
    },
    {
        "nome": "Rosquinha de leite Condensado",
        "descricao": "Produto com custo de R$24,00 por KG. Venda semanal: 4 KG.",
        "categoria": "Biscoito",
        "preco_unitario": 56.00,
        "peso_gramas": 1000,
        "data_criacao": "2025-05-18",
        "status": True
    }
]

# Cabeçalhos da requisição
headers = {
    "accept": "application/json",
    "x-token": TOKEN,
    "Content-Type": "application/json"
}

# Enviando os produtos
for produto in produtos:
    response = requests.post(URL, json=produto, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Produto '{produto['nome']}' enviado com sucesso.")
    else:
        print(f"❌ Erro ao enviar '{produto['nome']}': {response.status_code}")
        print(response.text)
