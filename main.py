import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from database import inicializar_banco, DB_URL
from dao import LivroDAO, AutorDAO  

inicializar_banco()

app = FastAPI(title="BookStore API")

# Libera o acesso do Front-End (HTML/JS) à API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

livro_dao = LivroDAO(DB_URL)
autor_dao = AutorDAO(DB_URL)

class AutorSchema(BaseModel): 
    nome_autor: str
    nacionalidade: str
    data_nascimento: str  

class LivroSchema(BaseModel):
    titulo: str
    ano_publicacao: int
    genero: str
    autor_id: int

@app.post("/autores", status_code=201)
def adicionar_autor(autor: AutorSchema):
    novo_id = autor_dao.inserir_autor(
        nome_autor=autor.nome_autor,
        nacionalidade=autor.nacionalidade,
        data_nascimento=autor.data_nascimento
    )
    return {
        "id": novo_id,
        "mensagem": "Autor adicionado com sucesso a base de dados!"
    }

@app.get("/autores")
def listar_autores():
    resultados = autor_dao.listar_todos()
    lista_formatada = []
    for autor in resultados:
        lista_formatada.append({
            "id": autor[0],
            "nome_autor": autor[1],
            "nacionalidade": autor[2],
            "data_nascimento": autor[3]
        })
    return lista_formatada

@app.get("/autores/{autor_id}")
def buscar_autor(autor_id: int):
    autor = autor_dao.buscar_por_id(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return {
        "id": autor[0],
        "nome_autor": autor[1],
        "nacionalidade": autor[2],
        "data_nascimento": autor[3]
    }  

@app.put("/autores/{autor_id}")
def atualizar_autor(autor_id: int, autor_atualizado: AutorSchema):
    if not autor_dao.buscar_por_id(autor_id):
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    autor_dao.atualizar_autor(
        autor_id=autor_id,
        nome_autor=autor_atualizado.nome_autor,
        nacionalidade=autor_atualizado.nacionalidade,
        data_nascimento=autor_atualizado.data_nascimento
    )
    return {
        "mensagem": f"Autor {autor_id} atualizado com sucesso na base de dados"
    }
    
@app.delete("/autores/{autor_id}")
def deletar_autor(autor_id: int):
    if not autor_dao.buscar_por_id(autor_id):
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    autor_dao.deletar_autor(autor_id)
    return {
        "mensagem": f"Autor {autor_id} deletado com sucesso da base de dados"
    }

@app.post("/livros", status_code=201)
def adicionar_livro(livro: LivroSchema):
    if not autor_dao.buscar_por_id(livro.autor_id):
        raise HTTPException(status_code=400, detail="Não é possível cadastrar um livro para um Autor que não existe.")

    novo_id = livro_dao.inserir_livro(
        titulo=livro.titulo,
        ano_publicacao=livro.ano_publicacao,
        genero=livro.genero,
        autor_id=livro.autor_id
    )
    return {
        "id": novo_id,
        "mensagem": "Livro adicionado com sucesso!"
    }  

@app.get("/livros")
def listar_livros(titulo: Optional[str] = None, genero: Optional[str] = None):
    resultados = livro_dao.listar_todos(titulo_filtro=titulo, genero_filtro=genero)
    lista_formatada = []
    for livro in resultados:
        lista_formatada.append({
            "id": livro[0],
            "titulo":  livro[1],
            "ano_publicacao": livro[2],
            "genero": livro[3],
            "autor_id": livro[4]
        })
    return lista_formatada

@app.get("/livros/{livro_id}")
def buscar_livro(livro_id: int):
    livro = livro_dao.buscar_por_id(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return {
        "id": livro[0],
        "titulo": livro[1],
        "ano_publicacao": livro[2],
        "genero": livro[3],
        "autor_id": livro[4]
    }

@app.put("/livros/{livro_id}")
def atualizar_livro(livro_id: int, livro_atualizado: LivroSchema):
    if not livro_dao.buscar_por_id(livro_id):
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    if not autor_dao.buscar_por_id(livro_atualizado.autor_id):
        raise HTTPException(status_code=400, detail="Autor informado não existe.")

    livro_dao.atualizar_livro(
        livro_id=livro_id,
        titulo=livro_atualizado.titulo,
        ano_publicacao=livro_atualizado.ano_publicacao,
        genero=livro_atualizado.genero,
        autor_id=livro_atualizado.autor_id
    )
    return {
        "mensagem": f"Livro {livro_id} atualizado com sucesso"
    }

@app.delete("/livros/{livro_id}")
def deletar_livro(livro_id: int):
    if not livro_dao.buscar_por_id(livro_id):
        raise HTTPException(status_code=404, detail="Livro não encontrado")
        
    livro_dao.deletar_livro(livro_id)
    return {
        "mensagem": f"Livro {livro_id} deletado com sucesso"
    }

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=porta)
