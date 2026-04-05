from pydantic import BaseModel, Field
from typing import Optional, List


class SQLAction(BaseModel):
    """Action taken by the agent - submit an optimized SQL query."""
    query: str = Field(description="The SQL query submitted by the agent")
    explanation: str = Field(
        default="",
        description="Agent explanation of what was changed and why"
    )


class SQLObservation(BaseModel):
    """Observation returned to the agent."""
    task_description: str = Field(description="What the agent needs to fix or optimize")
    original_query: str = Field(description="The original broken or slow SQL query")
    schema: str = Field(description="Database schema the query runs against")
    error_message: Optional[str] = Field(
        default=None,
        description="Error from last query attempt if any"
    )
    last_query: Optional[str] = Field(
        default=None,
        description="The last query the agent submitted"
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Execution time of last query in milliseconds"
    )
    rows_returned: Optional[int] = Field(
        default=None,
        description="Number of rows returned by last query"
    )
    step_number: int = Field(description="Current step number")
    max_steps: int = Field(description="Maximum steps allowed")
    hint: Optional[str] = Field(
        default=None,
        description="Optional hint for the agent"
    )


class SQLReward(BaseModel):
    """Reward signal for the agent."""
    score: float = Field(description="Reward score between 0.0 and 1.0")
    reason: str = Field(description="Explanation of the reward")
    syntax_correct: bool = Field(default=False)
    results_correct: bool = Field(default=False)
    performance_improved: bool = Field(default=False)


class EpisodeState(BaseModel):
    """Episode metadata."""
    episode_id: str
    step_count: int
    task_id: str
    task_difficulty: str
    done: bool
    total_reward: float
    best_score: float
