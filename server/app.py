import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
    <head>
        <title>SQL Query Optimizer - OpenEnv</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #0f0f0f; color: #fff; }
            h1 { color: #00d4ff; }
            h2 { color: #00ff88; }
            .endpoint { background: #1a1a2e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #00d4ff; }
            .method { background: #00d4ff; color: #000; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .method-get { background: #00ff88; }
            .task { background: #1a1a2e; padding: 10px; margin: 8px 0; border-radius: 6px; }
            .easy { border-left: 4px solid #00ff88; }
            .medium { border-left: 4px solid #ffaa00; }
            .hard { border-left: 4px solid #ff4444; }
            code { background: #333; padding: 2px 6px; border-radius: 3px; }
            .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-left: 8px; }
            .badge-easy { background: #00ff8833; color: #00ff88; }
            .badge-medium { background: #ffaa0033; color: #ffaa00; }
            .badge-hard { background: #ff444433; color: #ff4444; }
            a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <h1>🗄️ SQL Query Optimizer — OpenEnv</h1>
        <p>A real-world OpenEnv RL environment where AI agents learn to fix and optimize SQL queries through <strong>actual SQLite execution</strong>.</p>

        <h2>🎯 Tasks</h2>
        <div class="task easy">
            <strong>task_easy</strong> <span class="badge badge-easy">EASY</span>
            <p>Fix a broken JOIN query that returns wrong results.</p>
        </div>
        <div class="task medium">
            <strong>task_medium</strong> <span class="badge badge-medium">MEDIUM</span>
            <p>Eliminate N+1 correlated subquery using JOIN + GROUP BY.</p>
        </div>
        <div class="task medium">
            <strong>task_medium_2</strong> <span class="badge badge-medium">MEDIUM</span>
            <p>Find top rated products per category using AVG + GROUP BY.</p>
        </div>
        <div class="task hard">
            <strong>task_hard</strong> <span class="badge badge-hard">HARD</span>
            <p>Write monthly revenue report using CTEs.</p>
        </div>
        <div class="task hard">
            <strong>task_hard_2</strong> <span class="badge badge-hard">HARD</span>
            <p>Customer lifetime value ranking using Window Functions.</p>
        </div>

        <h2>🔌 API Endpoints</h2>
        <div class="endpoint">
            <span class="method">POST</span> <code>/reset</code> — Start new episode. Body: {"task_id": "task_easy"}
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <code>/step</code> — Submit SQL query. Body: {"query": "SELECT ..."}
        </div>
        <div class="endpoint">
            <span class="method method-get">GET</span> <code>/state</code> — Get current episode state.
        </div>
        <div class="endpoint">
            <span class="method method-get">GET</span> <code>/tasks</code> — List all 5 tasks.
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <code>/grader</code> — Grade a query. Body: {"task_id": "...", "query": "..."}
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <code>/baseline</code> — Run baseline on all tasks.
        </div>

        <h2>📚 Docs</h2>
        <p><a href="/docs">Interactive API Docs (Swagger UI)</a> | <a href="/redoc">ReDoc</a></p>

        <h2>🗄️ Database Schema</h2>
        <p>E-commerce dataset with 5 tables:</p>
        <code>customers | products | orders | order_items | reviews</code>
    </body>
    </html>
    """


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
            "db_schema": "string",
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
        "task_medium_2": (
            "SELECT p.category, p.name, AVG(r.rating) AS avg_rating "
            "FROM products p "
            "JOIN reviews r ON p.id = r.product_id "
            "GROUP BY p.category, p.name "
            "ORDER BY avg_rating DESC;"
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
        "task_hard_2": (
            "SELECT c.name, c.country, "
            "SUM(oi.quantity * oi.unit_price) AS total_spent, "
            "COUNT(DISTINCT o.id) AS order_count, "
            "ROW_NUMBER() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rank "
            "FROM customers c "
            "JOIN orders o ON c.id = o.customer_id "
            "JOIN order_items oi ON o.id = oi.order_id "
            "WHERE o.status = 'completed' "
            "GROUP BY c.id, c.name, c.country "
            "ORDER BY total_spent DESC;"
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


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
