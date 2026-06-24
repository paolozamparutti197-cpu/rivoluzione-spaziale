import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests


API_BASE = "https://ll.thespacedevs.com/2.3.0/launches/upcoming/"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "spacex_lanci_fino_luglio_2026 (1).html"
SITE_GENERATOR = ROOT / "03_script" / "genera_sito_rivoluzione.py"

MONTHS_IT = {
    1: "gennaio",
    2: "febbraio",
    3: "marzo",
    4: "aprile",
    5: "maggio",
    6: "giugno",
    7: "luglio",
    8: "agosto",
    9: "settembre",
    10: "ottobre",
    11: "novembre",
    12: "dicembre",
}

STATUS_LABELS = {
    "Go for Launch": "Go for launch",
    "To Be Confirmed": "Date/time may change",
    "To Be Determined": "NET / da definire",
}

SPECIAL_NAMES = {
    "Project Starfall Demonstration Mission": "Starfall Demo",
}

TARGET_FILES = [
    "03_script/aggiorna_lanci_spacex_sito.py",
    "05 - Aggiorna tutto e pubblica sito.bat",
    "LEGGIMI_SCRIPT_SITO.txt",
    "spacex_lanci_fino_luglio_2026 (1).html",
    "sezioni/lanci-imminenti.html",
    "sezioni/spacex.html",
    "sezioni/storico-lanci.html",
]


def safe_get(dct, *keys, default=""):
    cur = dct
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def fetch_spacex_launches(max_launches=100, retries=3):
    launches = []
    limit = 25
    offset = 0

    while len(launches) < max_launches:
        params = {
            "format": "json",
            "mode": "detailed",
            "lsp__name": "SpaceX",
            "ordering": "net",
            "limit": limit,
            "offset": offset,
        }
        for attempt in range(retries):
            response = requests.get(API_BASE, params=params, timeout=30)
            if response.status_code != 429 or attempt == retries - 1:
                break
            retry_after = response.headers.get("Retry-After")
            wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else 20 * (attempt + 1)
            print(f"Rate limit The Space Devs: attendo {wait_seconds}s e riprovo...")
            time.sleep(wait_seconds)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            break
        launches.extend(results)
        if not data.get("next"):
            break
        offset += limit

    return launches[:max_launches]


def mission_name(launch):
    name = safe_get(launch, "mission", "name")
    if not name:
        name = str(launch.get("name") or "").split("|")[-1].strip()
    return SPECIAL_NAMES.get(name, name)


def rocket_name(launch):
    return (
        safe_get(launch, "rocket", "configuration", "full_name")
        or safe_get(launch, "rocket", "configuration", "name")
        or "Razzo da confermare"
    )


def site_name(launch):
    pad = safe_get(launch, "pad", "name")
    location = safe_get(launch, "pad", "location", "name")
    if pad and location:
        return f"{pad}, {location}"
    return pad or location or "Sito da confermare"


def orbit_name(launch):
    abbrev = safe_get(launch, "mission", "orbit", "abbrev")
    name = safe_get(launch, "mission", "orbit", "name")
    if abbrev:
        return abbrev
    return name or "Orbita da confermare"


def first_sentence(text):
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    if not cleaned:
        return ""
    match = re.search(r"(?<=[.!?])\s+", cleaned)
    if match:
        return cleaned[: match.start()].strip()
    return cleaned


def compact_text(text, max_chars=430):
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    if not cleaned:
        return "Dettagli missione non ancora pubblicati nella fonte dati."
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[: max_chars - 1].rsplit(" ", 1)[0]
    return f"{cut}..."


def landing_text(launch):
    stages = safe_get(launch, "rocket", "launcher_stage", default=[])
    if not isinstance(stages, list) or not stages:
        return "Recupero booster non indicato da The Space Devs"

    pieces = []
    for stage in stages:
        landing = stage.get("landing") if isinstance(stage, dict) else None
        launcher = stage.get("launcher") if isinstance(stage, dict) else None
        launcher = launcher if isinstance(launcher, dict) else {}
        landing = landing if isinstance(landing, dict) else {}
        serial = launcher.get("serial_number")
        serial_unknown = not serial or launcher.get("is_placeholder") or str(serial).lower().startswith("unknown")
        flight = stage.get("launcher_flight_number")
        location = safe_get(landing, "landing_location", "abbrev") or safe_get(landing, "landing_location", "name")
        attempt = landing.get("attempt")

        if location and not serial_unknown and flight:
            pieces.append(f"{location}, booster {serial}, volo {flight}")
        elif location and not serial_unknown:
            pieces.append(f"{location}, booster {serial}")
        elif location:
            pieces.append(f"{location}, booster non identificato")
        elif attempt is False:
            pieces.append("Nessun tentativo di recupero indicato")

    return "; ".join(pieces) if pieces else "Recupero booster non indicato da The Space Devs"


def source_links(launch):
    links = [["The Space Devs", launch.get("url") or API_BASE]]
    for item in launch.get("info_urls") or []:
        url = item.get("url") if isinstance(item, dict) else None
        if not url:
            continue
        host = urlparse(url).netloc.replace("www.", "")
        label = host or "Fonte"
        if [label, url] not in links:
            links.append([label, url])
    for item in launch.get("vid_urls") or []:
        url = item.get("url") if isinstance(item, dict) else None
        if url:
            links.append(["Webcast", url])
            break
    return links


def is_exact_launch(launch):
    precision = safe_get(launch, "net_precision", "abbrev")
    return precision in {"SEC", "MIN", "HR"}


def date_label(launch, dt, exact):
    if not dt:
        return "Data da confermare"
    status = safe_get(launch, "status", "name")
    prefix = "NET " if status in {"To Be Confirmed", "To Be Determined"} else ""
    if exact:
        return f"{prefix}{dt.day} {MONTHS_IT[dt.month]} {dt.year}, {dt:%H:%M} UTC"
    return f"NET {MONTHS_IT[dt.month]} {dt.year}"


def window_label(launch, dt, exact):
    if not exact:
        precision = safe_get(launch, "net_precision", "abbrev")
        if precision in {"M", "Q1", "Q2", "Q3", "Q4", "Y"}:
            return "Mese o trimestre non puntuale; data e orario da ricontrollare"
        return "Finestra non puntuale; data e orario da ricontrollare"

    start = parse_iso(launch.get("window_start"))
    end = parse_iso(launch.get("window_end"))
    if start and end and start.date() == end.date():
        label = f"{start:%H:%M}-{end:%H:%M} UTC"
    elif start and end:
        label = f"{start.day} {MONTHS_IT[start.month]} {start:%H:%M} - {end.day} {MONTHS_IT[end.month]} {end:%H:%M} UTC"
    elif dt and exact:
        label = f"T-0 indicato: {dt:%H:%M} UTC"
    else:
        label = "Finestra non puntuale"

    status = safe_get(launch, "status", "name")
    if status in {"To Be Confirmed", "To Be Determined"}:
        label += "; data e orario da ricontrollare"
    return label


def categories_for(launch, name, rocket, exact):
    text = f"{name} {rocket}".lower()
    categories = ["exact"] if exact else ["net"]
    if "starlink" in text:
        categories.append("starlink")
    if "sda " in text or "space development agency" in text or "tranche" in text:
        categories.append("sda")
    if "starship" in text or "flight " in text and "starship" in rocket.lower():
        categories.append("starship")
    return categories


def convert_launch(launch):
    dt = parse_iso(launch.get("net"))
    exact = is_exact_launch(launch)
    name = mission_name(launch)
    rocket = rocket_name(launch)
    mission_type = safe_get(launch, "mission", "type")
    description = safe_get(launch, "mission", "description")
    status_name = safe_get(launch, "status", "name")
    status_description = safe_get(launch, "status", "description")
    payload = name if not mission_type else f"{name} ({mission_type})"
    return {
        "id": str(launch.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")),
        "cat": categories_for(launch, name, rocket, exact),
        "name": name,
        "status": STATUS_LABELS.get(status_name, status_name or "Stato da confermare"),
        "rocket": rocket,
        "dateLabel": date_label(launch, dt, exact),
        "iso": launch.get("net") or "",
        "window": window_label(launch, dt, exact),
        "site": site_name(launch),
        "landing": landing_text(launch),
        "orbit": orbit_name(launch),
        "payload": payload,
        "summary": compact_text(description),
        "news": status_description or first_sentence(description) or "Dati aggiornati da The Space Devs.",
        "sources": source_links(launch),
    }


def last_day_next_month(now):
    year = now.year + (1 if now.month == 12 else 0)
    next_month = 1 if now.month == 12 else now.month + 1
    after_next_year = year + (1 if next_month == 12 else 0)
    after_next_month = 1 if next_month == 12 else next_month + 1
    return datetime(after_next_year, after_next_month, 1, tzinfo=timezone.utc)


def build_manifest_launches(max_launches, include_all=False):
    now = datetime.now(timezone.utc)
    horizon = None if include_all else last_day_next_month(now)
    converted = []
    for launch in fetch_spacex_launches(max_launches=max_launches):
        dt = parse_iso(launch.get("net"))
        if dt and dt <= now:
            continue
        if horizon and dt and dt >= horizon:
            continue
        converted.append(convert_launch(launch))
    return sorted(converted, key=lambda item: item.get("iso") or "9999")


def replace_launches_block(text, launches):
    data = json.dumps(launches, ensure_ascii=False, indent=2)
    updated, count = re.subn(
        r"const launches = \[[\s\S]*?\];",
        f"const launches = {data};",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Blocco 'const launches = [...]' non trovato nel manifesto.")
    now = datetime.now()
    today = f"{now.day} {MONTHS_IT[now.month]} {now.year}"
    updated = re.sub(
        r"fotografia ragionata del quadro disponibile al [^.<]+",
        f"fotografia ragionata del quadro disponibile al {today}",
        updated,
        count=1,
    )
    return updated


def update_manifest(launches):
    text = MANIFEST.read_text(encoding="utf-8")
    updated = replace_launches_block(text, launches)
    MANIFEST.write_text(updated, encoding="utf-8")


def regenerate_site():
    subprocess.check_call([sys.executable, str(SITE_GENERATOR)], cwd=ROOT)


def publish_to_github(message):
    subprocess.check_call(["git", "add", "--", *TARGET_FILES], cwd=ROOT)
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True)
    if not staged.strip():
        print("Nessuna modifica da pubblicare.")
        return
    subprocess.check_call(["git", "commit", "-m", message], cwd=ROOT)
    subprocess.check_call(["git", "push", "origin", "main"], cwd=ROOT)
    subprocess.check_call(["git", "push", "origin", "main:gh-pages"], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="Aggiorna l'agenda SpaceX del sito usando The Space Devs."
    )
    parser.add_argument("--max", type=int, default=100, help="Numero massimo di lanci SpaceX da leggere dall'API.")
    parser.add_argument("--include-all", action="store_true", help="Non limitare l'output alla fine del mese prossimo.")
    parser.add_argument("--publish", action="store_true", help="Commit e push automatico su main e gh-pages.")
    parser.add_argument("--dry-run", action="store_true", help="Scarica e mostra il riepilogo senza scrivere file.")
    args = parser.parse_args()

    launches = build_manifest_launches(max_launches=args.max, include_all=args.include_all)
    exact = sum(1 for item in launches if "exact" in item.get("cat", []))
    net = sum(1 for item in launches if "net" in item.get("cat", []))

    print(f"Lanci SpaceX pronti per il sito: {len(launches)} ({exact} T-0, {net} NET).")
    for item in launches[:8]:
        print(f"- {item['dateLabel']}: {item['name']}")

    if args.dry_run:
        return

    update_manifest(launches)
    regenerate_site()
    print(f"Aggiornati: {MANIFEST}")
    print(f"Aggiornata: {ROOT / 'sezioni' / 'lanci-imminenti.html'}")

    if args.publish:
        publish_to_github("Aggiorna agenda SpaceX da The Space Devs")
        print("Pubblicato su main e gh-pages.")


if __name__ == "__main__":
    main()
