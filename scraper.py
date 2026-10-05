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
    
    pvm_str = pvm_str.strip()
    # Poistetaan mahdolliset viikonpäivät tai ylimääräiset merkit
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
    print(f"Haetaan kauden 2026 tuloksia: {urheilija['nimi']}...")
    
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
                if len(cols) >= 3:
                    tekstit = [col.get_text(strip=True) for col in cols]
                    
                    # Etsitään sijoitus
                    sijoitus = ""
                    for t in tekstit[:4]:
                        if t.isdigit() or t in ["1st", "2nd", "3rd", "OTL", "DNF"]:
                            sijoitus = t
                            break
                    
                    if sijoitus:
                        # Etsitään päivämäärä tarkemmin (etsitään kenttä jossa on piste ja pituutta vähintään 4 merkkiä)
                        paivamaara = ""
                        for t in tekstit:
                            if '.' in t and any(char.isdigit() for char in t) and len(t) <= 10:
                                paivamaara = t
                                break
                        
                        if not paivamaara:
                            paivamaara = "01.01."

                        # Etsitään kilpailun nimi linkistä
                        linkki = row.find('a', href=True)
                        kisan_nimi = ""
                        if linkki:
                            kisan_nimi = linkki.get_text(strip=True)
                        
                        if kisan_nimi and not kisan_nimi.isdigit():
                            tulokset.append({
                                "urheilija": urheilija["nimi"],
                                "talli": urheilija["talli"],
                                "kilpailu": kisan_nimi,
                                "sijoitus": sijoitus,
                                "pvm": paivamaara
                            })

    except Exception as e:
        print(f"  Virhe käsiteltäessä urheilijaa {urheilija['nimi']}: {e}")

    # Poistetaan duplikaatit
    uniset_tulokset = []
    loydetyt = set()
    for t in tulokset:
        tunniste = (t["urheilija"], t["kilpailu"], t["sijoitus"], t["pvm"])
        if tunniste not in loydetyt:
            loydetyt.add(tunniste)
            uniset_tulokset.append(t)

    return tulevat_kisat, uniset_tulokset

def paivita_data():
    kaikki_tulokset = []
    kaikki_tulevat = []

    for kusk in SEURATTAVAT:
        tulevat, tulokset = hae_urheilijan_tiedot(kusk)
        kaikki_tulevat.extend(tulevat)
        kaikki_tulokset.extend(tulokset)

    # Järjestetään KAIKKI tulokset globaalisti päivämäärän mukaan: uusin aina ylimpänä
    kaikki_tulokset.sort(key=lambda x: jäsennä_pvm(x['pvm']), reverse=True)

    data = {
        "paivitetty": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "suomalaiset": [{"nimi": k["nimi"], "talli": k["talli"]} for k in SEURATTAVAT],
        "tulokset": kaikki_tulokset,
        "tulevat_kisat": kaikki_tulevat
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("data.json päivitetty onnistuneesti ja lajiteltu globaalisti tuoreimmasta vanhimpaan!")

if __name__ == "__main__":
    paivita_data()
