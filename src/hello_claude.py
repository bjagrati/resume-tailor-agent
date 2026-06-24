"""Smoke test: prove our API key works and we can talk to Claude."""
import os
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

# Load .env from the project root (two levels up from this file)
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)

# Verify the key loaded
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit(
        f"❌ ANTHROPIC_API_KEY not found. Looked in: {ENV_PATH}\n"
        "Make sure .env exists at the project root with the key set."
    )
print(f"✓ API key loaded (starts with {api_key[:12]}...)")

# Make the simplest possible API call
client = Anthropic(api_key=api_key)

print("\nCalling Claude...")
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence, and tell me what model you are.",
        }
    ],
)

# Extract and print the response
reply = response.content[0].text
print(f"\nClaude's response:\n{reply}")

# Show usage so we know what we just spent
usage = response.usage
print(f"\nUsage: {usage.input_tokens} input tokens, {usage.output_tokens} output tokens")