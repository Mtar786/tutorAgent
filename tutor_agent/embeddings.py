"""Utilities for splitting notes into chunks and computing vector embeddings.

This module provides simple TF‑IDF based embedding functions for
representing text chunks and performing similarity search.  It avoids
external dependencies and network access.  You can replace the
implementation with a more sophisticated model (e.g., Sentence
Transformers) if available.
"""

from __future__ import annotations

import re
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_into_chunks(
    text: str,
    min_length: int = 50,
    max_length: int = 300,
) -> List[str]:
    """Split raw text into chunks of reasonable length.

    The function first splits on blank lines or two consecutive newline
    characters to preserve paragraph boundaries.  If a paragraph
    exceeds ``max_length`` characters it is further split into
    sentences using a simple period‐based heuristic.

    Parameters
    ----------
    text : str
        The raw text (notes or textbook content).
    min_length : int, optional
        Minimum length of a chunk in characters.  Shorter paragraphs are
        merged with neighbouring text when possible.
    max_length : int, optional
        Maximum length of a chunk.  Longer paragraphs are split into
        shorter sentences.

    Returns
    -------
    list of str
        A list of text chunks.
    """
    # Normalize line breaks
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: List[str] = []
    for para in paragraphs:
        if len(para) <= max_length:
            chunks.append(para)
        else:
            # Further split long paragraph into sentences by period
            sentences = re.split(r"(?<=[.!?])\s+", para)
            buf = ""
            for sent in sentences:
                if not sent:
                    continue
                if len(buf) + len(sent) + 1 <= max_length:
                    buf = f"{buf} {sent}".strip()
                else:
                    if buf:
                        chunks.append(buf)
                    buf = sent
            if buf:
                chunks.append(buf)
    # Merge tiny chunks
    merged: List[str] = []
    buf = ""
    for chunk in chunks:
        if len(buf) + len(chunk) + 1 <= max_length and (len(buf) < min_length or len(chunk) < min_length):
            buf = f"{buf} {chunk}".strip()
        else:
            if buf:
                merged.append(buf)
                buf = ""
            merged.append(chunk)
    if buf:
        merged.append(buf)
    return merged


def build_vector_store(chunks: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    """Compute TF‑IDF vectors for a list of chunks.

    Parameters
    ----------
    chunks : list of str
        The text chunks extracted from notes.

    Returns
    -------
    tuple
        A pair ``(vectorizer, matrix)`` where ``vectorizer`` is the
        fitted :class:`TfidfVectorizer` and ``matrix`` is a 2D array of
        shape ``(n_chunks, n_features)`` containing the TF‑IDF vectors.
    """
    # Use a simple tokeniser that keeps words and numbers
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)
    return vectorizer, matrix


def search_similar(
    query: str,
    vectorizer: TfidfVectorizer,
    matrix: np.ndarray,
    top_k: int = 3,
) -> List[int]:
    """Return the indices of the top_k most similar chunks to the query.

    Cosine similarity is computed between the query and each chunk.  The
    highest scoring indices are returned.
    """
    q_vec = vectorizer.transform([query])
    similarities = cosine_similarity(q_vec, matrix).flatten()
    # argsort descending
    idxs = np.argsort(-similarities)
    return idxs[:top_k].tolist()