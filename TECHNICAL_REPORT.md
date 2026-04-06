# SQL Query Optimizer - Technical Report

## 1. Problem Statement
SQL performance issues cost companies millions daily.
Developers write broken or slow queries that tank application performance.
Our environment trains AI agents to automatically detect and fix these issues.

## 2. Architecture

Agent (LLM via OpenAI Client)
    -> inference.py
    -> HuggingFace Space (FastAPI Server)
    -> SQLOptimizerEnvironment
    -> SQLite In-Memory DB (Real Execution)
    -> Graders (Score 0.0 to 1.0)

## 3. OpenEnv Compliance

Models (Pydantic typed):
- SQLAction: query + explanation
- SQLObservation: task, schema, error, execution time
- EpisodeState: episode_id, step_count, done, reward

API Endpoints:
- POST /reset: initializes episode, returns observation
- POST /step: executes SQL, grades it, returns reward
- GET /state: returns episode metadata
- GET /tasks: lists all 5 tasks
- POST /grader: grades any query
- POST /baseline: runs baseline on all tasks

## 4. Reinforcement Learning Design

State Space - The agent observes:
- Task description
- Database schema
- Original broken query
- Last submitted query
- Error message if any
- Execution time in ms
- Rows returned
- Step number

Action Space - The agent submits:
- A SQL query string
- Optional explanation

Reward Function:
reward = max(0.0, current_score - best_score_so_far)
penalty = -0.05 for syntax errors

Score breakdown:
- Syntax correct: +0.1
- Results partially correct: +0.2
- Results fully correct: +0.4
- Uses optimal query pattern: +0.3

Episode Termination:
- Score reaches 1.0 (perfect solution)
- Max steps reached (5/8/10 depending on difficulty)

## 5. Tasks Design

Task 1 - Easy: Fix Broken JOIN (max 5 steps)
Bug: Missing JOIN condition causes cartesian product
Expected: 3 correct customers from India with orders
Grading: 0.0 (syntax error) to 1.0 (perfect JOIN)

Task 2 - Medium: Eliminate N+1 (max 8 steps)
Bug: Correlated subquery runs N+1 times
Expected: Customer totals using efficient JOIN+GROUP BY
Grading: 0.0 to 1.0 (JOIN+GROUP BY)

Task 3 - Medium: Top Products Per Category (max 8 steps)
Goal: Find highest rated product per category
Expected: JOIN products+reviews, AVG rating, GROUP BY
Grading: 0.0 to 1.0 (perfect aggregation)

Task 4 - Hard: Monthly Revenue CTE (max 10 steps)
Goal: Monthly revenue report using CTEs
Expected: WITH clause, completed orders only, ordered by month
Grading: 0.0 to 1.0 (perfect CTE)

Task 5 - Hard: CLV Window Functions (max 10 steps)
Goal: Customer lifetime value with ROW_NUMBER()
Expected: Window functions, completed orders, ranking
Grading: 0.0 to 1.0 (perfect window function)

## 6. What Makes Us Unique

Real SQLite execution vs text matching
Partial progress rewards vs binary 0/1
Real e-commerce SQL vs toy problems
Every step reward vs end of episode only
Live in-memory SQLite vs mocked database

## 7. Baseline Results

task_easy: 1.0 - Perfect JOIN
task_medium: 1.0 - Perfect GROUP BY
task_medium_2: 1.0 - Perfect AVG aggregation
task_hard: 1.0 - Perfect CTE
task_hard_2: 1.0 - Perfect Window Function
Average: 1.0

## 8. Scalability

Horizontal: Each episode runs in isolated SQLite, stateless, infinitely scalable
New tasks: Add any SQL task by defining expected output + grader function
New schemas: Plug in any database schema for domain-specific training
Production: Replace SQLite with PostgreSQL for real production queries

## 9. Business Use Case

Enterprise: Train AI copilots to fix developer SQL mistakes automatically
Education: Train students on SQL optimization with real feedback
DevTools: Integrate into IDEs to suggest SQL optimizations in real-time
Cost savings: Slow queries cost companies thousands per hour in compute

## 10. Tech Stack

OpenEnv: Core RL framework (Meta + HuggingFace)
FastAPI: HTTP server
SQLite: In-memory query execution
Pydantic: Type-safe models
Docker: Containerized deployment
HuggingFace Spaces: Cloud deployment
