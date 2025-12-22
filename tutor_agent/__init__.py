"""Tutor Agent package.

This package contains the core logic for the Tutor Agent, an
AI‑assisted study tool that reads notes and quizzes users with
adaptive difficulty.  See the :mod:`tutor_agent.cli` module for the
command line interface.
"""

__all__ = ["QuizSession", "build_vector_store"]

from .quiz import QuizSession  # noqa: F401
from .embeddings import build_vector_store  # noqa: F401