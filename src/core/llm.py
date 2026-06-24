"""Reusable helpers for calling Claude with structured output via tool use."""
import os
from pathlib import Path
from typing import Type, TypeVar

from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel


# Load .env once when this module is imported.
# Path is relative to the project root, three levels up from this file.
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

# One client, shared across calls.
_client = Anthropic()

# Default model. claude-sonnet-4-6 is the right balance of quality and cost.
DEFAULT_MODEL = "claude-sonnet-4-6"

# Type variable so the return type matches the input model class
T = TypeVar("T", bound=BaseModel)


def structured_call(
    prompt: str,
    response_model: Type[T],
    system: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2000,
) -> T:
    """
    Call Claude and get back a Pydantic-validated structured response.
    
    Args:
        prompt: The user message to send.
        response_model: A Pydantic class describing the shape you want back.
        system: Optional system prompt (sets behavior/context).
        model: Which Claude model to use.
        max_tokens: Upper bound on response length.
    
    Returns:
        An instance of response_model, populated with Claude's response.
    
    Raises:
        ValueError: If Claude doesn't return a tool_use response.
        pydantic.ValidationError: If the returned data doesn't match the schema.
    """
    # Generate the JSON Schema from the Pydantic model.
    schema = response_model.model_json_schema()
    
    # Wrap it as a tool definition for Claude.
    tool_name = _pydantic_to_tool_name(response_model)
    tools = [
        {
            "name": tool_name,
            "description": response_model.__doc__ or "Return the structured response.",
            "input_schema": schema,
        }
    ]
    
    # Make the call. tool_choice forces Claude to call our tool.
    response = _client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        tools=tools,
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Find the tool_use block in the response and extract its input.
    for block in response.content:
        if block.type == "tool_use":
            # block.input is already a dict matching our schema.
            # Pydantic validates it as it constructs the instance.
            return response_model(**block.input)
    
    raise ValueError(
        f"Expected a tool_use response, but got: {[b.type for b in response.content]}"
    )


def _pydantic_to_tool_name(model_class: Type[BaseModel]) -> str:
    """Convert ClassName to snake_case for tool naming. e.g. JobAnalysis -> job_analysis"""
    name = model_class.__name__
    result = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            result.append("_")
        result.append(ch.lower())
    return "".join(result)