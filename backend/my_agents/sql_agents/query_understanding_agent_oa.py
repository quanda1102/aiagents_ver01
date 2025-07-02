from __future__ import annotations


import asyncio
import json
from typing import List, Optional

from agents import Agent, Runner, ModelSettings
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. Define the structured output of the agent using `pydantic`.
# ---------------------------------------------------------------------------

class QueryUnderstandingOutput(BaseModel):
    """Structured output describing the user query."""

    intent: Optional[str] = Field(None, description="High-level intent of the question")
    entities: List[str] = Field(default_factory=list, description="Entities mentioned in the question")


# ---------------------------------------------------------------------------
# 2. Create the agent, give it instructions, an output type and model.
# ---------------------------------------------------------------------------

QUERY_UNDERSTANDING_AGENT = Agent(
    name="QueryUnderstandingAgent",
    instructions=(
        "Bạn là một agent hiểu ngữ nghĩa câu hỏi. Dựa trên câu hỏi của người dùng, "
        "hãy trích xuất *intent* (mục đích chính) và danh sách *entities* (các thực thể được nhắc tới)."
        "\n\nTrả lời duy nhất bằng JSON khớp với schema sau:\n{\n  \"intent\": string | null,\n  \"entities\": string[]\n}"
    ),
    output_type=QueryUnderstandingOutput,  # The SDK will validate LLM output against this schema.
    model="gpt-4o-mini",
)


# ---------------------------------------------------------------------------
# 3. Run the agent
# ---------------------------------------------------------------------------

async def analyze_question(question: str) -> QueryUnderstandingOutput:
    """Run the agent asynchronously and get structured understanding back."""

    # `Runner.run` kicks off the agent loop until a final structured output is returned.
    result = await Runner.run(QUERY_UNDERSTANDING_AGENT, question)

    # `final_output_as` casts and validates against the declared `output_type`.
    return result.final_output_as(QueryUnderstandingOutput)


# ---------------------------------------------------------------------------
# 4.  Testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    q = "Thông tin doanh thu quý vừa rồi của Samsung là bao nhiêu?"

    async def _main():
        output = await analyze_question(q)
        # Pretty-print as JSON so it is easy to inspect.
        print(json.dumps(output.model_dump(), ensure_ascii=False, indent=2))

    asyncio.run(_main()) 