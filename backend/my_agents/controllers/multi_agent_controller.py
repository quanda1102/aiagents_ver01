from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from my_agents.agents.query_understanding_agent import QueryUnderstandingAgent
from my_agents.agents.schema_explorer_agent import SchemaExplorerAgent
from my_agents.agents.sql_generator_agent import SqlGeneratorAgent
from my_agents.agents.execution_validator_agent import ExecutionValidatorAgent
from my_agents.agents.router_agent import RouterAgent

router = APIRouter()

query_agent = QueryUnderstandingAgent()
schema_agent = SchemaExplorerAgent()
sql_agent = SqlGeneratorAgent()
validator_agent = ExecutionValidatorAgent()
router_agent = RouterAgent()

class QuestionRequest(BaseModel):
    question: str

class GenerateSQLRequest(BaseModel):
    intent: str
    entities: Dict[str, Any]
    schema_context: Optional[Dict[str, Any]] = None
    probes: Optional[List[Any]] = None

class ValidateSQLRequest(BaseModel):
    sql: str

class TextToSQLRequest(BaseModel):
    question: str
    sessionId: Optional[str] = None

@router.post("/analyze-query")
async def analyze_query(body: QuestionRequest):
    if not body.question:
        raise HTTPException(status_code=400, detail="Missing question")

    result = await query_agent.process(body.question, {})
    return { "success": True, "data": result }

@router.post("/explore-schema")
async def explore_schema(body: QuestionRequest):
    try:
        question = body.question or "Khám phá toàn bộ schema"
        result = await schema_agent.process(question, {})
        return { "success": True, "data": result }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-sql")
async def generate_sql(body: GenerateSQLRequest):
    if not body.intent or not body.entities:
        raise HTTPException(status_code=400, detail="Thiếu intent hoặc entities")

    result = await sql_agent.process(body.dict(), {})
    return { "success": True, "data": result }

@router.post("/validate-sql")
async def validate_sql(body: ValidateSQLRequest):
    if not body.sql:
        raise HTTPException(status_code=400, detail="Thiếu trường sql trong request body")

    try:
        result = await validator_agent.process({ "sql": body.sql }, {})
        return { "success": True, "data": result }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-sql-workflow")
async def text_to_sql_workflow(body: TextToSQLRequest):
    if not body.question:
        raise HTTPException(status_code=400, detail="Missing question")

    result = await router_agent.process({ "question": body.question, "sessionId": body.sessionId }, {})
    return {
        "success": True,
        "response": result.get("formattedResponse")
    }
