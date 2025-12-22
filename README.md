# Tutor Agent

The **Tutor Agent** project is an AI‑assisted study companion that reads
your class notes or textbook and quizzes you with dynamic difficulty
adjustment.  It uses vector embeddings to retrieve relevant content
from your notes, generates quiz questions on the fly, and adapts the
difficulty based on your performance.  This creates a personalized
learning experience that keeps you challenged while identifying gaps
in your understanding.

## Features

### Adaptive quizzes

Adaptive difficulty is a system that adjusts question difficulty in
real‑time based on your answers.  When you answer correctly the next
question becomes harder; if you answer incorrectly the next question
becomes easier【795579226878419†L32-L35】.  Adaptive quizzes provide a
balanced and engaging assessment that pinpoints what you know and where
you need help【795579226878419†L32-L37】.  The Tutor Agent implements a
simple adaptive algorithm: it starts at a medium difficulty level and
updates the difficulty according to your correctness, ensuring
questions stay appropriately challenging.

### Vector embeddings for retrieval

To generate meaningful questions, the agent needs to find the most
relevant passages in your notes.  It uses vector embeddings to
represent each paragraph as a numerical vector in a semantic space,
allowing the agent to measure similarity between your query and the
stored passages【760021047864135†L44-L48】.  Vector embeddings map text
into high‑dimensional arrays where semantically similar content is
clustered together【760021047864135†L67-L75】.  The Tutor Agent uses a
TF‑IDF based embedding (via scikit‑learn) for portability, but you can
swap in your own model (e.g., Sentence Transformers) to improve
semantic retrieval.

### Automated question generation

The agent splits your notes into chunks, retrieves a relevant chunk
based on your current study topic, and generates questions from it.
Questions are created by selecting key sentences and masking important
words or phrases.  A simple fuzzy matching algorithm evaluates your
answers; questions are scored for difficulty based on the length of the
passage they came from.  This heuristic approach avoids external API
calls while still producing varied and meaningful prompts.

### Progress tracking and reports

The CLI keeps track of how many questions you answered correctly,
incorrectly and at each difficulty level.  At the end of a session it
displays a summary report so you can review your progress and focus on
weak areas in future study sessions.

## Installation

1. Clone this repository and create a virtual environment (optional):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

The project depends on `click`, `pandas`, `numpy`, and `scikit-learn` for
vectorization and CLI support.

## Usage

The agent is driven via a command line interface.  To start a quiz
using your notes:

```bash
python -m tutor_agent.cli --notes path/to/your_notes.txt --num-questions 10
```

Key options:

* `--notes`: Path to a text file containing your notes or textbook
  content.  The agent splits the file into paragraphs.
* `--num-questions`: Number of questions to ask in this session (default: 5).
* `--topic`: Optional keyword or phrase to focus on.  The agent uses
  vector search to pick passages related to your topic.
* `--min-chunk-length` / `--max-chunk-length`: Control how the notes
  are split into chunks.
* `--quiet`: Suppress progress output.

After each question, the agent tells you whether you were correct and
adjusts the difficulty accordingly.  At the end of the quiz you’ll see
a summary of your performance.

## Example

Suppose your notes contain the following text:

```
Newton’s first law states that an object at rest stays at rest and an
object in motion stays in motion with the same speed and in the same
direction unless acted upon by an unbalanced force.  Newton’s second
law relates the net force on an object to its mass and acceleration.
Finally, Newton’s third law says that for every action there is an equal
and opposite reaction.
```

Running the agent:

```bash
python -m tutor_agent.cli --notes physics.txt --num-questions 3
```

The agent will retrieve passages, generate questions (e.g., “What does
Newton’s third law state?”), evaluate your answers, and adjust
difficulty as you progress.

## Limitations and future work

The current implementation uses a simple TF‑IDF embedding and a basic
heuristic for question generation.  It does not cover open‑ended
concepts or provide context beyond the selected chunk.  In the future
it could be extended to use true semantic embeddings, integrate with
language models to generate more varied questions and explanations, and
support spaced repetition schedules.

## References

* **Adaptive quizzes** – Adaptive quiz difficulty scaling adjusts
  question difficulty in real time based on the learner’s answers,
  getting harder after correct responses and easier after
  incorrect ones【795579226878419†L32-L35】.  Adaptive systems
  personalize assessments and can identify knowledge gaps【795579226878419†L32-L37】.
* **Vector embeddings** – Embeddings convert complex data (like text)
  into numerical vectors in a semantic space, allowing similarity
  search【760021047864135†L44-L48】.  They map semantically similar
  items close together【760021047864135†L67-L75】, enabling the agent
  to retrieve relevant passages from your notes.