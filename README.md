# SQL Query Optimizer Environment

An OpenEnv-compliant RL environment where AI agents learn to fix and optimize real SQL queries through trial and error with actual SQLite execution feedback.

## What Makes This Unique

- Real SQL Execution - queries actually run in SQLite, errors are real
- Partial Reward Shaping - agents get credit for syntax fixes, logic fixes, performance improvements
- 3 Difficulty Levels - easy, medium, hard
- No Text Matching - graders evaluate actual query results

## Environment Overview

Action Space: SQL query string + explanation
Observation Space: Task description, schema, last error, execution time, rows returned
Reward Range: -0.05 to 1.0
Tasks: 3 (easy, medium, hard)
Max Steps: 5 / 8 / 10 per task

## Tasks

Task 1 Easy: Fix the Broken Query
Fix a SQL query with a missing JOIN condition that returns wrong results.

Task 2 Medium: Eliminate the N+1 Subquery
Rewrite a correlated subquery using JOIN + GROUP BY for performance.

Task 3 Hard: Monthly Revenue Report with CTEs
Write a full monthly revenue report using CTEs from scratch.

## Setup

Install:
pip install -r server/requirements.txt

Run Locally:
uvicorn server.app:app --host 0.0.0.0 --port 7860

Run with Docker:
docker build -f server/Dockerfile -t sql-query-optimizer .
docker run -p 7860:7860 sql-query-optimizer

## API Endpoints

POST /reset  - Start new episode
POST /step   - Submit SQL query action
GET  /state  - Get current episode state
GET  /tasks  - List all tasks
POST /grader - Grade a query directly
POST /baseline - Run baseline on all tasks

## Run Inference

export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_SPACE_URL=https://your-space.hf.space
python inference.py

## Database Schema

customers(id, name, email, country, created_at)
products(id, name, category, price, stock)
orders(id, customer_id, created_at, status)
order_items(id, order_id, product_id, quantity, unit_price)

## Project Structure

code-review-env/
  openenv.yaml        - Environment metadata
  models.py           - Pydantic typed models
  tasks.py            - Task definitions + SQLite engine
  graders.py          - Scoring logic
  inference.py        - Baseline inference script
  README.md           - This file
  .env.example        - Environment variables template
  server/
    environment.py    - Core OpenEnv logic
    app.py            - FastAPI server
    requirements.txt  - Dependencies
    Dockerfile        - Container setup

## License
MIT
