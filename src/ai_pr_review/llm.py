from __future__ import annotations

import os
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI

from .errors import ConfigurationError

# Load environment variables
load_dotenv()


def _get_openai_api_key() -> str:
    """Return the OpenAI API key from the environment or raise an error."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ConfigurationError('OPENAI_API_KEY environment variable not set.')
    return api_key


def setup_openai_client() -> OpenAI:
    """Set up and return OpenAI client."""
    api_key = _get_openai_api_key()
    return OpenAI(api_key=api_key)


def create_review_prompts(
    pr_title: str, pr_description: str, context_blob: str
) -> tuple[str, str]:
    """Create system and user prompts for review."""
    system_prompt = (
        'You are an expert software engineer performing a pull request review. '
        'Focus on correctness, clarity, potential bugs, adherence to best practices, '
        'and areas for improvement. Be concise and actionable.'
    )

    user_prompt = (
        f'Please review the following pull request.\n\n'
        f'PR Title: {pr_title}\n'
        f'PR Description:\n{pr_description or "No description provided."}\n\n'
        f'Context (Diff, changed files, and relevant symbols):\n'
        f'```\n{context_blob}\n```\n\n'
        f'Provide your review:'
    )

    return system_prompt, user_prompt


def generate_review(
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    model: str = 'gpt-4.1',
    temperature: float = 0.2,
    max_tokens: int = 2000,
) -> str:
    """Generate review using LLM."""
    llm_response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = llm_response.choices[0].message.content
    return cast(str, content)


def review_with_llm(
    pr_title: str,
    pr_description: str,
    context_blob: str,
    model: str = 'gpt-4.1',
    temperature: float = 0.2,
    max_tokens: int = 2000,
) -> str:
    """Full process to generate a review using LLM."""
    # Set up OpenAI client
    client = setup_openai_client()

    # Create prompts
    system_prompt, user_prompt = create_review_prompts(
        pr_title, pr_description, context_blob
    )

    # Generate and return review
    return generate_review(
        client,
        system_prompt,
        user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
