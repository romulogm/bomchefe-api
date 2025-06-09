from fastapi import FastAPI, Depends
from app.database import engine, Base
from app.routers import clientes, produtos, estoque, vendas, feiras
from fastapi.responses import HTMLResponse
from jinja2 import Template
from app.utils.auth import verify_token
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
            root_path="/api"
            )


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"],   
)

# Criar as tabelas no banco
Base.metadata.create_all(bind=engine)

# Inclui os routers para as entidades
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])
app.include_router(estoque.router, prefix="/estoques", tags=["Estoques"])
app.include_router(vendas.router, prefix="/vendas", tags=["Vendas"])
app.include_router(feiras.router, prefix="/feiras", tags=["Feiras"])

# Template HTML para a página inicial
TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biscoitos Bom Chefe</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f8f8;
            padding: 50px;
        }
        h1 {
            color: #d2691e;
        }
        p {
            color: #444;
            font-size: 18px;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bem-vindo à Biscoitos Bom Chefe 🍪</h1>
        <p>Os melhores biscoitos caseiros feitos com amor e tradição!</p>
        <p>Entre em contato para saber mais sobre nossos produtos.</p>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return Template(TEMPLATE_HTML).render()

