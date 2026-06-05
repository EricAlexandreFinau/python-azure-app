import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# 1. CONFIGURAÇÃO DO BANCO DE DADOS (Azure)
# ==========================================
# O sistema procura a sua variável DB_URL lá do painel do Azure
DATABASE_URL = os.environ.get("DB_URL", "sqlite:///./banco_teste.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. MODELOS DAS TABELAS (Substitui o DAO)
# ==========================================
class AutorModel(Base):
    __tablename__ = "autores"
    id = Column(Integer, primary_key=True, index=True)
    nome_autor = Column(String)
    nacionalidade = Column(String)
    data_nascimento = Column(String)

class LivroModel(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    ano_publicacao = Column(Integer)
    genero = Column(String)
    autor_id = Column(Integer, ForeignKey("autores.id"))

# Cria as tabelas automaticamente no Azure se não existirem
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMAS (Validação)
# ==========================================
class AutorSchema(BaseModel): 
    nome_autor: str
    nacionalidade: str
    data_nascimento: str  

class LivroSchema(BaseModel):
    titulo: str
    ano_publicacao: int
    genero: str
    autor_id: int

# ==========================================
# 4. INICIALIZAÇÃO DA API
# ==========================================
app = FastAPI(title="BookStore API - Simplificada")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciador de conexão para não sobrecarregar o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. ROTAS DE AUTORES
# ==========================================
@app.post("/autores", status_code=201)
def adicionar_autor(autor: AutorSchema, db: Session = Depends(get_db)):
    novo_autor = AutorModel(**autor.model_dump())
    db.add(novo_autor)
    db.commit()
    db.refresh(novo_autor)
    return {"id": novo_autor.id, "mensagem": "Autor adicionado com sucesso a base de dados!"}

@app.get("/autores")
def listar_autores(db: Session = Depends(get_db)):
    autores = db.query(AutorModel).all()
    return [{"id": a.id, "nome_autor": a.nome_autor, "nacionalidade": a.nacionalidade, "data_nascimento": a.data_nascimento} for a in autores]

@app.get("/autores/{autor_id}")
def buscar_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(AutorModel).filter(AutorModel.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return {"id": autor.id, "nome_autor": autor.nome_autor, "nacionalidade": autor.nacionalidade, "data_nascimento": autor.data_nascimento}  

@app.put("/autores/{autor_id}")
def atualizar_autor(autor_id: int, autor_atualizado: AutorSchema, db: Session = Depends(get_db)):
    autor = db.query(AutorModel).filter(AutorModel.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    for key, value in autor_atualizado.model_dump().items():
        setattr(autor, key, value)
        
    db.commit()
    return {"mensagem": f"Autor {autor_id} atualizado com sucesso na base de dados"}
    
@app.delete("/autores/{autor_id}")
def deletar_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(AutorModel).filter(AutorModel.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    db.delete(autor)
    db.commit()
    return {"mensagem": f"Autor {autor_id} deletado com sucesso da base de dados"}

# ==========================================
# 6. ROTAS DE LIVROS
# ==========================================
@app.post("/livros", status_code=201)
def adicionar_livro(livro: LivroSchema, db: Session = Depends(get_db)):
    autor_existe = db.query(AutorModel).filter(AutorModel.id == livro.autor_id).first()
    if not autor_existe:
        raise HTTPException(status_code=400, detail="Não é possível cadastrar um livro para um Autor que não existe.")

    novo_livro = LivroModel(**livro.model_dump())
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return {"id": novo_livro.id, "mensagem": "Livro adicionado com sucesso!"}  

@app.get("/livros")
def listar_livros(titulo: Optional[str] = None, genero: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(LivroModel)
    if titulo:
        query = query.filter(LivroModel.titulo.ilike(f"%{titulo}%"))
    if genero:
        query = query.filter(LivroModel.genero.ilike(f"%{genero}%"))
        
    livros = query.all()
    return [{"id": l.id, "titulo": l.titulo, "ano_publicacao": l.ano_publicacao, "genero": l.genero, "autor_id": l.autor_id} for l in livros]

@app.get("/livros/{livro_id}")
def buscar_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(LivroModel).filter(LivroModel.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return {"id": livro.id, "titulo": livro.titulo, "ano_publicacao": livro.ano_publicacao, "genero": livro.genero, "autor_id": livro.autor_id}

@app.put("/livros/{livro_id}")
def atualizar_livro(livro_id: int, livro_atualizado: LivroSchema, db: Session = Depends(get_db)):
    livro = db.query(LivroModel).filter(LivroModel.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    autor_existe = db.query(AutorModel).filter(AutorModel.id == livro_atualizado.autor_id).first()
    if not autor_existe:
        raise HTTPException(status_code=400, detail="Autor informado não existe.")

    for key, value in livro_atualizado.model_dump().items():
        setattr(livro, key, value)
        
    db.commit()
    return {"mensagem": f"Livro {livro_id} atualizado com sucesso"}

@app.delete("/livros/{livro_id}")
def deletar_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(LivroModel).filter(LivroModel.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
        
    db.delete(livro)
    db.commit()
    return {"mensagem": f"Livro {livro_id} deletado com sucesso"}

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=porta)
