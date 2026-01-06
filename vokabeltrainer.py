"""CLI interface for the vocabulary trainer."""

from vocable_core import (
    VocableManager,
    QuizSession,
    StatisticsManager,
    DataManager
)


def add_vocables():
    """CLI interface for adding vocabulary."""
    print("Vokabeln hinzufügen (leere Eingabe bei 'english' zum Beenden)\n")

    vocab_mgr = VocableManager()

    while True:
        english = input("english: ").strip()

        if not english:
            print("Vokabeln hinzufügen beendet.\n")
            break

        german = input("deutsch: ").strip()

        if not german:
            print("Vokabeln hinzufügen beendet.\n")
            break

        vocab_mgr.add_vocable(german, english)
        print("✓ Vokabeln hinzugefügt!\n")


def show_vocables():
    """CLI interface for displaying all vocabulary."""
    stats_mgr = StatisticsManager()
    vocables = stats_mgr.get_vocables_with_scores()

    for v in vocables:
        print(
            f"{v['de']} – {v['en']} "
            f"| Score: {v.get('score', 0)} "
            f"| Geübt: {v.get('last_practiced')} "
            f"| Richtig: {v.get('last_correct')}"
        )
    print()


def calculate_statistics():
    """
    Calculate vocabulary statistics grouped by score ranges.

    Returns:
        Dictionary with total count and category breakdown with counts and percentages
    """
    stats_mgr = StatisticsManager()
    return stats_mgr.get_statistics()


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

    # Display score summary statistics
    total_score = stats.get("total_score", 0)
    max_score = stats.get("max_score", 0)
    min_score = stats.get("min_score", 0)
    print(f"║ Gesamtpunktzahl: {total_score:>36d}  ║")
    print(f"║ Höchste Punktzahl: {max_score:>34d}  ║")
    print(f"║ Niedrigste Punktzahl: {min_score:>31d}  ║")
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


def quiz():
    """CLI interface for running a quiz."""
    vocab_mgr = VocableManager()
    vocables = vocab_mgr.get_all_vocables()

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

    # Create quiz session
    quiz_session = QuizSession(count)

    # Run through all questions
    while not quiz_session.is_complete():
        question = quiz_session.get_current_question()

        print(f"\nFrage {question['index'] + 1}/{question['total']}")

        if question["direction"] == "de_en":
            response = input(f"Was heißt '{question['german']}' auf Englisch? ").strip()
        else:
            response = input(f"Was heißt '{question['english']}' auf Deutsch? ").strip()

        feedback = quiz_session.submit_answer(response)

        if feedback["was_correct"]:
            print("✓ Richtig!")
        else:
            print(f"✗ Falsch! Richtige Antwort: {feedback['correct_answer']}")

        quiz_session.move_next()

    # Save session and display results
    quiz_session.save_session()
    results = quiz_session.get_results()
    display_quiz_results(results)


def menu():
    """Main CLI menu loop."""
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
            add_vocables()
        elif auswahl == "2":
            quiz()
        elif auswahl == "3":
            show_vocables()
        elif auswahl == "4":
            print("Bis Bald!")
            break
        else:
            print("Ungültige auswahl.\n")


if __name__ == "__main__":
    menu()
