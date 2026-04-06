"""
Inference Script - SQL Query Optimizer Environment
Follows EXACT format required by hackathon judges.
"""

import os
import textwrap
from typing import List, Optional
from openai import OpenAI
import httpx

# ─────────────────────────────────────────
# ENV VARIABLES (mandatory as per spec)
# ─────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("API_KEY", os.getenv("HF_TOKEN", ""))
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

BENCHMARK = "sql-query-optimizer"
MAX_STEPS = 8
TEMPERATURE = 0.3
MAX_TOKENS = 512
SUCCESS_SCORE_THRESHOLD = 0.5

# ─────────────────────────────────────────
# LOGGING (exact format required by judges)
# ─────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_clean = action.replace("\n", " ").strip()[:200]
    print(
        f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

# ─────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert SQL engineer. Your job is to fix or optimize SQL queries.
    
    You will be given:
    - A task description
    - A database schema
    - A broken or slow SQL query
    - Feedback from previous attempts (if any)
    
    Rules:
    - Reply with ONLY the corrected SQL query
    - No explanation, no markdown, no code blocks
    - Just the raw SQL query ending with semicolon
    - Make sure it runs correctly on SQLite
""").strip()


def build_user_prompt(
    task_description: str,
    schema: str,
    original_query: str,
    last_query: Optional[str],
    error_message: Optional[str],
    execution_time_ms: Optional[float],
    rows_returned: Optional[int],
    hint: Optional[str],
    step: int,
    history: List[str],
) -> str:
    history_block = "\n".join(history[-3:]) if history else "None"
    prompt = f"""
TASK: {task_description}

DATABASE SCHEMA:
{schema}

ORIGINAL QUERY:
{original_query}
"""
    if last_query:
        prompt += f"\nYOUR LAST ATTEMPT:\n{last_query}\n"
    if error_message:
        prompt += f"\nERROR: {error_message}\n"
    if rows_returned is not None:
        prompt += f"\nROWS RETURNED: {rows_returned}\n"
    if hint:
        prompt += f"\nHINT: {hint}\n"
    if history:
        prompt += f"\nPREVIOUS ATTEMPTS:\n{history_block}\n"
    prompt += f"\nStep {step} of {MAX_STEPS}. Write the corrected SQL query now:"
    return prompt.strip()


def get_sql_from_model(
    client: OpenAI,
    task_description: str,
    schema: str,
    original_query: str,
    last_query: Optional[str],
    error_message: Optional[str],
    execution_time_ms: Optional[float],
    rows_returned: Optional[int],
    hint: Optional[str],
    step: int,
    history: List[str],
) -> str:
    user_prompt = build_user_prompt(
        task_description, schema, original_query,
        last_query, error_message, execution_time_ms,
        rows_returned, hint, step, history
    )
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        text = text.replace("```sql", "").replace("```", "").strip()
        return text if text else "SELECT 1;"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "SELECT 1;"


def run_task(task_id: str, base_url: str) -> dict:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    hf_url = base_url.rstrip("/")

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    history: List[str] = []

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_resp = httpx.post(
            f"{hf_url}/reset",
            json={"task_id": task_id},
            timeout=30
        )
        reset_resp.raise_for_status()
        obs = reset_resp.json()["observation"]

        for step in range(1, MAX_STEPS + 1):
            sql_query = get_sql_from_model(
                client=client,
                task_description=obs["task_description"],
                schema=obs["schema"],
                original_query=obs["original_query"],
                last_query=obs.get("last_query"),
                error_message=obs.get("error_message"),
                execution_time_ms=obs.get("execution_time_ms"),
                rows_returned=obs.get("rows_returned"),
                hint=obs.get("hint"),
                step=step,
                history=history,
            )

            step_resp = httpx.post(
                f"{hf_url}/step",
                json={"query": sql_query, "explanation": ""},
                timeout=30
            )
            step_resp.raise_for_status()
            step_data = step_resp.json()

            obs = step_data["observation"]
            reward = float(step_data["reward"])
            done = bool(step_data["done"])
            info = step_data.get("info", {})
            error = obs.get("error_message")

            rewards.append(reward)
            steps_taken = step
            score = float(info.get("best_score", 0.0))

            log_step(
                step=step,
                action=sql_query,
                reward=reward,
                done=done,
                error=error,
            )

            history.append(
                f"Step {step}: score={info.get('score', 0)} reason={info.get('reason', '')}"
            )

            if done:
                break

        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Episode error: {e}", flush=True)

    finally:
        log_end(
            success=success,
            steps=steps_taken,
            score=score,
            rewards=rewards,
        )

    return {"task_id": task_id, "score": score, "success": success, "steps": steps_taken}


if __name__ == "__main__":
    hf_space_url = os.getenv("HF_SPACE_URL", "https://alokrajkumar-sql-query-optimizer.hf.space")

    tasks_to_run = ["task_easy", "task_medium", "task_hard"]
    all_results = []

    for task_id in tasks_to_run:
        result = run_task(task_id, hf_space_url)
        all_results.append(result)

    avg = sum(r["score"] for r in all_results) / len(all_results)
    print(f"\n[SUMMARY] average_score={avg:.3f}", flush=True)
    for r in all_results:
        print(
            f"[SUMMARY] task={r['task_id']} score={r['score']:.3f} success={str(r['success']).lower()}",
            flush=True,
        )
