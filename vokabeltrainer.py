import json
import random
import os
from datetime import datetime

FILE_VOCABLES = "vokabeln.json"
FILE_SCORES = "scores.json"
FILE_SESSIONS = "sessions.json"


def load_vocables():
    if not os.path.exists(FILE_VOCABLES):
        return []
    with open(FILE_VOCABLES, "r", encoding="utf-8") as f:
        return json.load(f)


def save_vocables(vokabeln):
    with open(FILE_VOCABLES, "w", encoding="utf-8") as f:
        json.dump(vokabeln, f, ensure_ascii=False, indent=4)


def load_scores():
    if not os.path.exists(FILE_SCORES):
        return {}
    with open(FILE_SCORES, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scores(scores):
    with open(FILE_SCORES, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)


def load_sessions():
    if not os.path.exists(FILE_SESSIONS):
        return []
    with open(FILE_SESSIONS, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sessions(sessions):
    with open(FILE_SESSIONS, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=4)


def now():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def init_scores(scores, vocable_id):
    """If scores is empty, initialize it with the current date and time."""
    if str(vocable_id) not in scores:
        scores[str(vocable_id)] = {
            "score": 0,
            "last_practiced": None,
            "last_correct": None
        }


def add_vocables(vocables, scores):
    print("Vokabeln hinzufügen (leere Eingabe bei 'english' zum Beenden)\n")

    while True:
        english = input("english: ").strip()

        if not english:
            print("Vokabeln hinzufügen beendet.\n")
            break

        german = input("deutsch: ").strip()

        if not german:
            print("Vokabeln hinzufügen beendet.\n")
            break

        next_id = 1 if not vocables else max(v["id"] for v in vocables) + 1

        vocables.append({
            "id": next_id,
            "de": german,
            "en": english
        })

        init_scores(scores, next_id)

        save_vocables(vocables)
        save_scores(scores)

        print("✓ Vokabeln hinzugefügt!\n")


def show_vocables(vocables, scores):
    for v in vocables:
        s = scores.get(str(v["id"]), {})
        print(
            f"{v['de']} – {v['en']} "
            f"| Score: {s.get('score', 0)} "
            f"| Geübt: {s.get('last_practiced')} "
            f"| Richtig: {s.get('last_correct')}"
        )
    print()


def calculate_statistics():
    """
    Calculate vocabulary statistics grouped by score ranges.

    Returns:
        Dictionary with total count and category breakdown with counts and percentages
    """
    vocables = load_vocables()
    scores = load_scores()

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
        else:  # score > 40
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


def display_statistics_ascii(stats):
    """
    Display vocabulary statistics as ASCII art with progress bars.

    Args:
        stats: Dictionary with total and categories (from calculate_statistics())
    """
    total = stats["total"]

    # Handle empty database
    if total == 0:
        print("╔════════════════════════════════════════╗")
        print("║     Keine Vokabeln vorhanden          ║")
        print("╚════════════════════════════════════════╝")
        print()
        return

    # Find the maximum count for scaling bars
    max_count = max(cat["count"] for cat in stats["categories"].values())
    bar_width = 10  # Number of characters for full bar

    # Category labels in German
    labels = {
        "unpracticed": "Nicht geübt (0):",
        "beginner": "Anfänger (01-09):",
        "learning": "Lernend (10-19):",
        "advanced": "Fortgeschritten (20-29):",
        "good": "Gut (30-39):",
        "master": "Meister (40+):"
    }

    # Print header
    print()
    print("╔════════════════════════════════════════════════════════╗")
    title = f"Vokabeln Statistik (Total: {total})"
    padding = (56 - len(title)) // 2
    print(f"║{' ' * padding}{title}{' ' * (56 - len(title) - padding)}║")
    print("╠════════════════════════════════════════════════════════╣")

    # Print each category
    category_order = ["unpracticed", "beginner", "learning", "advanced", "good", "master"]
    for key in category_order:
        cat_data = stats["categories"][key]
        count = cat_data["count"]
        percentage = cat_data["percentage"]

        # Calculate bar length (scale to max_count)
        if max_count > 0:
            filled = round((count / max_count) * bar_width)
        else:
            filled = 0
        empty = bar_width - filled

        # Create progress bar
        bar = "█" * filled + "░" * empty

        # Format label with padding
        label = labels[key]

        # Print the line with proper formatting
        stats_str = f"{count:3d} ({percentage:3d}%)"
        print(f"║ {label:26s} [{bar}] {stats_str:9s}     ║")

    print("╚════════════════════════════════════════════════════════╝")
    print()


def select_vocables_by_priority(vocables, scores, count):
    """
    Select vocables prioritized by lowest score, oldest last_practiced, then random.

    Args:
        vocables: List of all vocabulary items
        scores: Dictionary of scores keyed by vocable ID
        count: Number of vocables to select

    Returns:
        List of selected vocables ordered by priority
    """
    priority_list = []

    for vocable in vocables:
        vocable_id = str(vocable["id"])
        init_scores(scores, vocable_id)
        score_data = scores[vocable_id]

        score = score_data["score"]
        last_practiced = score_data["last_practiced"]

        # Convert to sortable timestamp
        if last_practiced is None:
            ts = datetime.max  # Never practiced = lowest priority
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


def run_quiz_round(vocables, scores, selected_vocables):
    """
    Run a complete quiz round with multiple vocables.

    Args:
        vocables: List of all vocabulary items (for reference)
        scores: Dictionary to update with results
        selected_vocables: List of vocables to quiz (pre-sorted by priority)

    Returns:
        Dictionary with quiz results including total, correct count, and detailed results
    """
    results = {
        "total": 0,
        "correct": 0,
        "results": []
    }

    total_questions = len(selected_vocables)

    for idx, vocable in enumerate(selected_vocables, 1):
        vocable_id = vocable["id"]
        direction = random.choice(["de_en", "en_de"])

        print(f"\nFrage {idx}/{total_questions}")

        if direction == "de_en":
            response = input(f"Was heißt '{vocable['de']}' auf Englisch? ").strip()
            correct_answer = vocable["en"]
        else:
            response = input(f"Was heißt '{vocable['en']}' auf Deutsch? ").strip()
            correct_answer = vocable["de"]

        was_correct = (response == correct_answer)

        # Store detailed result
        result = {
            "vocable_id": vocable_id,
            "german": vocable["de"],
            "english": vocable["en"],
            "direction": direction,
            "user_answer": response,
            "correct_answer": correct_answer,
            "was_correct": was_correct
        }
        results["results"].append(result)

        # Update counters
        results["total"] += 1
        if was_correct:
            results["correct"] += 1
            print("✓ Richtig!")
        else:
            print(f"✗ Falsch! Richtige Antwort: {correct_answer}")

    return results


def update_scores_from_results(scores, results):
    """
    Update scores and timestamps based on quiz round results.

    Args:
        scores: Current scores dictionary
        results: Results from run_quiz_round()

    Returns:
        Updated scores dictionary
    """
    current_time = now()

    for result in results["results"]:
        vocable_id = str(result["vocable_id"])
        init_scores(scores, vocable_id)

        # Update last_practiced for all vocables
        scores[vocable_id]["last_practiced"] = current_time

        # If correct, increment score and update last_correct
        if result["was_correct"]:
            scores[vocable_id]["score"] += 1
            scores[vocable_id]["last_correct"] = current_time

    return scores


def display_quiz_results(results):
    """
    Display detailed quiz round statistics.

    Args:
        results: Results dictionary from run_quiz_round()
    """
    print("\n" + "=" * 50)
    print("Quiz abgeschlossen!")
    print("=" * 50)
    print(f"Ergebnis: {results['correct']}/{results['total']} richtig\n")

    # Show correct answers
    correct_results = [r for r in results["results"] if r["was_correct"]]
    if correct_results:
        print("✓ Richtige Antworten:")
        for r in correct_results:
            print(f"  • {r['german']} - {r['english']}")
        print()

    # Show incorrect answers with details
    incorrect_results = [r for r in results["results"] if not r["was_correct"]]
    if incorrect_results:
        print("✗ Falsche Antworten:")
        for r in incorrect_results:
            print(f"  • {r['german']} - {r['english']}")
            print(f"    Deine Antwort: {r['user_answer']}")
            print(f"    Richtig wäre: {r['correct_answer']}")
        print()


def quiz(vocables, scores):
    """Run a prioritized quiz round with multiple vocables."""
    if not vocables:
        print("Keine Vokabeln vorhanden.\n")
        return

    # Prompt user for number of vocables to practice
    try:
        count_input = input("Wie viele Vokabeln möchtest du üben? ").strip()
        count = int(count_input)
        if count <= 0:
            print("Bitte gib eine positive Zahl ein.\n")
            return
    except ValueError:
        print("Ungültige Eingabe. Bitte gib eine Zahl ein.\n")
        return

    # Check if fewer vocables available than requested
    available = len(vocables)
    if count > available:
        print(f"Es sind nur {available} Vokabeln vorhanden. Alle werden geübt.\n")
        count = available

    # Select vocables by priority
    selected_vocables = select_vocables_by_priority(vocables, scores, count)

    # Run the quiz round
    results = run_quiz_round(vocables, scores, selected_vocables)

    # Update scores based on results
    update_scores_from_results(scores, results)

    # Save updated scores
    save_scores(scores)

    # Save session data
    sessions = load_sessions()
    session = {
        "timestamp": now(),
        "total": results["total"],
        "correct": results["correct"],
        "results": results["results"]
    }
    sessions.append(session)
    save_sessions(sessions)

    # Display detailed results
    display_quiz_results(results)


def menu():
    vocables = load_vocables()
    scores = load_scores()

    while True:
        # Display statistics
        stats = calculate_statistics()
        display_statistics_ascii(stats)

        print("----- Vokabeltrainer -----")
        print("1) Vokabeln hinzufügen")
        print("2) Quiz starten")
        print("3) Alle Vokabeln anzeigen")
        print("4) beenden")

        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            add_vocables(vocables, scores)
        elif auswahl == "2":
            quiz(vocables, scores)
        elif auswahl == "3":
            show_vocables(vocables, scores)
        elif auswahl == "4":
            print("Bis Bald!")
            break
        else:
            print("Ungültige auswahl.\n")


if __name__ == "__main__":
    menu()
