class ReviewError(Exception):
    """Base exception for ai_pr_review errors."""


class ConfigurationError(ReviewError):
    """Raised when environment configuration is invalid."""


class GitHubError(ReviewError):
    """Raised when GitHub operations fail."""


class RepoError(ReviewError):
    """Raised for local repository operation failures."""
