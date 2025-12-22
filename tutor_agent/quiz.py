"""Quiz generation and adaptive difficulty logic for Tutor Agent."""

from __future__ import annotations

import difflib
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .embeddings import split_into_chunks


@dataclass
class Question:
    """Represents a single quiz question."""
    text: str
    answer: str
    difficulty: int  # 0=easy, 1=medium, 2=hard


class QuizSession:
    """Manage a quiz session with adaptive difficulty."""

    def __init__(
        self,
        notes: str,
        topic: Optional[str] = None,
        min_chunk_length: int = 50,
        max_chunk_length: int = 300,
    ) -> None:
        """Initialize the session.

        Parameters
        ----------
        notes : str
            The raw text content of your notes or textbook.
        topic : str, optional
            A keyword or phrase to focus on.  If provided, only chunks
            containing this keyword will be used.
        min_chunk_length : int
            Minimum length of a text chunk in characters.
        max_chunk_length : int
            Maximum length of a text chunk in characters.
        """
        self.raw_notes = notes
        self.topic = topic
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
        self.questions_by_level: Dict[int, List[Question]] = {0: [], 1: [], 2: []}
        self.current_level = 1  # start at medium
        self.correct_count = 0
        self.incorrect_count = 0
        self._prepare_questions()

    def _prepare_questions(self) -> None:
        """Split notes into chunks and generate questions for each chunk."""
        chunks = split_into_chunks(
            self.raw_notes,
            min_length=self.min_chunk_length,
            max_length=self.max_chunk_length,
        )
        for chunk in chunks:
            if self.topic and self.topic.lower() not in chunk.lower():
                continue
            q = self._generate_question_from_chunk(chunk)
            if q is None:
                continue
            question_text, answer_text, diff_score = q
            diff_level = self._difficulty_from_length(diff_score)
            self.questions_by_level[diff_level].append(
                Question(text=question_text, answer=answer_text, difficulty=diff_level)
            )
        # Shuffle questions within each level
        for level in self.questions_by_level:
            random.shuffle(self.questions_by_level[level])

    @staticmethod
    def _generate_question_from_chunk(self_chunk: str) -> Optional[Tuple[str, str, int]]:
        """Generate a simple Q/A pair from a text chunk.

        This heuristic selects the longest sentence in the chunk and
        constructs a question about its most distinctive word.
        Returns ``None`` if no suitable sentence is found.
        """
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", self_chunk)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return None
        # Choose the longest sentence
        sentence = max(sentences, key=len)
        # Choose a keyword: pick the longest alphanumeric word >4 chars
        words = [re.sub(r"[^A-Za-z0-9]", "", w) for w in sentence.split()]
        words = [w for w in words if w]
        if not words:
            return None
        keyword = max(words, key=len)
        # Build question
        question = f"What does the term '{keyword}' refer to in this context?"
        answer = sentence.strip()
        diff_score = len(self_chunk.split())
        return question, answer, diff_score

    @staticmethod
    def _difficulty_from_length(word_count: int) -> int:
        """Map a chunk's word count to a difficulty level."""
        if word_count <= 40:
            return 0  # easy
        if word_count <= 100:
            return 1  # medium
        return 2  # hard

    def ask(self, num_questions: int = 5, quiet: bool = False) -> None:
        """Run an interactive quiz session.

        Parameters
        ----------
        num_questions : int, optional
            Number of questions to ask.  If there are fewer
            available questions at a given difficulty level, the
            session may end early.
        quiet : bool, optional
            If ``True`` progress messages are suppressed.
        """
        for i in range(num_questions):
            # If no questions left at current level, move to next available level
            if not self.questions_by_level[self.current_level]:
                # find any remaining questions
                remaining_levels = [lvl for lvl, qs in self.questions_by_level.items() if qs]
                if not remaining_levels:
                    if not quiet:
                        print("No more questions available.")
                    break
                # pick level with most questions
                self.current_level = max(remaining_levels, key=lambda l: len(self.questions_by_level[l]))
            q = self.questions_by_level[self.current_level].pop()
            if not quiet:
                print(f"\nQuestion {i+1}/{num_questions} (level {self.current_level}):")
                print(q.text)
            user_answer = input("Your answer: ")
            if self._check_answer(user_answer, q.answer):
                if not quiet:
                    print("Correct!")
                self.correct_count += 1
                # Increase difficulty if possible
                if self.current_level < 2:
                    self.current_level += 1
            else:
                if not quiet:
                    print(f"Incorrect. Correct answer: {q.answer}")
                self.incorrect_count += 1
                # Decrease difficulty if possible
                if self.current_level > 0:
                    self.current_level -= 1
        if not quiet:
            self._print_summary(num_questions)

    @staticmethod
    def _check_answer(user: str, correct: str) -> bool:
        """Return True if the user answer matches the correct answer fuzzily."""
        user_norm = user.strip().lower()
        correct_norm = correct.strip().lower()
        if not user_norm or not correct_norm:
            return False
        # compute similarity based on SequenceMatcher ratio
        ratio = difflib.SequenceMatcher(None, user_norm, correct_norm).ratio()
        return ratio >= 0.6

    def _print_summary(self, num_questions: int) -> None:
        """Print a summary of the user's performance."""
        total_answered = self.correct_count + self.incorrect_count
        print("\nQuiz complete!")
        print(f"Questions attempted: {total_answered}")
        print(f"Correct answers:   {self.correct_count}")
        print(f"Incorrect answers: {self.incorrect_count}")
        if total_answered:
            accuracy = 100 * self.correct_count / total_answered
            print(f"Accuracy:         {accuracy:.1f}%")