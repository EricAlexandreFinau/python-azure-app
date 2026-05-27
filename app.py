from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

produtos_db = {}

class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    em_estoque: bool


# salvando no dicionario
@app.post("/produtos", status_code=201)
def criar_produto(produto: ProdutoSchema):
    novo_id = max(produtos_db.keys()) + 1 if produtos_db else 1

    produtos_db[novo_id] = produto.model_dump()

    return {
        "id": novo_id,
        "mensagem": "Produto criado com sucesso"
    }
#Atualizar
@app.put("/produtos/{produto_id}")
def atualizar_total_produto(produto_id: int, produto_atualizado: ProdutoSchema):
    if produto_id not in produtos_db:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produtos_db[produto_id] = produto_atualizado.model_dump()

    return {
        "mensagem": f"Produto {produto_id} totalmente atualizado",
        "dados": produtos_db[produto_id]
    }

class ProdutoPatchSchema(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    em_estoque: Optional[bool] = None

#Atualizar parcialmente
@app.patch("/produtos/{produto_id}")
def atualizar_parcial_produto(produto_id: int, dados_parciais: ProdutoPatchSchema):
    if produto_id not in produtos_db:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produto_atual = produtos_db[produto_id]

    dados_para_atualizar = dados_parciais.model_dump(exclude_unset=True)

    produto_atual.update(dados_para_atualizar)

    return {
        "mensagem": f"Produto {produto_id} modificado parcialmente",
        "dados": produto_atual
    }
                              

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    if produto_id not in produtos_db:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    del produtos_db[produto_id]

    return {
        "mensagem": f"Produto {produto_id} deletado com sucesso"
    }
