from fastapi import FastAPI, Depends, HTTPException, Request
from db import get_db_connection
from openai_client import generate_sql
import traceback
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai_client import generate_user_response

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

def is_safe_query(query: str) -> bool:
    """Ensures the SQL query is only a SELECT statement."""
    query = query.strip().upper()
    return query.startswith("SELECT") or query.startswith("WITH")

@app.get("/", response_class=HTMLResponse)
async def render_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.post("/query/")
def run_query(natural_query: str, db=Depends(get_db_connection)):
    cursor = db.cursor()

    try:
        sql_query = generate_sql(natural_query).strip()
        
        print(f"Generated SQL Query: {sql_query}")
        logger.info(f"Generated SQL Query: {sql_query}")

        if not is_safe_query(sql_query):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

        cursor.execute(sql_query)
        columns = [column[0] for column in cursor.description] if cursor.description else []
        result = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []

        human_response = generate_user_response(result if result else "No rows returned.")
        return {
            "query": sql_query,
            "result": result if result else "No rows returned.",
            "human_response": human_response if human_response else "No summary available."
}

    except Exception as e:
    
        error_message = traceback.format_exc()
        logger.error(f"Query Execution Error: {error_message}")
    
        return {"error": "Internal Server Error", "details": error_message}


    finally:
        cursor.close()
        db.close()

