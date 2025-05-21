"""Tests for the LLM module."""

from unittest.mock import MagicMock, patch

import pytest
from openai import OpenAI

from ai_pr_review.llm import (
    create_review_prompts,
    generate_review,
    review_with_llm,
    setup_openai_client,
)


@pytest.fixture
def mock_openai_client():
    """Provide a mocked OpenAI client."""
    client = MagicMock(spec=OpenAI)
    return client


def test_setup_openai_client():
    """Test setting up OpenAI client."""
    with patch('ai_pr_review.llm.OpenAI') as mock_openai:
        setup_openai_client()
        mock_openai.assert_called_once()
        # Verify API key is passed
        assert mock_openai.call_args[1]['api_key'] is not None


def test_create_review_prompts():
    """Test creating review prompts."""
    pr_title = 'Test PR'
    pr_description = 'This is a test PR description'
    context_blob = 'diff content and file contexts'

    system_prompt, user_prompt = create_review_prompts(
        pr_title, pr_description, context_blob
    )

    # Check system prompt
    assert 'expert software engineer' in system_prompt
    assert 'pull request review' in system_prompt

    # Check user prompt
    assert pr_title in user_prompt
    assert pr_description in user_prompt
    assert context_blob in user_prompt


def test_create_review_prompts_no_description():
    """Test creating review prompts with no description."""
    pr_title = 'Test PR'
    pr_description = None
    context_blob = 'diff content'

    system_prompt, user_prompt = create_review_prompts(
        pr_title, pr_description, context_blob
    )

    # Check user prompt handles None
    assert 'No description provided' in user_prompt


def test_generate_review(mock_openai_client):
    """Test generating review from LLM."""
    # Setup mocks
    response = MagicMock()
    message = MagicMock()
    message.content = 'This is the review content'
    response.choices = [MagicMock(message=message)]
    mock_openai_client.chat.completions.create.return_value = response

    # Test function
    system_prompt = 'You are a reviewer'
    user_prompt = 'Review this PR'

    result = generate_review(
        mock_openai_client,
        system_prompt,
        user_prompt,
        model='test-model',
        temperature=0.5,
        max_tokens=1000,
    )

    # Assertions
    mock_openai_client.chat.completions.create.assert_called_once()
    create_call = mock_openai_client.chat.completions.create
    call_args = create_call.call_args[1]
    assert call_args['model'] == 'test-model'
    assert call_args['temperature'] == 0.5
    assert call_args['max_tokens'] == 1000
    assert call_args['messages'][0]['role'] == 'system'
    assert call_args['messages'][0]['content'] == system_prompt
    assert call_args['messages'][1]['role'] == 'user'
    assert call_args['messages'][1]['content'] == user_prompt
    assert result == 'This is the review content'


def test_review_with_llm():
    """Test the complete LLM review workflow."""
    with (
        patch('ai_pr_review.llm.setup_openai_client') as mock_setup,
        patch('ai_pr_review.llm.create_review_prompts') as mock_prompts,
        patch('ai_pr_review.llm.generate_review') as mock_generate,
    ):
        # Setup mocks
        mock_client = MagicMock()
        mock_setup.return_value = mock_client
        mock_prompts.return_value = ('system prompt', 'user prompt')
        mock_generate.return_value = 'review content'

        # Test function
        pr_title = 'Test PR'
        pr_description = 'Description'
        context_blob = 'context'

        result = review_with_llm(
            pr_title,
            pr_description,
            context_blob,
            model='test-model',
            temperature=0.3,
            max_tokens=1500,
        )

        # Assertions
        mock_setup.assert_called_once()
        mock_prompts.assert_called_once_with(pr_title, pr_description, context_blob)
        mock_generate.assert_called_once_with(
            mock_client,
            'system prompt',
            'user prompt',
            model='test-model',
            temperature=0.3,
            max_tokens=1500,
        )
        assert result == 'review content'
