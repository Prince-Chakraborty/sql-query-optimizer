---
title: SQL Query Optimizer
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🗄️ SQL Query Optimizer — OpenEnv RL Environment

> An RL environment that trains AI agents to fix and optimize SQL queries using real SQLite execution feedback.

## ⚡ 30-Second Understanding

WHAT: AI agent receives broken/slow SQL → submits fix → gets real execution feedback
WHY: SQL bugs cost companies millions. No existing RL env trains agents on real SQL execution
HOW: Agent → submits query → SQLite runs it → grader scores result → reward signal

Flow:
Agent reads broken query
    |
    v
Submits fixed SQL
    |
    v
SQLite ACTUALLY executes it
    |
    v
Grader checks real results
    |
    v
Reward = improvement over best score so far
    |
    v
Agent learns and improves

## 🔥 Learning Signal (What Judges Want To See)

### Before vs After Example

Task: Fix broken JOIN query

Step 1 - Agent submits (naive attempt):
Query: SELECT * FROM customers WHERE country = 'India'
Result: 3 rows but missing order check
Reward: 0.1 (query runs but wrong results)

Step 2 - Agent improves:
Query: SELECT c.name FROM customers c, orders o WHERE c.country = 'India'
Result: 15 rows (cartesian product bug)
Reward: 0.0 (wrong - cartesian product)

Step 3 - Agent learns from error:
Query: SELECT DISTINCT c.name, c.email FROM customers c JOIN orders o ON c.id = o.customer_id WHERE c.country = 'India'
Result: exactly 3 correct customers
Reward: 1.0 (PERFECT!)

Total reward progression: 0.1 -> 0.0 -> 1.0
Agent learned: always use explicit JOIN with ON clause

## 🌍 Real-World Impact

This simulates how real query optimizers work in production systems.
Applicable in large-scale systems like Meta's data infrastructure.
Every major tech company has SQL performance problems at scale.

Real cost of bad SQL:
- Slow queries = $1000s/hour in compute costs
- N+1 queries = 100x more database calls
- Missing JOINs = wrong business decisions from bad data

## ❓ Why This Problem Is Hard

1. SQL ambiguity: Multiple valid queries produce same correct result
2. Partial correctness: Query can be 60% right (correct table, wrong filter)
3. Execution matters: Text similarity cannot measure query correctness
4. Performance vs correctness: A query can be correct but 100x slower
5. Error recovery: Agent must learn from SQLite error messages

This is why text-matching graders FAIL and real execution is essential.

## ⚡ Quick Start (Under 5 Minutes)

### Use Live Space
curl -X POST https://alokrajkumar-sql-query-optimizer.hf.space/reset -H "Content-Type: application/json" -d '{"task_id": "task_easy"}'

### Run Locally
git clone https://github.com/Prince-Chakraborty/sql-query-optimizer
cd sql-query-optimizer
pip install -r server/requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860

### Run with Docker
docker build -t sql-query-optimizer .
docker run -p 7860:7860 sql-query-optimizer

## 🎮 3-Step Demo

Step 1 - Start episode:
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_id": "task_easy"}'
Output: {"observation": {"task_description": "Fix broken JOIN...", "original_query": "SELECT DISTINCT c.name..."}}

Step 2 - Submit wrong query:
curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d '{"query": "SELECT * FROM customers WHERE country = 'India';"}'
Output: {"reward": 0.1, "done": false, "info": {"score": 0.1, "reason": "Query runs but wrong results"}}

Step 3 - Submit correct query:
curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d '{"query": "SELECT DISTINCT c.name, c.email FROM customers c JOIN orders o ON c.id = o.customer_id WHERE c.country = 'India';"}'
Output: {"reward": 1.0, "done": true, "info": {"score": 1.0, "reason": "Perfect! Correct results with proper JOIN."}}

## 💡 Why Real Execution Wins

Others: text matching (fake scoring)
Us: SQLite executes every query

Others: binary 0 or 1 reward
Us: partial progress 0.0 to 1.0

Others: 3 basic tasks
Us: 5 real-world tasks

Others: toy problems
Us: production SQL patterns

Others: random reward signal
Us: deterministic, consistent grading

## 📋 5 Tasks

EASY - Fix Broken JOIN (max 5 steps)
Bug: Missing JOIN condition, cartesian product
Score 0.0: syntax error
Score 0.2: partially correct
Score 0.65: correct but no explicit JOIN
Score 1.0: perfect JOIN with DISTINCT

MEDIUM - Eliminate N+1 Subquery (max 8 steps)
Bug: Correlated subquery runs N times
Score 0.0: syntax error
Score 0.35: JOIN structure but wrong totals
Score 0.7: correct results with JOIN
Score 1.0: perfect JOIN + GROUP BY

MEDIUM - Top Rated Products Per Category (max 8 steps)
Goal: AVG rating per category
Score 0.0: syntax error
Score 0.25: partial joins
Score 0.7: correct but missing ORDER BY
Score 1.0: perfect aggregation

HARD - Monthly Revenue CTEs (max 10 steps)
Goal: Monthly report using WITH clause
Score 0.0: syntax error
Score 0.3: basic structure only
Score 0.7: CTE but missing filters
Score 1.0: perfect CTE

HARD - Customer Lifetime Value Window Functions (max 10 steps)
Goal: ROW_NUMBER() ranking by spend
Score 0.0: syntax error
Score 0.25: basic joins only
Score 0.65: correct totals but no window function
Score 1.0: perfect window function ranking

## 🔌 API Reference

POST /reset - Body: {"task_id": "task_easy"} - Start new episode
POST /step - Body: {"query": "SELECT ..."} - Submit SQL action
GET /state - Get current episode metadata
GET /tasks - List all 5 tasks with descriptions
POST /grader - Body: {"task_id": "...", "query": "..."} - Grade any query
POST /baseline - Run baseline on all 5 tasks

## ��️ Database Schema

customers(id, name, email, country, created_at)
products(id, name, category, price, stock)
orders(id, customer_id, created_at, status)
order_items(id, order_id, product_id, quantity, unit_price)
reviews(id, customer_id, product_id, rating, review_text, created_at)

## 🤖 Run Inference

export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_SPACE_URL=https://alokrajkumar-sql-query-optimizer.hf.space
python3 inference.py

Expected output:
[START] task=task_easy env=sql-query-optimizer model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=SELECT ... reward=0.10 done=false error=null
[STEP] step=2 action=SELECT ... reward=0.90 done=false error=null
[STEP] step=3 action=SELECT ... reward=1.00 done=true error=null
[END] success=true steps=3 score=1.000 rewards=0.10,0.90,1.00

## ⚠️ Limitations

Single session: Not thread-safe for concurrent users
SQLite only: No PostgreSQL-specific syntax support
Fixed schema: Database schema cannot change at runtime
No persistence: Episodes reset on server restart

## 🔮 Future Improvements

Multi-database support (PostgreSQL, MySQL)
Custom schema upload by users
Query execution plan analysis task
Index recommendation task
Query cost estimation task

## �� Project Structure

sql-query-optimizer/
  Dockerfile            - Container (Python 3.11-slim)
  openenv.yaml          - Environment metadata
  pyproject.toml        - Project dependencies
  uv.lock               - Locked dependencies
  models.py             - Pydantic typed models
  tasks.py              - 5 tasks + SQLite engine
  graders.py            - Deterministic scoring (0.0-1.0)
  inference.py          - Baseline inference script
  TECHNICAL_REPORT.md   - Architecture deep-dive
  README.md             - This file
  server/
    environment.py      - Core OpenEnv logic
    app.py              - FastAPI + Web UI
    requirements.txt    - Server dependencies

## 📊 Baseline Scores

task_easy: 1.0
task_medium: 1.0
task_medium_2: 1.0
task_hard: 1.0
task_hard_2: 1.0
Average: 1.0

## 🏗️ Tech Stack

OpenEnv 0.2.3 - Meta + HuggingFace RL framework
FastAPI 0.135 - HTTP server
SQLite - Real in-memory execution
Pydantic 2.x - Type-safe models
Docker - Containerized deployment
HuggingFace Spaces - Cloud hosting
Python 3.11 - Runtime
