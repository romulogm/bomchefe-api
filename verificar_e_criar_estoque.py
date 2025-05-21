import requests
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_TOKEN = "AhuAk87&%&Ajha%ahga$2851S6hdma"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "x-token": API_TOKEN,
}

def get_produtos():
    try:
        response = requests.get(f"{API_BASE_URL}/produtos/", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {str(e)}")
        return []

def estoque_existe(produto_id):
    try:
        response = requests.get(f"{API_BASE_URL}/estoques/produto/{produto_id}", headers=headers)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return False
        print(f"⚠️ Erro HTTP ao verificar estoque de produto {produto_id}: {http_err}")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar estoque de produto {produto_id}: {str(e)}")
        return True

def criar_estoque(produto_id):
    hoje = datetime.now()
    payload = {
        "produto_id": produto_id,
        "quantidade": 100,
        "lote": "Lote-001",
        "data_producao": hoje.strftime("%Y-%m-%d"),
        "data_validade": hoje.strftime("%Y-%m-%d"),
        "localizacao": "Sede",
        "data_atualizacao": hoje.isoformat()
    }

    try:
        response = requests.post(f"{API_BASE_URL}/estoques/", json=payload, headers=headers)
        if response.status_code == 201:
            print(f"✅ Estoque criado para produto_id={produto_id}")
        else:
            print(f"❌ Erro ao criar estoque para produto_id={produto_id}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Exceção ao criar estoque para produto_id={produto_id}: {str(e)}")

def main():
    produtos = get_produtos()
    if not produtos:
        print("⚠️ Nenhum produto retornado.")
        return

    for produto in produtos:
        produto_id = produto.get("produto_id")
        if not produto_id:
            print(f"⚠️ Produto sem 'produto_id': {produto}")
            continue

        if not estoque_existe(produto_id):
            criar_estoque(produto_id)
        else:
            print(f"ℹ️ Estoque já existe para produto_id={produto_id}")

if __name__ == "__main__":
    main()
