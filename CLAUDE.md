# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a German-English vocabulary trainer (Vokabeltrainer) - a simple command-line application for learning vocabulary through quizzes. The application is a single-file Python script with JSON-based data persistence.

## Project Configuration

This project uses `pyproject.toml` for configuration and metadata:
- Build system: setuptools (PEP 517/518 compliant)
- Entry point: `vokabeltrainer` command after installation
- Tool configurations for black, ruff, and mypy

## Development Setup

**Install in development mode:**
```bash
pip install -e .
```

**Run directly without installation:**
```bash
python3 vokabeltrainer.py
```

The application presents an interactive menu with options to:
1. Add vocabulary (German-English pairs)
2. Start a quiz (random vocabulary in random direction)
3. View all vocabulary with scores
4. Exit

## Data Files

The application uses two JSON files for persistence:

- **vokabeln.json**: Stores vocabulary entries with structure `{"id": int, "de": string, "en": string}`
- **scores.json**: Tracks learning progress keyed by vocabulary ID with structure:
  ```json
  {
    "vocable_id": {
      "score": int,
      "last_practiced": "DD.MM.YYYY HH:MM:SS",
      "last_correct": "DD.MM.YYYY HH:MM:SS"
    }
  }
  ```

Both files are created automatically if they don't exist. Vocabulary IDs are auto-incremented integers.

## Architecture

This is a simple procedural application with:
- **Data layer**: JSON load/save functions for vocables and scores
- **Business logic**: Functions for adding vocables, quizzing, and displaying results
- **UI layer**: Console-based menu loop with German language prompts

The quiz logic randomly selects both the vocabulary item and the translation direction (German→English or English→German). Scores increment on correct answers and track timestamps for practice and correctness.

## Key Implementation Details

- Vocabulary IDs are stored as strings in scores.json (due to JSON key constraints) but as integers in vokabeln.json
- The application uses exact string matching for quiz answers (case-sensitive)
- Timestamps use German date format: DD.MM.YYYY HH:MM:SS
- UTF-8 encoding is used throughout for German characters
