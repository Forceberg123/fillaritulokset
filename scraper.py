from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup

SEURATTAVAT = [
    # Miehet
    {"nimi": "Axel Källberg", "url_nimi": "axel-kallberg", "talli": "Lucky Sport Cycling Team"},
    {"nimi": "Kasper Borremans", "url_nimi": "kasper-borremans", "talli": "Bahrain Victorious Development Team"},
    # Naiset
    {"nimi": "Anniina Ahtosalo", "url_nimi": "anniina-ahtosalo", "talli": "Uno-X Mobility"},
    {"nimi": "Wilma Aintila", "url_nimi": "wilma-aintila", "talli": "CANYON//SRAM"},
    {"nimi": "Heidi Antikainen", "url_nimi": "heidi-antikainen", "talli": "Minimax Cycling Team"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FinnishCyclistsBot/1.0 (Hobby Project)"
}

def jäsennä_pvm(pvm_str):
    """Muuntaa päivämäärämerkkijonon datetime-olioksi lajittelua varten."""
    if not pvm_str:
        return datetime(1900, 1, 1)
    
    pvm_str = str(pvm_str).strip()
    muodot = ['%d.%m.%Y', '%d.%m.', '%d.%m']
    for muoto in muodot:
        try:
            dt = datetime.strptime(pvm_str, muoto)
            if dt.year == 1900:
                dt = dt.replace(year=2026)
            return dt
        except ValueError:
            continue
    return datetime(1900, 1, 1)

def hae_urheilijan_tiedot(urheilija):
    url = f"https://www.procyclingstats.com/rider/{urheilija['url_nimi']}"
    print(f"Haetaan tiedot: {urheilija['nimi']}...")
    
    tulevat_kisat = []
    tulokset = []
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"  Virhe haussa (status {response.status_code})")
            return tulevat_kisat, tulokset

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    tekstit = [col.get_text(strip=True) for col in cols]
                    
                    # 1. Etsitään päivämäärä sarakkeista (etsitään kenttä, jossa on piste ja numeroita)
                    paivamaara = ""
                    for t in tekstit:
                        if '.' in t and any(char.isdigit() for char in t) and len(t) <= 10:
                            paivamaara = t
                            break
                    
                    # 2. Etsitään kilpailun nimi linkistä
                    linkki = row.find('a', href=True)
                    kisan_nimi = ""
                    if linkki:
                        kisan_nimi = linkki.get_text(strip=True)
                    
                    if not kisan_nimi or kisan_nimi.isdigit():
                        continue

                    # 3. Tarkistetaan onko rivillä sijoitusta (tulos vs tuleva kisa)
                    sijoitus = ""
                    for t in tekstit[:4]:
                        if t.isdigit() or t in ["1st", "2nd", "3rd", "OTL", "DNF"]:
                            sijoitus = t
                            break

                    if sijoitus:
                        # Mennyt tulos
                        if not paivamaara:
                            paivamaara = "01.01."
                        tulokset.append({
                            "urheilija": urheilija["nimi"],
                            "talli": urheilija["talli"],
                            "kilpailu": kisan_nimi,
                            "sijoitus": sijoitus,
                            "pvm": paivamaara
                        })
                    else:
                        # Tuleva kisa (Program) - varmistetaan että päivämäärä löytyy
                        if paivamaara:
                            tulevat_kisat.append({
                                "urheilija": urheilija["nimi"],
                                "talli": urheilija["talli"],
                                "kilpailu": kisan_nimi,
                                "pvm": paivamaara
                            })

    except Exception as e:
        print(f"  Virhe käsiteltäessä urheilijaa {urheilija['nimi']}: {e}")

    # Poistetaan duplikaatit tuloksista
    uniset_tulokset = []
    loydetyt_tulokset = set()
    for t in tulokset:
        tunniste = (t["urheilija"], t["kilpailu"], t["sijoitus"], t["pvm"])
        if tunniste not in loydetyt_tulokset:
            loydetyt_tulokset.add(tunniste)
            uniset_tulokset.append(t)

    # Poistetaan duplikaatit tulevista
    uniset_tulevat = []
    loydetyt_tulevat = set()
    for t in tulevat_kisat:
        tunniste = (t["urheilija"], t["kilpailu"], t["pvm"])
        if tunniste not in loydetyt_tulevat:
            loydetyt_tulevat.add(tunniste)
            uniset_tulevat.append(t)

    return uniset_tulevat, uniset_tulokset

def paivita_data():
    kaikki_tulokset = []
    kaikki_tulevat = []

    for kusk in SEURATTAVAT:
        tulevat, tulokset = hae_urheilijan_tiedot(kusk)
        kaikki_tulevat.extend(tulevat)
        kaikki_tulokset.extend(tulokset)

    # Lajitellaan tulokset: uusin ensin (laskeva)
    kaikki_tulokset.sort(key=lambda x: jäsennä_pvm(x['pvm']), reverse=True)

    # Lajitellaan tulevat kisat: lähin ensin (nouseva aikajärjestys)
    kaikki_tulevat.sort(key=lambda x: jäsennä_pvm(x['pvm']))

    data = {
        "paivitetty": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "suomalaiset": [{"nimi": k["nimi"], "talli": k["talli"]} for k in SEURATTAVAT],
        "tulokset": kaikki_tulokset,
        "tulevat_kisat": kaikki_tulevat
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("data.json päivitetty: tulevat kisat ja päivämäärät haettu onnistuneesti!")

if __name__ == "__main__":
    paivita_data()
