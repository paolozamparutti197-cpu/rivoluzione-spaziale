import requests
import html
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from pathlib import Path


API_BASE = "https://ll.thespacedevs.com/2.3.0/launches/upcoming/"


PROVIDERS = {
    "SpaceX": {
        "lsp_name": "SpaceX",
        "filename": "lanci_spacex.html"
    },
    "United Launch Alliance": {
        "lsp_name": "United Launch Alliance",
        "filename": "lanci_ula.html"
    },
    "Rocket Lab": {
        "lsp_name": "Rocket Lab",
        "filename": "lanci_rocket_lab.html"
    },
    "Blue Origin": {
        "lsp_name": "Blue Origin",
        "filename": "lanci_blue_origin.html"
    },
    "Arianespace": {
        "lsp_name": "Arianespace",
        "filename": "lanci_arianespace.html"
    },
    "China Aerospace Science and Technology Corporation": {
        "lsp_name": "China Aerospace Science and Technology Corporation",
        "filename": "lanci_casc.html"
    },
    "Indian Space Research Organization": {
        "lsp_name": "Indian Space Research Organization",
        "filename": "lanci_isro.html"
    },
    "Japan Aerospace Exploration Agency": {
        "lsp_name": "Japan Aerospace Exploration Agency",
        "filename": "lanci_jaxa.html"
    },
    "Mitsubishi Heavy Industries": {
        "lsp_name": "Mitsubishi Heavy Industries",
        "filename": "lanci_mhi.html"
    },
    "Russian Federal Space Agency (ROSCOSMOS)": {
        "lsp_name": "Russian Federal Space Agency (ROSCOSMOS)",
        "filename": "lanci_roscosmos.html"
    },
    "Northrop Grumman Innovation Systems": {
        "lsp_name": "Northrop Grumman Innovation Systems",
        "filename": "lanci_northrop_grumman.html"
    },
    "Firefly Aerospace": {
        "lsp_name": "Firefly Aerospace",
        "filename": "lanci_firefly.html"
    },
    "Relativity Space": {
        "lsp_name": "Relativity Space",
        "filename": "lanci_relativity.html"
    },
    "Astra Space": {
        "lsp_name": "Astra Space",
        "filename": "lanci_astra.html"
    },
    "ABL Space Systems": {
        "lsp_name": "ABL Space Systems",
        "filename": "lanci_abl.html"
    },
    "Galactic Energy": {
        "lsp_name": "Galactic Energy",
        "filename": "lanci_galactic_energy.html"
    },
    "CAS Space": {
        "lsp_name": "CAS Space",
        "filename": "lanci_cas_space.html"
    },
    "LandSpace": {
        "lsp_name": "LandSpace",
        "filename": "lanci_landspace.html"
    },
    "ExPace": {
        "lsp_name": "ExPace",
        "filename": "lanci_expace.html"
    },
    "i-Space": {
        "lsp_name": "i-Space",
        "filename": "lanci_i_space.html"
    },
    "PLD Space": {
        "lsp_name": "PLD Space",
        "filename": "lanci_pld_space.html"
    },
    "Korea Aerospace Research Institute": {
        "lsp_name": "Korea Aerospace Research Institute",
        "filename": "lanci_kari.html"
    },
    "Iran Space Agency": {
        "lsp_name": "Iran Space Agency",
        "filename": "lanci_iran_space_agency.html"
    }
}


def safe_get(dct, *keys, default=""):
    cur = dct
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def slugify_filename(name):
    cleaned = name.lower()
    cleaned = cleaned.replace(" ", "_")
    cleaned = cleaned.replace("/", "_")
    cleaned = cleaned.replace("\\", "_")
    cleaned = cleaned.replace("(", "")
    cleaned = cleaned.replace(")", "")
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("-", "_")
    cleaned = "".join(ch for ch in cleaned if ch.isalnum() or ch == "_")
    return f"lanci_{cleaned}.html"


def fetch_launches(provider_lsp_name, max_launches=100):
    launches = []
    limit = 25
    offset = 0

    while len(launches) < max_launches:
        params = {
            "format": "json",
            "mode": "detailed",
            "lsp__name": provider_lsp_name,
            "ordering": "net",
            "limit": limit,
            "offset": offset
        }

        response = requests.get(API_BASE, params=params, timeout=30)

        if response.status_code == 404:
            raise RuntimeError(
                "Endpoint non trovato. L'endpoint corretto è: "
                "https://ll.thespacedevs.com/2.3.0/launches/upcoming/"
            )

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


def parse_iso_date(date_string):
    if not date_string:
        return None

    try:
        return datetime.fromisoformat(date_string.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def format_date_utc(date_string):
    dt = parse_iso_date(date_string)
    if dt is None:
        return "Data non disponibile"
    return dt.strftime("%d/%m/%Y %H:%M UTC")


def is_fixed_enough(launch):
    net = launch.get("net")
    if not net:
        return False
    return parse_iso_date(net) is not None


def esc(value):
    return html.escape(str(value or ""), quote=True)


def extract_launch_row(launch):
    name = launch.get("name", "")
    net = launch.get("net", "")
    window_start = launch.get("window_start", "")
    window_end = launch.get("window_end", "")

    status = safe_get(launch, "status", "name")
    status_description = safe_get(launch, "status", "description")

    provider = safe_get(launch, "launch_service_provider", "name")

    rocket = safe_get(launch, "rocket", "configuration", "full_name")
    if not rocket:
        rocket = safe_get(launch, "rocket", "configuration", "name")

    mission_name = safe_get(launch, "mission", "name")
    mission_type = safe_get(launch, "mission", "type")
    orbit = safe_get(launch, "mission", "orbit", "name")
    mission_description = safe_get(launch, "mission", "description")

    pad = safe_get(launch, "pad", "name")
    location = safe_get(launch, "pad", "location", "name")

    webcast_live = launch.get("webcast_live")
    image = launch.get("image")
    info_url = launch.get("url")

    return {
        "name": name,
        "net": net,
        "net_formatted": format_date_utc(net),
        "window_start": format_date_utc(window_start) if window_start else "",
        "window_end": format_date_utc(window_end) if window_end else "",
        "status": status,
        "status_description": status_description,
        "provider": provider,
        "rocket": rocket,
        "mission_name": mission_name,
        "mission_type": mission_type,
        "orbit": orbit,
        "mission_description": mission_description,
        "pad": pad,
        "location": location,
        "webcast_live": webcast_live,
        "image": image,
        "info_url": info_url
    }


def generate_html(provider_label, launches):
    generated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    rows = []
    countdown_data = []

    for idx, launch in enumerate(launches, start=1):
        row = extract_launch_row(launch)

        countdown_id = f"countdown_{idx}"
        details_id = f"details_{idx}"

        countdown_data.append({
            "id": countdown_id,
            "net": row["net"],
            "name": row["name"]
        })

        image_html = ""
        if row["image"]:
            image_html = f"""
            <img class="mission-img" src="{esc(row["image"])}" alt="Immagine missione">
            """

        description_html = ""
        if row["mission_description"]:
            description_html = f"""
            <div class="details-block">
                <strong>Descrizione missione</strong>
                <p>{esc(row["mission_description"])}</p>
            </div>
            """

        status_description_html = ""
        if row["status_description"]:
            status_description_html = f"""
            <div class="details-block">
                <strong>Nota sullo stato</strong>
                <p>{esc(row["status_description"])}</p>
            </div>
            """

        info_link_html = ""
        if row["info_url"]:
            info_link_html = f"""
            <a href="{esc(row["info_url"])}" target="_blank" rel="noopener noreferrer">
                Scheda The Space Devs
            </a>
            """

        webcast_html = ""
        if row["webcast_live"] is not None:
            webcast_html = f"""
            <span>Webcast live previsto: {esc(row["webcast_live"])}</span>
            """

        rows.append(f"""
        <tr>
            <td data-label="#">{idx}</td>

            <td data-label="Missione">
                <button class="mission-button" onclick="toggleDetails('{details_id}')">
                    {esc(row["name"])}
                </button>

                <div id="{details_id}" class="details">
                    {image_html}

                    <div class="details-grid">
                        <div><strong>Missione:</strong> {esc(row["mission_name"])}</div>
                        <div><strong>Tipo missione:</strong> {esc(row["mission_type"])}</div>
                        <div><strong>Orbita:</strong> {esc(row["orbit"])}</div>
                        <div><strong>Provider:</strong> {esc(row["provider"])}</div>
                        <div><strong>Razzo:</strong> {esc(row["rocket"])}</div>
                        <div><strong>Pad:</strong> {esc(row["pad"])}</div>
                        <div><strong>Località:</strong> {esc(row["location"])}</div>
                        <div><strong>Finestra inizio:</strong> {esc(row["window_start"])}</div>
                        <div><strong>Finestra fine:</strong> {esc(row["window_end"])}</div>
                    </div>

                    {description_html}
                    {status_description_html}

                    <div class="links">
                        {info_link_html}
                        {webcast_html}
                    </div>
                </div>
            </td>

            <td data-label="Data NET">{esc(row["net_formatted"])}</td>
            <td data-label="Stato">{esc(row["status"])}</td>
            <td data-label="Razzo">{esc(row["rocket"])}</td>
            <td data-label="Pad">{esc(row["pad"])}</td>
            <td data-label="Località">{esc(row["location"])}</td>
            <td data-label="Countdown" id="{countdown_id}" class="countdown">Calcolo...</td>
        </tr>
        """)

    countdown_json = json.dumps(countdown_data, ensure_ascii=False)

    html_doc = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Lanci {esc(provider_label)} - The Space Devs</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    body {{
        margin: 0;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #0d1117;
        color: #e6edf3;
    }}

    header {{
        padding: 28px 32px;
        background: linear-gradient(135deg, #111827, #1f2937);
        border-bottom: 1px solid #30363d;
    }}

    h1 {{
        margin: 0 0 8px 0;
        font-size: 28px;
    }}

    .subtitle {{
        color: #9ca3af;
        font-size: 15px;
    }}

    main {{
        padding: 24px 32px 48px 32px;
    }}

    .note {{
        margin-bottom: 20px;
        padding: 14px 16px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        color: #c9d1d9;
        line-height: 1.45;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        overflow: hidden;
    }}

    th, td {{
        padding: 12px 14px;
        border-bottom: 1px solid #30363d;
        vertical-align: top;
        font-size: 14px;
    }}

    th {{
        background: #21262d;
        text-align: left;
        color: #f0f6fc;
        position: sticky;
        top: 0;
        z-index: 2;
    }}

    tr:hover {{
        background: #1c2128;
    }}

    .mission-button {{
        background: none;
        border: none;
        color: #58a6ff;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        text-align: left;
        padding: 0;
    }}

    .mission-button:hover {{
        text-decoration: underline;
    }}

    .countdown {{
        font-weight: 700;
        color: #7ee787;
        min-width: 170px;
    }}

    .launched {{
        color: #ff7b72;
    }}

    .details {{
        display: none;
        margin-top: 12px;
        padding: 14px;
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 10px;
        color: #c9d1d9;
    }}

    .details-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 8px 16px;
        margin-bottom: 12px;
    }}

    .details-block {{
        margin-top: 12px;
    }}

    .details-block p {{
        margin: 6px 0 0 0;
        line-height: 1.45;
    }}

    .links {{
        margin-top: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        color: #9ca3af;
    }}

    a {{
        color: #58a6ff;
    }}

    .mission-img {{
        max-width: 260px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
    }}

    @media (max-width: 900px) {{
        main {{
            padding: 16px;
        }}

        table, thead, tbody, th, td, tr {{
            display: block;
        }}

        thead {{
            display: none;
        }}

        tr {{
            margin-bottom: 16px;
            border: 1px solid #30363d;
            border-radius: 12px;
            overflow: hidden;
        }}

        td {{
            border-bottom: 1px solid #30363d;
        }}

        td::before {{
            content: attr(data-label);
            display: block;
            color: #9ca3af;
            font-size: 12px;
            margin-bottom: 4px;
        }}
    }}
</style>
</head>

<body>
<header>
    <h1>Lanci {esc(provider_label)}</h1>
    <div class="subtitle">
        Dati scaricati da The Space Devs, Launch Library 2. Generato il {esc(generated_at)}.
    </div>
</header>

<main>
    <div class="note">
        Questa pagina è statica: i dati sono quelli scaricati al momento della generazione.
        Il conto alla rovescia viene calcolato dal browser in tempo reale.
        Le date sono in UTC. Una data NET è una previsione operativa, non una promessa divina.
    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Missione</th>
                <th>Data NET</th>
                <th>Stato</th>
                <th>Razzo</th>
                <th>Pad</th>
                <th>Località</th>
                <th>Countdown</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
</main>

<script>
const countdowns = {countdown_json};

function toggleDetails(id) {{
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = el.style.display === "block" ? "none" : "block";
}}

function formatCountdown(distanceMs) {{
    if (distanceMs <= 0) {{
        return "Lancio già avvenuto o finestra iniziata";
    }}

    const totalSeconds = Math.floor(distanceMs / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${{days}}g ${{hours}}h ${{minutes}}m ${{seconds}}s`;
}}

function updateCountdowns() {{
    const now = new Date();

    countdowns.forEach(item => {{
        const el = document.getElementById(item.id);
        if (!el) return;

        const target = new Date(item.net);
        const distance = target - now;

        el.textContent = formatCountdown(distance);

        if (distance <= 0) {{
            el.classList.add("launched");
        }}
    }});
}}

updateCountdowns();
setInterval(updateCountdowns, 1000);
</script>

</body>
</html>
"""

    return html_doc


def generate_file(provider_label, provider_lsp_name, output_filename):
    launches = fetch_launches(provider_lsp_name, max_launches=100)
    fixed_launches = [launch for launch in launches if is_fixed_enough(launch)]

    if not fixed_launches:
        raise RuntimeError(
            f"Nessun lancio con data utilizzabile trovato per: {provider_lsp_name}"
        )

    html_doc = generate_html(provider_label, fixed_launches)

    output_path = Path(output_filename)
    output_path.write_text(html_doc, encoding="utf-8")

    return output_path.resolve(), len(launches), len(fixed_launches)


def on_provider_change(event=None):
    selected = provider_var.get()

    if selected == "Altro provider manuale":
        manual_entry.config(state="normal")
        manual_entry.focus()
    else:
        manual_entry.delete(0, tk.END)
        manual_entry.config(state="disabled")


def on_generate():
    selected = provider_var.get()

    if not selected:
        messagebox.showwarning("Selezione mancante", "Seleziona un provider.")
        return

    if selected == "Altro provider manuale":
        provider_lsp_name = manual_entry.get().strip()

        if not provider_lsp_name:
            messagebox.showwarning(
                "Nome mancante",
                "Inserisci il nome esatto del provider da cercare."
            )
            return

        provider_label = provider_lsp_name
        output_filename = slugify_filename(provider_lsp_name)

    else:
        provider_data = PROVIDERS[selected]
        provider_label = selected
        provider_lsp_name = provider_data["lsp_name"]
        output_filename = provider_data["filename"]

    generate_button.config(state="disabled")
    status_var.set(f"Scarico i dati per {provider_label}...")
    root.update_idletasks()

    try:
        output_path, total_found, fixed_found = generate_file(
            provider_label,
            provider_lsp_name,
            output_filename
        )

        status_var.set(
            f"Fatto. Lanci trovati: {total_found}. "
            f"Lanci con data utilizzabile: {fixed_found}."
        )

        messagebox.showinfo(
            "HTML creato",
            f"File creato:\n{output_path}\n\n"
            f"Lanci trovati dall'API: {total_found}\n"
            f"Lanci con data utilizzabile: {fixed_found}\n\n"
            "Apri il file HTML con doppio clic."
        )

    except Exception as exc:
        status_var.set("Errore.")
        messagebox.showerror("Errore", str(exc))

    finally:
        generate_button.config(state="normal")


root = tk.Tk()
root.title("Generatore lanci spaziali, The Space Devs")
root.geometry("620x300")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(
    main_frame,
    text="Generatore HTML dei lanci spaziali",
    font=("Segoe UI", 16, "bold")
)
title_label.pack(anchor="w", pady=(0, 8))

description_label = ttk.Label(
    main_frame,
    text=(
        "Seleziona un provider dal menu a tendina. "
        "Il programma scarica i lanci futuri e crea un HTML tabellare con countdown."
    ),
    wraplength=560
)
description_label.pack(anchor="w", pady=(0, 16))

provider_var = tk.StringVar()

provider_names = list(PROVIDERS.keys())
provider_names.append("Altro provider manuale")

provider_combo = ttk.Combobox(
    main_frame,
    textvariable=provider_var,
    values=provider_names,
    state="readonly",
    width=58
)
provider_combo.pack(anchor="w", pady=(0, 10))
provider_combo.bind("<<ComboboxSelected>>", on_provider_change)

provider_combo.set("SpaceX")

manual_label = ttk.Label(
    main_frame,
    text="Provider manuale, usa il nome esatto presente in The Space Devs:"
)
manual_label.pack(anchor="w")

manual_entry = ttk.Entry(main_frame, width=62)
manual_entry.pack(anchor="w", pady=(4, 14))
manual_entry.config(state="disabled")

generate_button = ttk.Button(
    main_frame,
    text="Genera HTML",
    command=on_generate
)
generate_button.pack(anchor="w", pady=(0, 14))

status_var = tk.StringVar()
status_var.set("Pronto.")

status_label = ttk.Label(
    main_frame,
    textvariable=status_var,
    foreground="#555555"
)
status_label.pack(anchor="w")

root.mainloop()