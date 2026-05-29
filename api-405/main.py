from fastapi import FastAPI
from pydantic import BaseModel, Field
import asyncpg

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

async def get_db_connection():
    return await asyncpg.connect(
        user="postgres",
        password="sql",
        database="405",
        host="localhost"
    )

@app.get("/test")
async def test_connection():
    conn = await get_db_connection()
    await conn.close()
    return {"message": "Conexão com o PostgreSQL bem-sucedida!"}

class Produto(BaseModel):
    nome: str
    categoria: str
    preco: float
    estoque: int

@app.post("/produtos")
async def create_product(produto: Produto):
    conn = await get_db_connection()
    await conn.execute(
            "INSERT INTO produtos (nome, categoria, preco, estoque) VALUES ($1, $2, $3, $4)",
            produto.nome, produto.categoria, produto.preco, produto.estoque
        )
    await conn.close()
    return {"message": "Produto criado com sucesso!"}

@app.get("/produtos")
async def get_products():
    conn = await get_db_connection()
    rows = await conn.fetch("SELECT * FROM produtos")
    await conn.close()
    produtos = []
    for row in rows:
        produtos.append(f"ID do produto: {row['id']}, Nome: {row['nome']}, Categoria: {row['categoria']}, Preço: {row['preco']}, Estoque: {row['estoque']}")
    return {"produtos": produtos}

@app.get("/produtos/{produto_id}")
async def get_product(produto_id: int):
    conn = await get_db_connection()
    produto = await conn.fetchrow("SELECT * FROM produtos WHERE id = $1", produto_id)
    await conn.close()
    return {"produto": f"ID do produto: {produto['id']}, Nome: {produto['nome']}, Categoria: {produto['categoria']}, Preço: {produto['preco']}, Estoque: {produto['estoque']}"}

@app.put("/produtos/{produto_id}")
async def update_product(produto_id: int, produto: Produto):
    conn = await get_db_connection()
    result = await conn.execute(
        """
        UPDATE produtos
        SET nome = $1, categoria = $2, preco = $3, estoque = $4
        WHERE id = $5
        """,
        produto.nome, produto.categoria, produto.preco, produto.estoque, produto_id
    )
    await conn.close()
    if result == "UPDATE 1":
        return {"message": "Produto atualizado com sucesso!"}
    else:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    
@app.delete("/produtos/{produto_id}")
async def delete_product(produto_id: int):
    conn = await get_db_connection()
    await conn.execute("DELETE FROM pedidos WHERE produto_id = $1", produto_id)
    result = await conn.execute("DELETE FROM produtos WHERE id = $1", produto_id)
    await conn.close()
    if result == "DELETE 1":
        return {"message": f"Produto {produto_id} deletado com sucesso!"}
    else:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")