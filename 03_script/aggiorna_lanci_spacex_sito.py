import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests


API_BASE = "https://ll.thespacedevs.com/2.3.0/launches/upcoming/"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "spacex_lanci_fino_luglio_2026 (1).html"
SITE_GENERATOR = ROOT / "03_script" / "genera_sito_rivoluzione.py"
PUBLIC_PAGE = "https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/sezioni/lanci-imminenti.html"
CHECK_STATE = Path(tempfile.gettempdir()) / "rivoluzione-spaziale-space-launches-check.json"
CHECK_COOLDOWN_SECONDS = 600
MAX_AUTOMATIC_WAIT_SECONDS = 90

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

PUBLISH_FILES = [
    "spacex_lanci_fino_luglio_2026 (1).html",
    "sezioni/lanci-imminenti.html",
    "sezioni/spacex.html",
]


def log(message):
    print(message, flush=True)


def run_git(*args, capture=False):
    command = ["git", *args]
    if capture:
        return subprocess.check_output(command, cwd=ROOT, text=True, encoding="utf-8").strip()
    subprocess.check_call(command, cwd=ROOT)


def recent_successful_check():
    try:
        state = json.loads(CHECK_STATE.read_text(encoding="utf-8"))
        checked_at = float(state.get("checked_at", 0))
    except (OSError, ValueError, TypeError):
        return 0
    age = time.time() - checked_at
    return max(0, CHECK_COOLDOWN_SECONDS - age) if 0 <= age < CHECK_COOLDOWN_SECONDS else 0


def record_successful_check():
    try:
        CHECK_STATE.write_text(json.dumps({"checked_at": time.time()}), encoding="utf-8")
    except OSError:
        pass


def agenda_files_are_clean():
    return subprocess.run(["git", "diff", "--quiet", "--", *PUBLISH_FILES], cwd=ROOT).returncode == 0


@contextmanager
def single_instance():
    lock_path = Path(tempfile.gettempdir()) / "rivoluzione-spaziale-space-launches.lock"
    handle = lock_path.open("a+b")
    handle.seek(0)
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    try:
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    except (ImportError, OSError):
        handle.close()
        raise RuntimeError(
            "Un altro aggiornamento SpaceX e gia in corso. Attendi che termini: non serve aprire di nuovo il numero 3."
        )
    try:
        yield
    finally:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        handle.close()


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
        response = None
        for attempt in range(retries):
            try:
                response = requests.get(
                    API_BASE,
                    params=params,
                    timeout=(10, 45),
                    headers={"Accept": "application/json", "User-Agent": "Rivoluzione-Spaziale-Updater/2.0"},
                )
                retryable = response.status_code == 429 or 500 <= response.status_code < 600
                if not retryable or attempt == retries - 1:
                    break
                retry_after = response.headers.get("Retry-After")
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else 10 * (attempt + 1)
                if wait_seconds > MAX_AUTOMATIC_WAIT_SECONDS:
                    retry_at = datetime.now().astimezone() + timedelta(seconds=wait_seconds)
                    raise RuntimeError(
                        "The Space Devs ha temporaneamente esaurito la quota di richieste. "
                        f"Riprova dopo le {retry_at:%H:%M}; nessun file e stato modificato."
                    )
                log(f"Fonte temporaneamente occupata ({response.status_code}); nuovo tentativo tra {wait_seconds} s...")
                time.sleep(wait_seconds)
            except requests.RequestException:
                if attempt == retries - 1:
                    raise
                wait_seconds = 10 * (attempt + 1)
                log(f"Problema di rete; nuovo tentativo tra {wait_seconds} s...")
                time.sleep(wait_seconds)
        if response is None:
            raise RuntimeError("La fonte The Space Devs non ha restituito alcuna risposta.")
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


def launches_version(launches):
    canonical = json.dumps(launches, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def read_manifest_launches(text):
    match = re.search(r"const launches = (\[[\s\S]*?\]);", text)
    if not match:
        raise RuntimeError("Blocco 'const launches = [...]' non trovato nel manifesto.")
    return json.loads(match.group(1))


def replace_launches_block(text, launches):
    previous = read_manifest_launches(text)
    data_changed = previous != launches
    version = launches_version(launches)
    existing_updated_at = re.search(r'const launchesUpdatedAt = "([^"]+)";', text)
    updated_at = existing_updated_at.group(1) if existing_updated_at else ""

    if data_changed or not updated_at:
        updated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")

    data = json.dumps(launches, ensure_ascii=False, indent=2)
    updated, count = re.subn(
        r"const launches = \[[\s\S]*?\];",
        f"const launches = {data};",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Blocco 'const launches = [...]' non trovato nel manifesto.")

    metadata = (
        f'const launchesUpdatedAt = "{updated_at}";\n'
        f'const launchesDataVersion = "{version}";\n'
    )
    if re.search(r'const launchesUpdatedAt = "[^"]*";\s*const launchesDataVersion = "[^"]*";\s*', updated):
        updated = re.sub(
            r'const launchesUpdatedAt = "[^"]*";\s*const launchesDataVersion = "[^"]*";\s*',
            metadata,
            updated,
            count=1,
        )
    else:
        updated = updated.replace("const launches = [", metadata + "const launches = [", 1)

    if data_changed:
        now = datetime.now()
        today = f"{now.day} {MONTHS_IT[now.month]} {now.year}"
        updated = re.sub(
            r"fotografia ragionata del quadro disponibile al [^.<]+",
            f"fotografia ragionata del quadro disponibile al {today}",
            updated,
            count=1,
        )
    return updated, previous, data_changed, version, updated_at


def update_manifest(launches):
    text = MANIFEST.read_text(encoding="utf-8")
    updated, previous, data_changed, version, updated_at = replace_launches_block(text, launches)
    file_changed = updated != text
    if file_changed:
        MANIFEST.write_text(updated, encoding="utf-8")
    return file_changed, data_changed, previous, version, updated_at


def regenerate_site():
    subprocess.check_call([sys.executable, str(SITE_GENERATOR)], cwd=ROOT)


def prepare_publish():
    branch = run_git("branch", "--show-current", capture=True)
    if branch != "main":
        raise RuntimeError(f"Pubblicazione interrotta: il branch attivo e '{branch}', non 'main'.")
    if subprocess.run(["git", "diff", "--cached", "--quiet", "--", *PUBLISH_FILES], cwd=ROOT).returncode != 0:
        raise RuntimeError("Ci sono gia modifiche in staging nei file dell'agenda. Rivedile prima di usare il numero 3.")

    run_git("fetch", "origin", "main", "--quiet")
    remote_main = run_git("rev-parse", "origin/main", capture=True)
    head = run_git("rev-parse", "HEAD", capture=True)
    if subprocess.run(["git", "merge-base", "--is-ancestor", remote_main, head], cwd=ROOT).returncode == 0:
        return
    if subprocess.run(["git", "merge-base", "--is-ancestor", head, remote_main], cwd=ROOT).returncode == 0:
        log("Il repository locale e indietro: allineamento veloce con GitHub...")
        run_git("merge", "--ff-only", "origin/main")
        return
    raise RuntimeError("Il branch locale e GitHub hanno storie divergenti. Serve un controllo manuale prima del push.")


def verify_public_page(version, timeout_seconds=600):
    deadline = time.monotonic() + timeout_seconds
    log("[4/4] Attendo che GitHub Pages renda visibile la nuova versione...")
    while time.monotonic() < deadline:
        try:
            response = requests.get(
                PUBLIC_PAGE,
                params={"v": version, "t": int(time.time())},
                timeout=(10, 30),
                headers={"Cache-Control": "no-cache", "User-Agent": "Rivoluzione-Spaziale-Updater/2.0"},
            )
            if response.ok and f'content="{version}"' in response.text:
                log(f"OK: versione {version} visibile online: {PUBLIC_PAGE}?v={version}")
                return True
        except requests.RequestException:
            pass
        time.sleep(15)
    log(f"ATTENZIONE: push riuscito, ma GitHub Pages non ha confermato la versione entro {timeout_seconds // 60} minuti.")
    log(f"Controlla piu tardi: {PUBLIC_PAGE}?v={version}")
    return False


def publish_to_github(message, version):
    run_git("add", "--", *PUBLISH_FILES)
    if subprocess.run(["git", "diff", "--cached", "--quiet", "--", *PUBLISH_FILES], cwd=ROOT).returncode == 0:
        log("Nessuna modifica da pubblicare: non creo commit e non avvio GitHub Pages.")
        return False
    run_git("commit", "--only", "-m", message, "--", *PUBLISH_FILES)
    commit = run_git("rev-parse", "HEAD", capture=True)
    log("[3/4] Invio un solo aggiornamento a main e gh-pages...")
    run_git("push", "origin", "main")
    run_git("push", "origin", "main:gh-pages")
    verify_public_page(version)
    log(f"Pubblicazione completata con commit {commit[:8]}.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Aggiorna l'agenda SpaceX del sito usando The Space Devs."
    )
    parser.add_argument("--max", type=int, default=100, help="Numero massimo di lanci SpaceX da leggere dall'API.")
    parser.add_argument("--include-all", action="store_true", help="Non limitare l'output alla fine del mese prossimo.")
    parser.add_argument("--publish", action="store_true", help="Commit e push automatico su main e gh-pages.")
    parser.add_argument("--dry-run", action="store_true", help="Scarica e mostra il riepilogo senza scrivere file.")
    parser.add_argument("--force", action="store_true", help="Ignora la pausa di 10 minuti tra due controlli consecutivi.")
    args = parser.parse_args()
    with single_instance():
        cooldown = recent_successful_check()
        if cooldown and not args.force and agenda_files_are_clean():
            log(
                "Controllo gia eseguito da pochi minuti. "
                f"Per evitare richieste e pubblicazioni inutili, riprova tra {max(1, int(cooldown // 60) + 1)} min."
            )
            return

        if args.publish:
            log("[1/4] Controllo repository e collegamento con GitHub...")
            prepare_publish()

        log("[2/4] Leggo e confronto i prossimi lanci SpaceX...")
        launches = build_manifest_launches(max_launches=args.max, include_all=args.include_all)
        record_successful_check()
        exact = sum(1 for item in launches if "exact" in item.get("cat", []))
        net = sum(1 for item in launches if "net" in item.get("cat", []))
        log(f"Fonte letta correttamente: {len(launches)} lanci ({exact} T-0, {net} NET).")
        for item in launches[:8]:
            log(f"- {item['dateLabel']}: {item['name']}")

        if args.dry_run:
            log("Controllo terminato: nessun file modificato.")
            return

        file_changed, data_changed, previous, version, updated_at = update_manifest(launches)
        old_by_id = {item.get("id"): item for item in previous}
        new_by_id = {item.get("id"): item for item in launches}
        added = len(new_by_id.keys() - old_by_id.keys())
        removed = len(old_by_id.keys() - new_by_id.keys())
        revised = sum(old_by_id[key] != new_by_id[key] for key in old_by_id.keys() & new_by_id.keys())

        if not file_changed:
            log(f"Nessuna variazione nei dati (versione {version}, aggiornata il {updated_at}).")
            if args.publish:
                log("Nessun commit e nessun nuovo deployment: la pagina pubblicata resta valida.")
            return

        regenerate_site()
        if data_changed:
            log(f"Agenda aggiornata: +{added} nuovi, -{removed} rimossi, {revised} modificati.")
        else:
            log("Metadati tecnici dell'agenda normalizzati; dati dei lanci invariati.")

        if args.publish:
            publish_to_github("Aggiorna agenda SpaceX da The Space Devs", version)
        else:
            log("File locali aggiornati. Nessuna pubblicazione richiesta.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log(f"ERRORE: {exc}")
        sys.exit(1)
