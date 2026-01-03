import json
import random
import os

DATEI = "vokabeln.json"


def lade_vokabeln():
    if not os.path.exist(DATEI):
        return []
    with open(DATEI,"r", encoding="utf-8") as f:
        return json.load(f)


def menue():
    vokabeln = lade_vokabeln()

    while True:
        print("----- Vokabeltrainer -----")
        print("1) vokabeln hinzfügen")
        print("2) Quiz starten")
        print("3) Alle Vokabeln anzeigen")
        print("4) beenden")

        auswahl =input("auswahl: ").strip()

        if auswahl == "4":
            print("Bis Bald!")
            break

        else:
            print("Ungültige auswahl.\n")



if __name__ == "__main__":
    menue()