---
title: SQL Query Optimizer
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🗄️ SQL Query Optimizer — OpenEnv RL Environment

An RL environment that trains AI agents to fix and optimize SQL queries using real SQLite execution feedback.

## The Problem
SQL bugs and slow queries cost companies millions daily. No existing RL environment trains agents on real SQL execution — they all use synthetic scoring.

## How It Works

Agent receives broken SQL query
    ↓
Submits fixed query via /step
    ↓
SQLite ACTUALLY executes it
    ↓
Grader scores real results (0.0–0.99)
    ↓
Reward = improvement over best score so far

## Quick Start

Use live Space:
curl -X POST https://alokrajkumar-sql-query-optimizer.hf.space/reset -H "Content-Type: application/json" -d '{"task_id": "task_easy"}'

Run locally:
git clone https://github.com/Prince-Chakraborty/sql-query-optimizer
cd sql-query-optimizer
pip install -r server/requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860

## Example: Learning Signal

Step 1 — Wrong query → reward: 0.10
Step 2 — Partial fix → reward: 0.45
Step 3 — Perfect JOIN → reward: 0.99
Agent learned: always use explicit JOIN with ON clause

## Tasks
5 SQL optimization tasks covering JOINs, subqueries, CTEs, aggregations, and window functions. Difficulty: easy → medium → hard.

## Core API

POST /reset  — Start new episode
POST /step   — Submit SQL query, get reward
GET  /state  — Get episode metadata

## Real-World Impact
Built with real SQL execution using SQLite instead of synthetic scoring.
Applicable to enterprise query optimization, developer tooling, and SQL education at scale.

## Results
Average Score: 0.99 across all 5 tasks

## Run Inference

export API_BASE_URL=your_endpoint
export API_KEY=your_key
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_SPACE_URL=https://alokrajkumar-sql-query-optimizer.hf.space
python3 inference.py

## Tech Stack
OpenEnv 0.2.3 · FastAPI · SQLite · Pydantic 2.x · Docker · HuggingFace Spaces · Python 3.11

## Limitations
Single-session (not thread-safe). SQLite only. Fixed schema.

## Future
Multi-database support · Query execution plan analysis
