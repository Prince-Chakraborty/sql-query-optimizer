---
title: SQL Query Optimizer
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🗄️ SQL Query Optimizer — OpenEnv RL Environment

> Train AI agents to fix and optimize real SQL queries through actual SQLite execution feedback.

## ⚡ Quick Start (Run in under 5 minutes)

### Option 1 — Use Live HuggingFace Space
curl -X POST https://alokrajkumar-sql-query-optimizer.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_easy"}'

### Option 2 — Run Locally
git clone https://github.com/Prince-Chakraborty/sql-query-optimizer
cd sql-query-optimizer
pip install -r server/requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860

### Option 3 — Run with Docker
docker build -t sql-query-optimizer .
docker run -p 7860:7860 sql-query-optimizer

## 🎯 What This Does

An AI agent learns to fix and optimize SQL queries by:
1. Receiving a broken/slow SQL query
2. Submitting a fixed version
3. Getting real execution feedback from SQLite
4. Receiving partial reward based on correctness

## 🔄 Agent Flow

Input Query (broken/slow)
    |
    v
Agent (LLM) reads observation
    |
    v
Agent submits fixed SQL query
    |
    v
SQLite executes query ACTUALLY
    |
    v
Grader scores result (0.0 to 1.0)
    |
    v
Reward = improvement over best score
    |
    v
Agent learns and tries again

## 🎮 Demo

Step 1: Reset environment
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_easy"}'

Step 2: Submit broken query (score = 0.1)
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM customers WHERE country = 'India';"}'

Step 3: Submit fixed query (score = 1.0)
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT DISTINCT c.name, c.email FROM customers c JOIN orders o ON c.id = o.customer_id WHERE c.country = 'India';"}'

Result: reward=1.0, done=true

## 📋 5 Tasks (Easy to Hard)

EASY: Fix Broken JOIN Query (max 5 steps)
- Bug: Missing JOIN condition causes cartesian product
- Score 0.0: syntax error
- Score 0.2: partially correct results
- Score 0.65: correct but no explicit JOIN
- Score 1.0: perfect JOIN with DISTINCT

MEDIUM: Eliminate N+1 Subquery (max 8 steps)
- Bug: Correlated subquery runs N times
- Score 0.0: syntax error
- Score 0.35: JOIN structure correct but wrong totals
- Score 0.7: correct results with JOIN
- Score 1.0: perfect JOIN + GROUP BY

MEDIUM: Top Rated Products Per Category (max 8 steps)
- Goal: AVG rating per category using JOIN
- Score 0.0: syntax error
- Score 0.25: partial joins
- Score 0.7: correct but missing ORDER BY
- Score 1.0: perfect aggregation

HARD: Monthly Revenue Report with CTEs (max 10 steps)
- Goal: Monthly report using WITH clause
- Score 0.0: syntax error
- Score 0.3: basic structure
- Score 0.7: CTE but missing filters
- Score 1.0: perfect CTE with all requirements

HARD: Customer Lifetime Value with Window Functions (max 10 steps)
- Goal: ROW_NUMBER() ranking by total spend
- Score 0.0: syntax error
- Score 0.25: basic joins only
- Score 0.65: correct totals but no window function
- Score 1.0: perfect window function ranking

## 🔌 API Reference

POST /reset
Body: {"task_id": "task_easy"}
Returns: observation, episode_id

POST /step
Body: {"query": "SELECT ...", "explanation": "optional"}
Returns: observation, reward, done, info

GET /state
Returns: episode_id, step_count, task_id, done, total_reward

GET /tasks
Returns: list of all 5 tasks with descriptions

POST /grader
Body: {"task_id": "task_easy", "query": "SELECT ..."}
Returns: score, reason, details

POST /baseline
Returns: scores for all 5 tasks

## 🗄️ Database Schema

customers(id, name, email, country, created_at)
products(id, name, category, price, stock)
orders(id, customer_id, created_at, status)
order_items(id, order_id, product_id, quantity, unit_price)
reviews(id, customer_id, product_id, rating, review_text, created_at)

E-commerce dataset: 5 customers, 5 products, 7 orders, 8 order items, 7 reviews

## 🤖 Run Inference

export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_SPACE_URL=https://alokrajkumar-sql-query-optimizer.hf.space

python3 inference.py

Expected output:
[START] task=task_easy env=sql-query-optimizer model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=SELECT ... reward=0.00 done=false error=null
[STEP] step=2 action=SELECT ... reward=1.00 done=true error=null
[END] success=true steps=2 score=1.000 rewards=0.00,1.00

## 💡 Why This Wins

Real execution: Queries actually run in SQLite, not text matched
Partial rewards: Agent gets credit for each improvement
5 tasks: Easy to hard, each testing different SQL concepts
Window functions: Advanced SQL rarely seen in RL environments
Deterministic: Same query always gets same score

## ⚠️ Limitations

Single session: Environment is not thread-safe for concurrent users
SQLite only: Does not support PostgreSQL-specific syntax
No persistence: Episodes reset when server restarts
Schema fixed: Database schema cannot be changed at runtime

## 🔮 Future Improvements

Multi-database support (PostgreSQL, MySQL)
Custom schema upload
Query execution plan analysis
Index recommendation task
Query cost estimation task

## 📁 Project Structure

code-review-env/
  Dockerfile          - Container setup (Python 3.11)
  openenv.yaml        - Environment metadata
  pyproject.toml      - Dependencies
  models.py           - Pydantic typed models
  tasks.py            - 5 task definitions + SQLite engine
  graders.py          - Scoring logic (0.0 to 1.0)
  inference.py        - Baseline inference script
  TECHNICAL_REPORT.md - Detailed architecture report
  README.md           - This file
  server/
    environment.py    - Core OpenEnv logic
    app.py            - FastAPI server + Web UI
    requirements.txt  - Python dependencies

## 📊 Baseline Scores

task_easy: 1.0
task_medium: 1.0
task_medium_2: 1.0
task_hard: 1.0
task_hard_2: 1.0
Average: 1.0

## 🏗️ Tech Stack

OpenEnv 0.2.3 - Core RL framework by Meta + HuggingFace
FastAPI 0.135 - HTTP server
SQLite - In-memory query execution
Pydantic 2.x - Type-safe models
Docker - Containerized deployment
HuggingFace Spaces - Cloud hosting
