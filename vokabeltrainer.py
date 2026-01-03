import json
import random
import os

FILE_VOCABLES = "vokabeln.json"
FILE_SCORES = "scores.json"


def load_vocables():
    if not os.path.exists(FILE_VOCABLES):
        return []
    with open(FILE_VOCABLES, "r", encoding="utf-8") as f:
        return json.load(f)


def speichere_vokabeln(vokabeln):
    with open(FILE_VOCABLES, "w", encoding="utf-8") as f:
        json.dump(vokabeln, f, ensure_ascii=False, indent=4)


def vokabeln_hinzufuegen(vokabeln):
    deutsch = input("deutsch: ").strip()
    english = input("english: ").strip()

    next_id = 1 if not vokabeln else max(v["id"] for v in vokabeln) + 1

    vokabeln.append({
        "id": next_id,
        "de": deutsch,
        "en": english
    })
    speichere_vokabeln(vokabeln)
    print("Vokabeln hinzugefügt!\n")


def show_vocables(vokabeln):
    for v in vokabeln:
        print(f"{v['de']} - {v['en']}")
    print("\n")


def quiz(vokabeln):
    if not vokabeln:
        print("keine vokabeln vorhanden.\n")
        return

    frage = random.choice(vokabeln)
    richtung = random.choice(["de_en", "en_de"])

    if richtung == "de_en":
        antwort = input(f"Was heißt '{frage['de']} auf Englisch? ").strip().lower()
        if antwort == frage['en'].lower():
            print("Richtig!\n")
        else:
            print(f"x Falsch!. Richtige Antwort: {frage['en']}")
    else:
        antwort = input(f"Was heißt '{frage['en']} auf Deutsch? ").strip().lower()
        if antwort == frage['de'].lower():
            print("Richtig!\n")
        else:
            print(f"x Falsch!. Richtige Antwort: {frage['de']}")


def menue():
    vokabeln = lade_vokabeln()

    while True:
        print("----- Vokabeltrainer -----")
        print("1) Vokabeln hinzufügen")
        print("2) Quiz starten")
        print("3) Alle Vokabeln anzeigen")
        print("4) beenden")

        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            vokabeln_hinzufuegen(vokabeln)
        elif auswahl == "2":
            quiz(vokabeln)
        elif auswahl == "3":
            show_vocables(vokabeln)
        elif auswahl == "4":
            print("Bis Bald!")
            break
        else:
            print("Ungültige auswahl.\n")


if __name__ == "__main__":
    menue()
