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


API_URL = "https://ll.thespacedevs.com/2.3.0/launches/upcoming/"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("prossimi_lanci_electron.json")
SITE_GENERATOR = ROOT / "03_script" / "genera_sito_rivoluzione.py"
OUTPUT = ROOT / "sezioni" / "lanci-imminenti-electron.html"

MONTHS_IT = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio", 6: "giugno",
    7: "luglio", 8: "agosto", 9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre",
}


def safe_get(data, *keys, default=""):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def compact(value, limit=430):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return "Dettagli della missione non ancora pubblicati nella fonte dati."
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "..."


def fetch_upcoming(max_launches=100, retries=3):
    params = {
        "format": "json",
        "mode": "detailed",
        "rocket__configuration__name": "Electron",
        "ordering": "net",
        "limit": min(max_launches, 100),
    }
    for attempt in range(retries):
        response = requests.get(API_URL, params=params, timeout=90)
        if response.status_code != 429 or attempt == retries - 1:
            break
        wait_seconds = int(response.headers.get("Retry-After", 20 * (attempt + 1)))
        print(f"Rate limit The Space Devs: attendo {wait_seconds}s...")
        time.sleep(wait_seconds)
    response.raise_for_status()
    return response.json().get("results", [])[:max_launches]


def end_of_next_month(now):
    year = now.year + (1 if now.month == 12 else 0)
    month = 1 if now.month == 12 else now.month + 1
    end_year = year + (1 if month == 12 else 0)
    end_month = 1 if month == 12 else month + 1
    return datetime(end_year, end_month, 1, tzinfo=timezone.utc)


def date_label(launch, launch_time, exact):
    if not launch_time:
        return "Data da confermare"
    if exact:
        return f"{launch_time.day} {MONTHS_IT[launch_time.month]} {launch_time.year}, {launch_time:%H:%M} UTC"
    return f"NET {MONTHS_IT[launch_time.month]} {launch_time.year}"


def source_links(launch):
    links = [{"label": "The Space Devs", "url": launch.get("url") or API_URL}]
    video_urls = launch.get("vid_urls") or []
    for item in (launch.get("info_urls") or []) + video_urls:
        url = item.get("url") if isinstance(item, dict) else None
        if not url:
            continue
        label = "Webcast" if item in video_urls else urlparse(url).netloc.replace("www.", "") or "Fonte"
        candidate = {"label": label, "url": url}
        if candidate not in links:
            links.append(candidate)
    return links[:4]


def convert(launch):
    launch_time = parse_iso(launch.get("net"))
    precision = safe_get(launch, "net_precision", "abbrev")
    exact = precision in {"SEC", "MIN", "HR"}
    mission = launch.get("mission") or {}
    pad = launch.get("pad") or {}
    location = pad.get("location") or {}
    mission_name = mission.get("name") or str(launch.get("name") or "").split("|")[-1].strip()
    orbit = safe_get(mission, "orbit", "abbrev") or safe_get(mission, "orbit", "name") or "Da confermare"
    site = ", ".join(part for part in (pad.get("name"), location.get("name")) if part) or "Sito da confermare"
    status = safe_get(launch, "status", "name") or "Stato da confermare"
    return {
        "id": launch.get("slug") or launch.get("id"),
        "cat": ["exact"] if exact else ["net"],
        "name": mission_name,
        "status": status,
        "rocket": "Electron",
        "dateLabel": date_label(launch, launch_time, exact),
        "iso": launch.get("net") or "",
        "window": "T-0 puntuale" if exact else "Finestra NET; data e orario da ricontrollare",
        "site": site,
        "landing": "Recupero del primo stadio non previsto nell'agenda",
        "orbit": orbit,
        "payload": mission.get("type") or "Missione Electron",
        "summary": compact(mission.get("description")),
        "news": status,
        "sources": source_links(launch),
    }


def main():
    parser = argparse.ArgumentParser(description="Aggiorna le pagine dei prossimi lanci Rocket Lab Electron.")
    parser.add_argument("--max", type=int, default=100, help="Numero massimo di lanci da leggere.")
    parser.add_argument("--include-all", action="store_true", help="Mostra tutti i lanci futuri disponibili.")
    parser.add_argument("--dry-run", action="store_true", help="Scarica e mostra il riepilogo senza scrivere file.")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    horizon = None if args.include_all else end_of_next_month(now)
    launches = []
    for raw in fetch_upcoming(args.max):
        launch_time = parse_iso(raw.get("net"))
        if launch_time and launch_time <= now:
            continue
        if horizon and launch_time and launch_time >= horizon:
            continue
        launches.append(convert(raw))
    launches.sort(key=lambda item: item["iso"] or "9999")

    print(f"Prossimi lanci Electron trovati: {len(launches)}")
    for launch in launches:
        print(f"- {launch['dateLabel']}: {launch['name']}")
    if args.dry_run:
        return

    MANIFEST.write_text(json.dumps(launches, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.check_call([sys.executable, str(SITE_GENERATOR)], cwd=ROOT)
    print(f"Manifest aggiornato: {MANIFEST}")
    print(f"Pagina aggiornata: {OUTPUT}")


if __name__ == "__main__":
    main()
