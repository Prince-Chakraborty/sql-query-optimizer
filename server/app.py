import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from models import SQLAction, SQLObservation, EpisodeState
from server.environment import SQLOptimizerEnvironment
from tasks import list_tasks
from graders import grade

app = FastAPI(
    title="SQL Query Optimizer Environment",
    description="OpenEnv environment where AI agents learn to fix and optimize SQL queries.",
    version="1.0.0",
)

env = SQLOptimizerEnvironment()


class ResetRequest(BaseModel):
    task_id: Optional[str] = "task_easy"


class StepRequest(BaseModel):
    query: str
    explanation: Optional[str] = ""


class GraderRequest(BaseModel):
    task_id: str
    query: str


@app.get("/")
def root():
    return {
        "name": "SQL Query Optimizer Environment",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/grader", "/baseline"]
    }


@app.post("/reset")
def reset(request: ResetRequest = ResetRequest()):
    try:
        obs = env.reset(task_id=request.task_id or "task_easy")
        return {
            "observation": obs.model_dump(),
            "episode_id": env.episode_id,
            "task_id": env.task_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(request: StepRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    try:
        action = SQLAction(
            query=request.query,
            explanation=request.explanation or ""
        )
        result = env.step(action)
        return {
            "observation": result["observation"].model_dump(),
            "reward": result["reward"],
            "done": result["done"],
            "info": result["info"],
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    return env.state().model_dump()


@app.get("/tasks")
def tasks():
    return {
        "tasks": list_tasks(),
        "action_schema": {
            "query": "string - the SQL query to submit",
            "explanation": "string optional - explanation of changes made"
        },
        "observation_schema": {
            "task_description": "string",
            "original_query": "string",
            "schema": "string",
            "error_message": "string or null",
            "last_query": "string or null",
            "execution_time_ms": "float or null",
            "rows_returned": "int or null",
            "step_number": "int",
            "max_steps": "int",
            "hint": "string or null"
        }
    }


@app.post("/grader")
def grader(request: GraderRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    try:
        result = grade(request.task_id, request.query)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/baseline")
def baseline():
    baseline_queries = {
        "task_easy": (
            "SELECT DISTINCT c.name, c.email "
            "FROM customers c "
            "JOIN orders o ON c.id = o.customer_id "
            "WHERE c.country = 'India';"
        ),
        "task_medium": (
            "SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_spent "
            "FROM customers c "
            "JOIN orders o ON c.id = o.customer_id "
            "JOIN order_items oi ON o.id = oi.order_id "
            "GROUP BY c.id, c.name;"
        ),
        "task_hard": (
            "WITH monthly AS ("
            "  SELECT strftime('%Y-%m', o.created_at) AS month, "
            "         COUNT(DISTINCT o.id) AS total_orders, "
            "         SUM(oi.quantity * oi.unit_price) AS total_revenue "
            "  FROM orders o "
            "  JOIN order_items oi ON o.id = oi.order_id "
            "  WHERE o.status = 'completed' "
            "  GROUP BY month "
            ") "
            "SELECT month, total_orders, total_revenue "
            "FROM monthly "
            "ORDER BY month ASC;"
        ),
    }

    results = {}
    for task_id, query in baseline_queries.items():
        result = grade(task_id, query)
        results[task_id] = {
            "score": result["score"],
            "reason": result["reason"],
            "query_used": query,
        }

    return {
        "baseline_scores": results,
        "average_score": round(
            sum(r["score"] for r in results.values()) / len(results), 3
        )
    }


@app.get("/health")
def health():
    return {"status": "ok"}
