"""initial

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    op.create_table('cvs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('candidate_name', sa.String(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('description_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('cv_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cv_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column('content_tsv', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cv_id'], ['cvs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('cv_chunks_tsv_idx', 'cv_chunks', ['content_tsv'], unique=False, postgresql_using='gin')

    op.create_table('job_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column('content_tsv', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('job_chunks_tsv_idx', 'job_chunks', ['content_tsv'], unique=False, postgresql_using='gin')

    op.execute("""
    CREATE OR REPLACE FUNCTION update_content_tsv() RETURNS trigger AS $$
    BEGIN
      NEW.content_tsv := to_tsvector('simple', NEW.content);
      RETURN NEW;
    END
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trg_cv_chunks_tsv BEFORE INSERT OR UPDATE ON cv_chunks
    FOR EACH ROW EXECUTE PROCEDURE update_content_tsv();
    """)
    
    op.execute("""
    CREATE TRIGGER trg_job_chunks_tsv BEFORE INSERT OR UPDATE ON job_chunks
    FOR EACH ROW EXECUTE PROCEDURE update_content_tsv();
    """)

def downgrade() -> None:
    op.drop_table('job_chunks')
    op.drop_table('jobs')
    op.drop_table('cv_chunks')
    op.drop_table('cvs')
    op.execute("DROP FUNCTION IF EXISTS update_content_tsv() CASCADE")
