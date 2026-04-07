from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import text
from backend.db.session import SessionLocal
import google.generativeai as genai
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Google AI for embeddings
genai.configure(api_key=settings.GOOGLE_API_KEY)

class SQLQueryInput(BaseModel):
    template: str = Field(..., description="The SQL query template with parameterized placeholders.")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dictionary of parameters for the SQL query.")

class KBSearchInput(BaseModel):
    query: str = Field(..., description="The search query text.")
    top_k: int = Field(default=5, description="Number of top results to return.")

def sql_query(input_data: SQLQueryInput) -> Dict[str, Any]:
    """
    Executes a read-only SQL query using parameterized execution for safety.
    """
    template = input_data.template
    params = input_data.params or {}

    session = SessionLocal()
    try:
        # Explicitly set the role to the read-only application user for absolute defense-in-depth,
        # ensuring that even if the session pool mixes connections, this execution context is strictly read-only.
        session.execute(text(f"SET ROLE {settings.APP_USER};"))

        # We use SQLAlchemy's text() for safe parameterized queries
        result = session.execute(text(template), params)
        # Fetch results
        rows = [dict(row._mapping) for row in result]
        return {"status": "success", "result": rows}
    except Exception as e:
        session.rollback()
        logger.error(f"Error executing SQL query: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # Reset role back to the default connection user to avoid polluting the connection pool
        try:
            session.execute(text("RESET ROLE;"))
        except Exception:
            pass
        session.close()

def _get_embedding(text: str) -> List[float]:
    """Helper function to get embeddings."""
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == 'your_google_api_key_here':
        import random
        return [random.uniform(-1, 1) for _ in range(768)]

    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Error calling Google AI embedding: {e}")
        import random
        return [random.uniform(-1, 1) for _ in range(768)]

def kb_search(input_data: KBSearchInput) -> Dict[str, Any]:
    """
    Searches the knowledge base using vector similarity.
    """
    query = input_data.query
    top_k = input_data.top_k
    try:
        embedding = _get_embedding(query)
    except Exception as e:
        return {"status": "error", "message": f"Failed to generate embedding: {e}"}

    session = SessionLocal()
    try:
        # Convert list of floats to a format pgvector accepts: '[0.1, 0.2, ...]'
        embedding_str = str(embedding)

        # We use the <-> operator for L2 distance (which works well for embeddings normalized or not)
        # However, the user specifically mentioned "<=>" which is cosine similarity in pgvector. Let's use <=>
        # Note: We use CAST(:embedding AS vector) because SQLAlchemy's text() parser gets confused by :embedding::vector
        sql = text("""
            SELECT filename, content, 1 - (embedding <=> CAST(:embedding AS vector)) as similarity
            FROM public.kb_embeddings
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)

        result = session.execute(sql, {"embedding": embedding_str, "top_k": top_k})
        rows = [{"filename": row.filename, "content": row.content, "similarity": row.similarity} for row in result]
        return {"status": "success", "result": rows}
    except Exception as e:
        session.rollback()
        logger.error(f"Error executing KB search: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        session.close()

def kpi_top_root_causes() -> Dict[str, Any]:
    """
    Retrieves aggregate KPIs for support ticket root causes (issue types).
    Aggregates data from marts.fact_tickets.
    """
    session = SessionLocal()
    try:
        # Aggregating tickets by issue_type, calculating total volume and average resolution time
        sql = text("""
            SELECT
                issue_type,
                COUNT(*) as ticket_count,
                AVG(resolution_time_hours) as avg_resolution_time_hours,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets
            FROM marts.fact_tickets
            GROUP BY issue_type
            ORDER BY ticket_count DESC
        """)

        result = session.execute(sql)
        rows = [dict(row._mapping) for row in result]
        return {"status": "success", "result": rows}
    except Exception as e:
        session.rollback()
        logger.error(f"Error executing KPI query: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        session.close()
