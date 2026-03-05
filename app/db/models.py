import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class CV(Base):
    __tablename__ = "cvs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    candidate_name: Mapped[str] = mapped_column(String, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    chunks = relationship("CVChunk", back_populates="cv", cascade="all, delete-orphan")

class CVChunk(Base):
    __tablename__ = "cv_chunks"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    cv_id: Mapped[str] = mapped_column(String, ForeignKey("cvs.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(1536))
    content_tsv = mapped_column(TSVECTOR)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    cv = relationship("CV", back_populates="chunks")

    __table_args__ = (
        Index('cv_chunks_tsv_idx', 'content_tsv', postgresql_using='gin'),
        Index('cv_chunks_embedding_idx', 'embedding', postgresql_using='ivfflat', postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String, nullable=True)
    description_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    chunks = relationship("JobChunk", back_populates="job", cascade="all, delete-orphan")

class JobChunk(Base):
    __tablename__ = "job_chunks"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(String, ForeignKey("jobs.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(1536))
    content_tsv = mapped_column(TSVECTOR)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    job = relationship("Job", back_populates="chunks")

    __table_args__ = (
        Index('job_chunks_tsv_idx', 'content_tsv', postgresql_using='gin'),
        Index('job_chunks_embedding_idx', 'embedding', postgresql_using='ivfflat', postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )
