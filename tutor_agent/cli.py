"""Command line interface for Tutor Agent."""

from __future__ import annotations

import click

from .quiz import QuizSession


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--notes",
    "notes_path",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
    required=True,
    help="Path to the text file containing your class notes or textbook.",
)
@click.option(
    "--num-questions",
    default=5,
    show_default=True,
    type=int,
    help="Number of questions to ask during the session.",
)
@click.option(
    "--topic",
    default=None,
    type=str,
    help="Optional keyword or phrase to focus on.  Only chunks containing this keyword will be used.",
)
@click.option(
    "--min-chunk-length",
    default=50,
    show_default=True,
    type=int,
    help="Minimum length of a text chunk in characters.",
)
@click.option(
    "--max-chunk-length",
    default=300,
    show_default=True,
    type=int,
    help="Maximum length of a text chunk in characters.",
)
@click.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Suppress progress messages and show only the quiz questions and summary.",
)
def main(
    notes_path: str,
    num_questions: int,
    topic: str | None,
    min_chunk_length: int,
    max_chunk_length: int,
    quiet: bool,
) -> None:
    """Run the Tutor Agent quiz on your notes."""
    with open(notes_path, "r", encoding="utf-8") as f:
        text = f.read()
    session = QuizSession(
        notes=text,
        topic=topic,
        min_chunk_length=min_chunk_length,
        max_chunk_length=max_chunk_length,
    )
    session.ask(num_questions=num_questions, quiet=quiet)


if __name__ == "__main__":  # pragma: no cover
    main()