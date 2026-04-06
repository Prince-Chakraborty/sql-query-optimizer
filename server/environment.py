import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from models import SQLAction, SQLObservation, EpisodeState
from tasks import get_task, run_query, SCHEMA_DESCRIPTION
from graders import grade


class SQLOptimizerEnvironment:
    def __init__(self):
        self.episode_id: str = ""
        self.task_id: str = ""
        self.step_count: int = 0
        self.done: bool = False
        self.total_reward: float = 0.0
        self.best_score: float = 0.0
        self.current_task: dict = {}
        self.last_query: Optional[str] = None
        self.last_error: Optional[str] = None
        self.last_execution_time: Optional[float] = None
        self.last_rows: Optional[int] = None

    def reset(self, task_id: str = "task_easy") -> SQLObservation:
        self.episode_id = str(uuid.uuid4())
        self.task_id = task_id
        self.step_count = 0
        self.done = False
        self.total_reward = 0.0
        self.best_score = 0.0
        self.last_query = None
        self.last_error = None
        self.last_execution_time = None
        self.last_rows = None
        self.current_task = get_task(task_id)

        return SQLObservation(
            task_description=self.current_task["task_description"],
            original_query=self.current_task["original_query"],
            db_schema=SCHEMA_DESCRIPTION,
            error_message=None,
            last_query=None,
            execution_time_ms=None,
            rows_returned=None,
            step_number=0,
            max_steps=self.current_task["max_steps"],
            hint=self.current_task.get("hint"),
        )

    def step(self, action: SQLAction) -> dict:
        if self.done:
            raise RuntimeError("Episode is done. Call reset() first.")

        self.step_count += 1
        query = action.query.strip()
        self.last_query = query

        rows, error, time_ms = run_query(query)
        self.last_error = error
        self.last_execution_time = time_ms
        self.last_rows = len(rows) if rows else 0

        result = grade(self.task_id, query)
        score = result["score"]
        reason = result["reason"]

        reward = max(0.0, score - self.best_score)
        if score > self.best_score:
            self.best_score = score

        if error:
            reward = -0.05

        self.total_reward += reward

        max_steps = self.current_task["max_steps"]
        if score >= 1.0 or self.step_count >= max_steps:
            self.done = True

        observation = SQLObservation(
            task_description=self.current_task["task_description"],
            original_query=self.current_task["original_query"],
            db_schema=SCHEMA_DESCRIPTION,
            error_message=error,
            last_query=query,
            execution_time_ms=time_ms,
            rows_returned=self.last_rows,
            step_number=self.step_count,
            max_steps=max_steps,
            hint=self.current_task.get("hint") if score < 0.5 else None,
        )

        return {
            "observation": observation,
            "reward": round(reward, 4),
            "done": self.done,
            "info": {
                "score": score,
                "reason": reason,
                "best_score": self.best_score,
                "step": self.step_count,
                "error": error,
            }
        }

    def state(self) -> EpisodeState:
        return EpisodeState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            task_id=self.task_id,
            task_difficulty=self.current_task.get("difficulty", "unknown"),
            done=self.done,
            total_reward=round(self.total_reward, 4),
            best_score=round(self.best_score, 4),
        )
