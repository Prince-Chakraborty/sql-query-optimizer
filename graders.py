from typing import Dict, Any, Tuple
from tasks import run_query


def grade_easy(query: str) -> Tuple[float, str, Dict[str, Any]]:
    rows, error, time_ms = run_query(query)

    if error:
        return 0.0, f"Syntax error: {error}", {
            "syntax_correct": False,
            "results_correct": False,
            "performance_improved": False
        }

    expected_names = {"Alice", "Carol", "Eve"}
    got_names = {str(r[0]) for r in rows} if rows else set()

    query_upper = query.upper()
    uses_join = "JOIN" in query_upper
    uses_distinct = "DISTINCT" in query_upper

    if got_names == expected_names and uses_join and uses_distinct:
        score = 1.0
        reason = "Perfect! Correct results with proper JOIN and DISTINCT."
    elif got_names == expected_names and uses_join:
        score = 0.85
        reason = "Correct results with JOIN. Add DISTINCT to avoid duplicates."
    elif got_names == expected_names:
        score = 0.65
        reason = "Correct results but use explicit JOIN syntax."
    elif expected_names.issubset(got_names):
        score = 0.4
        reason = f"Correct customers found but extra rows returned."
    elif got_names & expected_names:
        score = 0.2
        reason = f"Partially correct. Got {got_names}, expected {expected_names}"
    elif rows and len(rows) > 0:
        score = 0.1
        reason = f"Query runs but completely wrong results."
    else:
        score = 0.05
        reason = "Query runs but returns no rows."

    return score, reason, {
        "syntax_correct": True,
        "results_correct": got_names == expected_names,
        "performance_improved": uses_join,
        "rows_returned": len(rows) if rows else 0,
        "execution_time_ms": time_ms
    }


def grade_medium(query: str) -> Tuple[float, str, Dict[str, Any]]:
    rows, error, time_ms = run_query(query)

    if error:
        return 0.0, f"Syntax error: {error}", {
            "syntax_correct": False,
            "results_correct": False,
            "performance_improved": False
        }

    if not rows:
        return 0.1, "Query ran but returned no rows.", {
            "syntax_correct": True,
            "results_correct": False,
            "performance_improved": False
        }

    try:
        totals = [float(r[1]) for r in rows if r[1] is not None]
    except (IndexError, TypeError, ValueError):
        return 0.2, "Could not parse total_spent column.", {
            "syntax_correct": True,
            "results_correct": False,
            "performance_improved": False
        }

    expected_totals = {2299.96, 199.99, 299.98, 999.99, 499.99}
    got_totals = set(round(t, 2) for t in totals)

    query_upper = query.upper()
    uses_join = "JOIN" in query_upper
    uses_group = "GROUP BY" in query_upper
    no_subquery = "SELECT" not in query_upper.split("FROM")[0].replace("SELECT", "", 1)
    results_correct = len(got_totals & expected_totals) >= 3

    if results_correct and uses_join and uses_group and no_subquery:
        score = 1.0
        reason = "Perfect! Correct totals using efficient JOIN + GROUP BY."
    elif results_correct and uses_join and uses_group:
        score = 0.85
        reason = "Correct results with JOIN + GROUP BY."
    elif results_correct and uses_join:
        score = 0.7
        reason = "Correct results with JOIN. Add GROUP BY."
    elif results_correct:
        score = 0.5
        reason = "Correct totals but still uses subquery."
    elif uses_join and uses_group:
        score = 0.35
        reason = "Good structure but totals not matching."
    elif uses_join:
        score = 0.2
        reason = "Uses JOIN but results incorrect."
    else:
        score = 0.1
        reason = "Query runs but results incorrect."

    return score, reason, {
        "syntax_correct": True,
        "results_correct": results_correct,
        "performance_improved": uses_join and uses_group,
        "rows_returned": len(rows),
        "execution_time_ms": time_ms
    }


def grade_hard(query: str) -> Tuple[float, str, Dict[str, Any]]:
    rows, error, time_ms = run_query(query)

    if error:
        return 0.0, f"Syntax error: {error}", {
            "syntax_correct": False,
            "results_correct": False,
            "performance_improved": False
        }

    if not rows:
        return 0.1, "Query ran but returned no rows.", {
            "syntax_correct": True,
            "results_correct": False,
            "performance_improved": False
        }

    query_upper = query.upper()
    uses_cte = "WITH " in query_upper
    filters_completed = "'COMPLETED'" in query_upper
    has_enough_cols = len(rows[0]) >= 3
    ordered = "ORDER BY" in query_upper
    has_month = any("2024" in str(r[0]) for r in rows)

    score = 0.05
    reasons = []

    if has_enough_cols:
        score += 0.15
        reasons.append("has required columns")
    if filters_completed:
        score += 0.2
        reasons.append("filters completed orders")
    if uses_cte:
        score += 0.25
        reasons.append("uses CTE")
    if ordered:
        score += 0.15
        reasons.append("results ordered")
    if has_month:
        score += 0.1
        reasons.append("correct month format")
    if uses_cte and filters_completed and has_enough_cols and ordered and has_month:
        score = 1.0
        reasons = ["Perfect CTE-based monthly revenue report!"]

    reason = (
        "Partial credit: " + ", ".join(reasons)
        if score < 1.0 else reasons[0]
    )

    return round(min(score, 1.0), 3), reason, {
        "syntax_correct": True,
        "results_correct": uses_cte and filters_completed and has_enough_cols,
        "performance_improved": uses_cte,
        "rows_returned": len(rows),
        "execution_time_ms": time_ms
    }


def grade_medium_2(query: str) -> Tuple[float, str, Dict[str, Any]]:
    """Top rated products per category."""
    rows, error, time_ms = run_query(query)

    if error:
        return 0.0, f"Syntax error: {error}", {
            "syntax_correct": False,
            "results_correct": False,
            "performance_improved": False
        }

    if not rows:
        return 0.1, "Query ran but returned no rows.", {
            "syntax_correct": True,
            "results_correct": False,
            "performance_improved": False
        }

    query_upper = query.upper()
    uses_join = "JOIN" in query_upper
    uses_group = "GROUP BY" in query_upper
    uses_avg = "AVG" in query_upper
    has_enough_cols = len(rows[0]) >= 3
    ordered = "ORDER BY" in query_upper

    score = 0.05
    reasons = []

    if uses_join:
        score += 0.2
        reasons.append("joins products with reviews")
    if uses_avg:
        score += 0.2
        reasons.append("uses AVG rating")
    if uses_group:
        score += 0.2
        reasons.append("groups by category")
    if has_enough_cols:
        score += 0.15
        reasons.append("has required columns")
    if ordered:
        score += 0.1
        reasons.append("results ordered")
    if uses_join and uses_avg and uses_group and has_enough_cols and ordered:
        score = 1.0
        reasons = ["Perfect! Top rated products per category with correct aggregation."]

    reason = (
        "Partial credit: " + ", ".join(reasons)
        if score < 1.0 else reasons[0]
    )

    return round(min(score, 1.0), 3), reason, {
        "syntax_correct": True,
        "results_correct": uses_join and uses_avg and uses_group,
        "performance_improved": uses_join and uses_group,
        "rows_returned": len(rows),
        "execution_time_ms": time_ms
    }


def grade_hard_2(query: str) -> Tuple[float, str, Dict[str, Any]]:
    """Customer lifetime value with window functions."""
    rows, error, time_ms = run_query(query)

    if error:
        return 0.0, f"Syntax error: {error}", {
            "syntax_correct": False,
            "results_correct": False,
            "performance_improved": False
        }

    if not rows:
        return 0.1, "Query ran but returned no rows.", {
            "syntax_correct": True,
            "results_correct": False,
            "performance_improved": False
        }

    query_upper = query.upper()
    uses_join = "JOIN" in query_upper
    uses_group = "GROUP BY" in query_upper
    uses_window = "ROW_NUMBER" in query_upper or "OVER" in query_upper
    filters_completed = "'COMPLETED'" in query_upper
    has_enough_cols = len(rows[0]) >= 4
    ordered = "ORDER BY" in query_upper

    score = 0.05
    reasons = []

    if uses_join:
        score += 0.15
        reasons.append("joins required tables")
    if filters_completed:
        score += 0.15
        reasons.append("filters completed orders")
    if uses_group:
        score += 0.15
        reasons.append("groups correctly")
    if uses_window:
        score += 0.25
        reasons.append("uses window function")
    if has_enough_cols:
        score += 0.1
        reasons.append("has required columns")
    if ordered:
        score += 0.1
        reasons.append("results ordered")
    if uses_join and uses_group and uses_window and filters_completed and has_enough_cols:
        score = 1.0
        reasons = ["Perfect CLV ranking with window functions!"]

    reason = (
        "Partial credit: " + ", ".join(reasons)
        if score < 1.0 else reasons[0]
    )

    return round(min(score, 1.0), 3), reason, {
        "syntax_correct": True,
        "results_correct": uses_join and uses_window and filters_completed,
        "performance_improved": uses_window,
        "rows_returned": len(rows),
        "execution_time_ms": time_ms
    }


GRADERS = {
    "task_easy": grade_easy,
    "task_medium": grade_medium,
    "task_medium_2": grade_medium_2,
    "task_hard": grade_hard,
    "task_hard_2": grade_hard_2,
}


def grade(task_id: str, query: str) -> Dict[str, Any]:
    if task_id not in GRADERS:
        raise ValueError(f"No grader for task: {task_id}")
    score, reason, details = GRADERS[task_id](query)
    # Scores must be strictly between 0 and 1 (hackathon requirement)
    score = round(max(0.01, min(0.99, score)), 3)
    return {
        "task_id": task_id,
        "score": score,
        "reason": reason,
        **details
    }


def clamp_score(score: float) -> float:
    """Ensure score is strictly between 0 and 1 as required by hackathon."""
    return round(max(0.01, min(0.99, score)), 3)
