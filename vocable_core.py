"""
Core business logic for the vocabulary trainer.
Shared by both CLI and web interfaces.
"""

import json
import random
import os
from datetime import datetime
from typing import List, Dict, Optional, Any


# Data file constants
FILE_VOCABLES = "vokabeln.json"
FILE_SCORES = "scores.json"
FILE_SESSIONS = "sessions.json"


# Utility functions
def now() -> str:
    """Return current timestamp in German format."""
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def init_scores(scores: Dict[str, Any], vocable_id: int) -> None:
    """Initialize score entry for a vocable if it doesn't exist."""
    if str(vocable_id) not in scores:
        scores[str(vocable_id)] = {
            "score": 0,
            "last_practiced": None,
            "last_correct": None
        }


class DataManager:
    """Handles all JSON file persistence operations."""

    @staticmethod
    def load_vocables() -> List[Dict[str, Any]]:
        """Load vocabulary from JSON file."""
        if not os.path.exists(FILE_VOCABLES):
            return []
        with open(FILE_VOCABLES, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_vocables(vokabeln: List[Dict[str, Any]]) -> None:
        """Save vocabulary to JSON file."""
        with open(FILE_VOCABLES, "w", encoding="utf-8") as f:
            json.dump(vokabeln, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_scores() -> Dict[str, Any]:
        """Load scores from JSON file."""
        if not os.path.exists(FILE_SCORES):
            return {}
        with open(FILE_SCORES, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_scores(scores: Dict[str, Any]) -> None:
        """Save scores to JSON file."""
        with open(FILE_SCORES, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_sessions() -> List[Dict[str, Any]]:
        """Load session history from JSON file."""
        if not os.path.exists(FILE_SESSIONS):
            return []
        with open(FILE_SESSIONS, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_sessions(sessions: List[Dict[str, Any]]) -> None:
        """Save session history to JSON file."""
        with open(FILE_SESSIONS, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=4)


class VocableManager:
    """Manages vocabulary operations."""

    def __init__(self):
        self.data_mgr = DataManager()

    def add_vocable(self, german: str, english: str) -> int:
        """
        Add a new vocabulary entry.

        Args:
            german: German translation
            english: English translation

        Returns:
            The ID of the newly created vocable
        """
        vocables = self.data_mgr.load_vocables()
        scores = self.data_mgr.load_scores()

        # Generate next ID
        next_id = 1 if not vocables else max(v["id"] for v in vocables) + 1

        # Create new vocable
        vocables.append({
            "id": next_id,
            "de": german,
            "en": english
        })

        # Initialize scores
        init_scores(scores, next_id)

        # Save both files
        self.data_mgr.save_vocables(vocables)
        self.data_mgr.save_scores(scores)

        return next_id

    def get_all_vocables(self) -> List[Dict[str, Any]]:
        """Get all vocabulary entries."""
        return self.data_mgr.load_vocables()

    def get_vocable_by_id(self, vocable_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific vocable by ID."""
        vocables = self.data_mgr.load_vocables()
        for v in vocables:
            if v["id"] == vocable_id:
                return v
        return None

    def delete_vocable(self, vocable_id: int) -> bool:
        """
        Delete a vocabulary entry and its scores.

        Args:
            vocable_id: ID of vocable to delete

        Returns:
            True if deleted, False if not found
        """
        vocables = self.data_mgr.load_vocables()
        scores = self.data_mgr.load_scores()

        # Find and remove vocable
        original_len = len(vocables)
        vocables = [v for v in vocables if v["id"] != vocable_id]

        if len(vocables) == original_len:
            return False  # Not found

        # Remove scores entry
        if str(vocable_id) in scores:
            del scores[str(vocable_id)]

        # Save both files
        self.data_mgr.save_vocables(vocables)
        self.data_mgr.save_scores(scores)

        return True


class StatisticsManager:
    """Manages statistics and reporting."""

    def __init__(self):
        self.data_mgr = DataManager()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate vocabulary statistics grouped by score ranges.

        Returns:
            Dictionary with total count and category breakdown with counts and percentages
        """
        vocables = self.data_mgr.load_vocables()
        scores = self.data_mgr.load_scores()

        total = len(vocables)

        # Initialize counters for each category
        categories = {
            "unpracticed": 0,    # score = 0
            "beginner": 0,       # 01-09
            "learning": 0,       # 10-19
            "advanced": 0,       # 20-29
            "good": 0,           # 30-39
            "master": 0          # 40+
        }

        # Count vocables in each category
        for vocable in vocables:
            vocable_id = str(vocable["id"])
            score_data = scores.get(vocable_id, {"score": 0})
            score = score_data.get("score", 0)

            if score == 0:
                categories["unpracticed"] += 1
            elif 1 <= score <= 9:
                categories["beginner"] += 1
            elif 10 <= score <= 19:
                categories["learning"] += 1
            elif 20 <= score <= 29:
                categories["advanced"] += 1
            elif 30 <= score <= 39:
                categories["good"] += 1
            else:  # score >= 40
                categories["master"] += 1

        # Calculate percentages
        stats = {
            "total": total,
            "categories": {}
        }

        for key, count in categories.items():
            percentage = round((count / total * 100)) if total > 0 else 0
            stats["categories"][key] = {
                "count": count,
                "percentage": percentage
            }

        return stats

    def get_vocables_with_scores(self) -> List[Dict[str, Any]]:
        """
        Get all vocables enriched with their score data.

        Returns:
            List of vocables with score, last_practiced, last_correct fields added
        """
        vocables = self.data_mgr.load_vocables()
        scores = self.data_mgr.load_scores()

        result = []
        for v in vocables:
            vocable_id = str(v["id"])
            score_data = scores.get(vocable_id, {
                "score": 0,
                "last_practiced": None,
                "last_correct": None
            })

            enriched = {
                **v,
                "score": score_data.get("score", 0),
                "last_practiced": score_data.get("last_practiced"),
                "last_correct": score_data.get("last_correct")
            }
            result.append(enriched)

        return result

    def get_session_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get quiz session history.

        Args:
            limit: Maximum number of sessions to return (most recent first)

        Returns:
            List of session records
        """
        sessions = self.data_mgr.load_sessions()

        # Return most recent first
        sessions.reverse()

        if limit:
            return sessions[:limit]
        return sessions


def select_vocables_by_priority(vocables: List[Dict[str, Any]],
                                 scores: Dict[str, Any],
                                 count: int) -> List[Dict[str, Any]]:
    """
    Select vocables prioritized by lowest score, oldest last_practiced, then random.

    This is the core spaced repetition algorithm.

    Args:
        vocables: List of all vocabulary items
        scores: Dictionary of scores keyed by vocable ID (as strings)
        count: Number of vocables to select

    Returns:
        List of selected vocables ordered by priority (highest priority first)
    """
    priority_list = []

    for vocable in vocables:
        vocable_id = str(vocable["id"])
        init_scores(scores, vocable["id"])
        score_data = scores[vocable_id]

        score = score_data["score"]
        last_practiced = score_data["last_practiced"]

        # Convert to sortable timestamp
        if last_practiced is None:
            ts = datetime.max  # Never practiced = highest priority
        else:
            ts = datetime.strptime(last_practiced, "%d.%m.%Y %H:%M:%S")

        # Create priority tuple: lower score = higher priority, older date = higher priority
        priority_tuple = (score, ts, random.random(), vocable)
        priority_list.append(priority_tuple)

    # Sort by priority (ascending: lowest score first, oldest practice first)
    priority_list.sort()

    # Select the requested number of vocables (or all if fewer available)
    selected_count = min(count, len(priority_list))
    selected = [item[3] for item in priority_list[:selected_count]]  # Extract vocable from tuple

    return selected


class QuizSession:
    """
    Manages a stateful quiz session.

    This class handles the entire lifecycle of a quiz from selection
    to completion and persistence.
    """

    def __init__(self, count: int):
        """
        Initialize a new quiz session.

        Args:
            count: Number of vocables to practice
        """
        self.data_mgr = DataManager()

        # Load data
        vocables = self.data_mgr.load_vocables()
        self.scores = self.data_mgr.load_scores()

        # Select vocables by priority
        available = len(vocables)
        actual_count = min(count, available)
        self.selected_vocables = select_vocables_by_priority(vocables, self.scores, actual_count)

        # Initialize quiz state
        self.current_index = 0
        self.results = []
        self.current_direction = None
        self.current_vocable = None

        # Prepare first question
        if self.selected_vocables:
            self._prepare_question()

    def _prepare_question(self) -> None:
        """Prepare the current question by selecting direction."""
        if self.current_index < len(self.selected_vocables):
            self.current_vocable = self.selected_vocables[self.current_index]
            self.current_direction = random.choice(["de_en", "en_de"])

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question data.

        Returns:
            Dictionary with question, direction, vocable_id, index, total
            or None if quiz is complete
        """
        if self.is_complete():
            return None

        question_text = (self.current_vocable["de"] if self.current_direction == "de_en"
                        else self.current_vocable["en"])

        return {
            "question": question_text,
            "direction": self.current_direction,
            "vocable_id": self.current_vocable["id"],
            "german": self.current_vocable["de"],
            "english": self.current_vocable["en"],
            "index": self.current_index,
            "total": len(self.selected_vocables)
        }

    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """
        Submit an answer for the current question.

        Args:
            answer: User's answer (string)

        Returns:
            Dictionary with feedback: was_correct, correct_answer, user_answer
        """
        if self.is_complete():
            raise ValueError("Quiz is already complete")

        # Determine correct answer
        correct_answer = (self.current_vocable["en"] if self.current_direction == "de_en"
                         else self.current_vocable["de"])

        # Check if correct
        was_correct = (answer.strip() == correct_answer)

        # Store result
        result = {
            "vocable_id": self.current_vocable["id"],
            "german": self.current_vocable["de"],
            "english": self.current_vocable["en"],
            "direction": self.current_direction,
            "user_answer": answer.strip(),
            "correct_answer": correct_answer,
            "was_correct": was_correct
        }
        self.results.append(result)

        # Return feedback
        return {
            "was_correct": was_correct,
            "correct_answer": correct_answer,
            "user_answer": answer.strip()
        }

    def move_next(self) -> None:
        """Move to the next question."""
        self.current_index += 1
        if not self.is_complete():
            self._prepare_question()

    def is_complete(self) -> bool:
        """Check if the quiz is complete."""
        return self.current_index >= len(self.selected_vocables)

    def get_results(self) -> Dict[str, Any]:
        """
        Get the final quiz results.

        Returns:
            Dictionary with total, correct, and detailed results list
        """
        correct_count = sum(1 for r in self.results if r["was_correct"])

        return {
            "total": len(self.results),
            "correct": correct_count,
            "results": self.results
        }

    def save_session(self) -> None:
        """
        Save the quiz session and update scores.

        This should be called when the quiz is complete.
        """
        if not self.is_complete():
            raise ValueError("Cannot save incomplete quiz session")

        # Update scores based on results
        current_time = now()

        for result in self.results:
            vocable_id = str(result["vocable_id"])
            init_scores(self.scores, result["vocable_id"])

            # Update last_practiced for all vocables
            self.scores[vocable_id]["last_practiced"] = current_time

            # If correct, increment score and update last_correct
            if result["was_correct"]:
                self.scores[vocable_id]["score"] += 1
                self.scores[vocable_id]["last_correct"] = current_time

        # Save updated scores
        self.data_mgr.save_scores(self.scores)

        # Save session data
        sessions = self.data_mgr.load_sessions()
        session = {
            "timestamp": current_time,
            "total": len(self.results),
            "correct": sum(1 for r in self.results if r["was_correct"]),
            "results": self.results
        }
        sessions.append(session)
        self.data_mgr.save_sessions(sessions)
