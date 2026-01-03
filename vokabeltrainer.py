import json
import random
import os
from typing import Any

DATEI = "vokabeln.json"


def lade_vokabeln():
    if not os.path.exists(DATEI):
        return []
    with open(DATEI,"r", encoding="utf-8") as f:
        return json.load(f)


def speichere_vokabeln(vokabeln):
    with open(DATEI,"r", encoding="utf-8") as f:
        json.dump(vokabeln,f, ensure_ascii=False, indent=4)

def vokabeln_hinzufuegen(vokabeln):
    deutsch = input("deutsch: ").strip()
    english = input("english: ").strip()
    vokabeln.append({"de":deutsch,"en":english})
    speichere_vokabeln(vokabeln)
    print("Vokabeln hinzugefügt!\n")


def show_vocables(vokabeln):
    for v in vokabeln:
        print(f"{v['de']} - {v['en']}")
    print("\n")


def menue():
    vokabeln = lade_vokabeln()

    while True:
        print("----- Vokabeltrainer -----")
        print("1) vokabeln hinzfügen")
        print("2) Quiz starten")
        print("3) Alle Vokabeln anzeigen")
        print("4) beenden")

        auswahl =input("auswahl: ").strip()

        if auswahl == "1":
            vokabeln_hinzufuegen(vokabeln)
        elif auswahl == "3":
            show_vocables(vokabeln)
        elif auswahl == "4":
            print("Bis Bald!")
            break
        else:
            print("Ungültige auswahl.\n")


if __name__ == "__main__":
    menue()