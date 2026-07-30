from typing import Literal  # <-- FIXED: Imported from native typing library
from pydantic import BaseModel, Field

class JudgeGuardrail(BaseModel):
    # This locks the model into choosing ONLY "yes" or "no"
    careerRelated: Literal["yes", "no"] = Field(
        description="Must be 'yes' if the response talks strictly about career paths, otherwise 'no'."
    )