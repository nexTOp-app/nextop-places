#!/usr/bin/env python3
"""Luoghi e attività della zona della rete GTT da Overture Maps (dataset
aperto) per la ricerca dell'app nexTOp: negozi, locali, studi che
OpenStreetMap non ha.

Lo esegue ogni mese GitHub Actions (.github/workflows/places.yml), che
pubblica il file come release; il server di nexTOp lo scarica e lo importa da
solo. Una riga per luogo, dopo un'intestazione {"release": …}:

    {"id", "n": nome, "a": via e numero, "t": comune, "c": categoria,
     "y": latitudine, "x": longitudine, "k": affidabilità 0–1}

A mano (serve DuckDB: `pip install duckdb`):

    python3 overture_places.py [--release 2026-10-21.0] [--out places.jsonl.gz]

Senza --release usa l'ultima versione pubblicata di Overture.

Licenze dei dati (per luogo): CDLA Permissive 2.0, Apache 2.0, CC0. Nessun
dato di OpenStreetMap. Vedi LICENSE-DATA.md.
"""

import argparse
import gzip
import json
import re
import sys
import urllib.request

# Riquadro della rete GTT, come ServiceArea.network* nell'app.
MIN_LAT, MAX_LAT = 44.35, 45.57
MIN_LON, MAX_LON = 7.10, 8.50

# Affidabilità minima: sotto 0,5 soprattutto doppioni e attività chiuse. Il
# centro estetico che ha avviato il lavoro (registro aziendale) ha 0,5.
MIN_CONFIDENCE = 0.5

CATALOG = "https://stac.overturemaps.org/catalog.json"
BUCKET = "s3://overturemaps-us-west-2/release"

# Comuni scritti in inglese o in maiuscolo nei registri.
TOWN_FIX = {"turin": "Torino"}

# Parole che restano minuscole nei nomi di via ("Corso Giovanni Agnelli",
# "Via della Rocca").
SMALL = {"di", "del", "della", "delle", "dei", "degli", "dello", "da", "e",
         "al", "alla", "alle", "ai", "agli", "in", "sul", "sulla", "d", "l"}


def latest_release() -> str:
    with urllib.request.urlopen(CATALOG, timeout=30) as response:
        return json.load(response)["latest"]


def nice(text: str | None) -> str:
    """Testo in maiuscolo dei registri ("CORSO GIOVANNI AGNELLI 52") in forma
    normale; quello già scritto bene resta com'è."""
    if not text:
        return ""
    text = " ".join(text.split())
    if text != text.upper():
        return text
    words = []
    for i, word in enumerate(text.lower().split(" ")):
        words.append(word if i > 0 and word in SMALL else word[:1].upper() + word[1:])
    return " ".join(words)


def town(text: str | None) -> str:
    value = nice(text)
    return TOWN_FIX.get(value.lower(), value)


def looks_like_address(name: str) -> bool:
    """Nomi che sono solo un indirizzo ("Corso Giovanni Agnelli, 100/e")."""
    return re.match(
        r"^(via|corso|c\.so|piazza|p\.za|viale|largo|strada|str\.)\s", name.lower()
    ) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--release", help="versione di Overture (es. 2026-10-21.0)")
    parser.add_argument("--out", default="places.jsonl.gz")
    args = parser.parse_args()

    import duckdb  # solo qui: per --help non serve

    release = args.release or latest_release()
    print(f"Overture {release}: lettura della zona GTT…", file=sys.stderr)
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    rows = con.sql(f"""
        SELECT id, names.primary, addresses[1].freeform, addresses[1].locality,
               basic_category, bbox.ymin, bbox.xmin, confidence
        FROM read_parquet('{BUCKET}/{release}/theme=places/type=place/*',
                          hive_partitioning=1)
        WHERE bbox.xmin BETWEEN {MIN_LON} AND {MAX_LON}
          AND bbox.ymin BETWEEN {MIN_LAT} AND {MAX_LAT}
          AND confidence >= {MIN_CONFIDENCE}
          AND (operating_status IS NULL OR operating_status = 'open')
          AND names.primary IS NOT NULL
    """).fetchall()

    kept = 0
    with gzip.open(args.out, "wt", encoding="utf-8") as out:
        out.write(json.dumps({"release": release}) + "\n")
        for pid, name, address, locality, category, lat, lon, confidence in rows:
            name = " ".join(name.split())
            if len(name) < 2 or looks_like_address(name):
                continue
            out.write(json.dumps({
                "id": pid,
                "n": name[:200],
                "a": nice(address)[:200],
                "t": town(locality)[:100],
                "c": (category or "")[:60],
                "y": round(lat, 6),
                "x": round(lon, 6),
                "k": round(confidence, 2),
            }, ensure_ascii=False) + "\n")
            kept += 1
    print(f"{kept} luoghi in {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
