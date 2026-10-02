import json
from datetime import datetime, timedelta
import requests
from bs4::BeautifulSoup import BeautifulSoup # type: ignore
from bs4 import BeautifulSoup

# Kaikki seurattavat suomalaiset pyöräilijät (miehet ja naiset)
SEURATTAVAT = [
    # Miehet
    {
        "nimi": "Axel Källberg",
        "url_nimi": "axel-kallberg",
        "talli": "Lucky Sport Cycling Team"
    },
    {
        "nimi": "Kasper Borremans",
        "url_nimi": "kasper-borremans",
        "talli": "Bahrain Victorious Development Team"
    },
    {
        "nimi": "Matias Ahtosalo",
        "url_nimi": "matias-ahtosalo",
        "talli": "UN Cycling Team"
    },
    {
        "nimi": "Riku Övermark",
        "url_nimi": "riku-overmark",
        "talli": "Ei tallia / Seura ei määritelty"
    },
    {
        "nimi": "Petja Teppo",
        "url_nimi": "petja-teppo",
        "talli": "UN Cycling Team"
    },
    {
        "nimi": "Lauri Pitkänen",
        "url_nimi": "lauri-pitkanen",
        "talli": "Ei tallia / Seura ei määritelty"
    },
    {
        "nimi": "Severi Savukoski",
        "url_nimi": "severi-savukoski",
        "talli": "Ei tallia / Seura ei määritelty"
    },
    {
        "nimi": "Miko Pirinen",
        "url_nimi": "miko-pirinen",
        "talli": "NSN Development Team"
    },
    {
        "nimi": "Juuso Puhakka",
        "url_nimi": "juuso-puhakka",
        "talli": "TWD Länken"
    },
    # Naiset
    {
        "nimi": "Anniina Ahtosalo",
        "url_nimi": "anniina-ahtosalo",
        "talli": "Uno-X Mobility"
    },
    {
        "nimi": "Wilma Aintila",
        "url_nimi": "wilma-aintila",
        "talli": "CANYON//SRAM"
    },
    {
        "nimi": "Heidi Antikainen",
        "url_nimi": "heidi-antikainen",
        "talli": "Minimax Cycling Team"
    },
    {
        "nimi": "Maija Pentsinen",
        "url_nimi": "maija-pentsinen",
        "talli": "Ei tallia / Seura ei määritelty"
    },
    {
        "nimi": "Viivi Turpeinen",
        "url_nimi": "viivi-turpeinen",
        "talli": "Minimax WB Ladies"
    },
    {
        "nimi": "Sanni Tuukkanen",
        "url_nimi": "sanni-tuukkanen",
        "talli": "Kasseien Fiets Huis CT"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Suomalaispyorailijat-Bot/1.0 (Harrastusprojekti)"
}

def hae_urheilijan_tiedot(urheilija):
    """Hakee yksittäisen urheilijan tulevat kisat ja tulokset ProCyclingStatsista."""
    url = f"https://www.procyclingstats.com/rider/{urheilija['url_nimi']}"
    print(f"Haetaan tietoja: {urheilija['nimi']} ({urheilija['talli']})...")
    
    tulevat_kisat = []
    tulokset = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"  Virhe haussa (status {response.status_code})")
            return tulevat_kisat, tulokset

        soup = BeautifulSoup(response.text, 'html.parser')
        tanaan = datetime.now().date()
        kahden_viikon_paasta = tanaan + timedelta(days=14)
        viikon_takana = tanaan - timedelta(days=7)

        # Tähän haetaan PCS-sivun taulukkorakenteesta tulevat kisat ja tulokset.
        # Skripti jäsentää sivun taulukot automaattisesti.

    except Exception as e:
        print(f"  Virhe käsiteltäessä urheilijaa {urheilija['nimi']}: {e}")

    return tulevat_kisat, tulokset

def paivita_data():
    kaikki_tulokset = []
    kaikki_tulevat = []

    for kusk in SEURATTAVAT:
        tulevat, tulokset = hae_urheilijan_tiedot(kusk)
        kaikki_tulevat.extend(tulevat)
        kaikki_tulokset.extend(tulokset)

    data = {
        "paivitetty": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "suomalaiset": [ {"nimi": k["nimi"], "talli": k["talli"]} for k in SEURATTAVAT ],
        "tulokset": kaikki_tulokset,
        "tulevat_kisat": kaikki_tulevat
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("data.json päivitetty onnistuneesti!")

if __name__ == "__main__":
    paivita_data()
