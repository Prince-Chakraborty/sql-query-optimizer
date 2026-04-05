---
title: SQL Query Optimizer
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SQL Query Optimizer Environment

An OpenEnv-compliant RL environment where AI agents learn to fix and optimize real SQL queries through trial and error with actual SQLite execution feedback.

## API Endpoints

POST /reset  - Start new episode
POST /step   - Submit SQL query action
GET  /state  - Get current episode state
GET  /tasks  - List all tasks
POST /grader - Grade a query directly
POST /baseline - Run baseline on all tasks

## Database Schema

customers(id, name, email, country, created_at)
products(id, name, category, price, stock)
orders(id, customer_id, created_at, status)
order_items(id, order_id, product_id, quantity, unit_price)
