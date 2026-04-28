import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

#model embedding chuyen text sang vector
embedding_model = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

def embed_query(query: str):
    return embedding_model(f"query:{query}")