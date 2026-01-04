import json
import random
import os
from datetime import datetime

FILE_VOCABLES = "vokabeln.json"
FILE_SCORES = "scores.json"


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


def quiz(vocables, scores):
    if not vocables:
        print("Keine Vokabeln vorhanden.\n")
        return

    question = random.choice(vocables)
    vocable_id = str(question["id"])

    init_scores(scores, vocable_id)
    direction = random.choice(["de_en", "en_de"])

    if direction == "de_en":
        response = input(f"Was heißt '{question['de']}' auf Englisch? ").strip()
        correct = question["en"]
    else:
        response = input(f"Was heißt '{question['en']}' auf Deutsch? ").strip()
        correct = question["de"]

    scores[vocable_id]["last_practiced"] = now()

    if response == correct:
        print("✓ Richtig!\n")
        scores[vocable_id]["score"] += 1
        scores[vocable_id]["last_correct"] = now()
    else:
        print(f"✗ Falsch! Richtige Antwort: {correct}\n")

    save_scores(scores)


def menu():
    vocables = load_vocables()
    scores = load_scores()

    while True:
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
