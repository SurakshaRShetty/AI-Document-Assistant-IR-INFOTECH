from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float
from app.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    page_number = Column(Integer)
    text = Column(Text)
    embedding = Column(ARRAY(Float))  # deprecated: vectors now live in ChromaDB

