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

    if got_names == expected_names:
        query_upper = query.upper()
        if "JOIN" in query_upper:
            score = 1.0
            reason = "Perfect! Correct results with proper JOIN condition."
        else:
            score = 0.7
            reason = "Correct results but use explicit JOIN syntax."
    elif expected_names.issubset(got_names):
        score = 0.4
        reason = f"Correct customers found but extra rows returned."
    elif got_names & expected_names:
        score = 0.2
        reason = f"Partially correct. Got {got_names}, expected {expected_names}"
    else:
        score = 0.1
        reason = f"Query runs but wrong results. Got: {got_names}"

    return score, reason, {
        "syntax_correct": True,
        "results_correct": got_names == expected_names,
        "performance_improved": False,
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
    results_correct = len(got_totals & expected_totals) >= 3

    if results_correct and uses_join and uses_group:
        score = 1.0
        reason = "Excellent! Correct totals using efficient JOIN + GROUP BY."
    elif results_correct and uses_join:
        score = 0.8
        reason = "Correct results with JOIN. Add GROUP BY for cleaner aggregation."
    elif results_correct:
        score = 0.5
        reason = "Correct totals but rewrite with JOIN + GROUP BY."
    elif uses_join and uses_group:
        score = 0.4
        reason = "Good structure but totals not matching expected values."
    else:
        score = 0.2
        reason = "Query runs but results incorrect. Check aggregation logic."

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

    score = 0.1
    reasons = []

    if has_enough_cols:
        score += 0.2
        reasons.append("has required columns")
    if filters_completed:
        score += 0.2
        reasons.append("filters completed orders")
    if uses_cte:
        score += 0.2
        reasons.append("uses CTE")
    if ordered:
        score += 0.15
        reasons.append("results ordered")
    if uses_cte and filters_completed and has_enough_cols and ordered:
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


GRADERS = {
    "task_easy": grade_easy,
    "task_medium": grade_medium,
    "task_hard": grade_hard,
}


def grade(task_id: str, query: str) -> Dict[str, Any]:
    if task_id not in GRADERS:
        raise ValueError(f"No grader for task: {task_id}")
    score, reason, details = GRADERS[task_id](query)
    return {
        "task_id": task_id,
        "score": round(score, 3),
        "reason": reason,
        **details
    }
