import sqlite3
import time
from typing import Dict, Any, Optional, Tuple

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""

SEED_SQL = """
INSERT INTO customers VALUES
(1,'Alice','alice@email.com','India','2023-01-10'),
(2,'Bob','bob@email.com','USA','2023-02-15'),
(3,'Carol','carol@email.com','India','2023-03-20'),
(4,'Dave','dave@email.com','UK','2023-04-25'),
(5,'Eve','eve@email.com','India','2023-05-30');

INSERT INTO products VALUES
(1,'Laptop','Electronics',999.99,50),
(2,'Phone','Electronics',499.99,100),
(3,'Desk','Furniture',199.99,30),
(4,'Chair','Furniture',149.99,40),
(5,'Monitor','Electronics',299.99,60);

INSERT INTO orders VALUES
(1,1,'2024-01-05','completed'),
(2,2,'2024-01-10','completed'),
(3,1,'2024-02-01','completed'),
(4,3,'2024-02-14','pending'),
(5,4,'2024-03-01','completed'),
(6,5,'2024-03-10','completed'),
(7,2,'2024-03-15','pending');

INSERT INTO order_items VALUES
(1,1,1,1,999.99),
(2,1,2,2,499.99),
(3,2,3,1,199.99),
(4,3,5,1,299.99),
(5,4,4,2,149.99),
(6,5,1,1,999.99),
(7,6,2,1,499.99),
(8,7,3,2,199.99);
"""

SCHEMA_DESCRIPTION = """
Tables:
- customers(id, name, email, country, created_at)
- products(id, name, category, price, stock)
- orders(id, customer_id, created_at, status)
- order_items(id, order_id, product_id, quantity, unit_price)
"""


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    return conn


def run_query(query: str) -> Tuple[Optional[list], Optional[str], float]:
    conn = get_db()
    try:
        start = time.perf_counter()
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        elapsed = (time.perf_counter() - start) * 1000
        return rows, None, round(elapsed, 3)
    except Exception as e:
        return None, str(e), 0.0
    finally:
        conn.close()


TASKS: Dict[str, Dict[str, Any]] = {
    "task_easy": {
        "id": "task_easy",
        "difficulty": "easy",
        "max_steps": 5,
        "name": "Fix the Broken Query",
        "task_description": (
            "The following SQL query is supposed to return all customers from India "
            "who have placed at least one order. But it has a bug and returns wrong results. "
            "Fix it so it returns the correct customers."
        ),
        "original_query": (
            "SELECT DISTINCT c.name, c.email "
            "FROM customers c, orders o "
            "WHERE c.country = 'India';"
        ),
        "hint": "Check if the tables are properly joined.",
        "expected_row_check": lambda rows: (
            {(r[0], r[1]) for r in rows} ==
            {("Alice", "alice@email.com"),
             ("Carol", "carol@email.com"),
             ("Eve", "eve@email.com")}
        ),
    },
    "task_medium": {
        "id": "task_medium",
        "difficulty": "medium",
        "max_steps": 8,
        "name": "Eliminate the N+1 Subquery",
        "task_description": (
            "The query below finds customers along with their total spending. "
            "It uses a correlated subquery which is slow. "
            "Rewrite it using a JOIN and GROUP BY for better performance. "
            "Result must show customer name and total amount spent."
        ),
        "original_query": (
            "SELECT c.name, "
            "(SELECT SUM(oi.quantity * oi.unit_price) "
            " FROM orders o JOIN order_items oi ON o.id = oi.order_id "
            " WHERE o.customer_id = c.id) AS total_spent "
            "FROM customers c;"
        ),
        "hint": "Use JOIN + GROUP BY instead of a correlated subquery.",
        "expected_row_check": lambda rows: (
            len(rows) > 0 and
            any(abs(float(r[1]) - 1799.97) < 1.0
                for r in rows if r[1] is not None)
        ),
    },
    "task_hard": {
        "id": "task_hard",
        "difficulty": "hard",
        "max_steps": 10,
        "name": "Monthly Revenue Report with CTEs",
        "task_description": (
            "Write a query to produce a monthly revenue report showing: "
            "month (YYYY-MM), total_orders, total_revenue. "
            "Use CTEs (WITH clause) for clarity. "
            "Only include completed orders. "
            "Order results by month ascending."
        ),
        "original_query": (
            "SELECT * FROM orders WHERE status = 'completed';"
        ),
        "hint": "Use WITH monthly AS (...) then SELECT from it.",
        "expected_row_check": lambda rows: (
            len(rows) >= 1 and len(rows[0]) >= 3
        ),
    },
}


def get_task(task_id: str) -> Dict[str, Any]:
    if task_id not in TASKS:
        raise ValueError(
            f"Unknown task: {task_id}. Valid: {list(TASKS.keys())}"
        )
    return TASKS[task_id]


def list_tasks() -> list:
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "difficulty": t["difficulty"],
            "max_steps": t["max_steps"],
            "description": t["task_description"],
        }
        for t in TASKS.values()
    ]
