from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clientes, produtos
from fastapi.responses import HTMLResponse
from jinja2 import Template
app = FastAPI()

# Criar as tabelas no banco
Base.metadata.create_all(bind=engine)

app.include_router(clientes.router)
app.include_router(produtos.router)

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

