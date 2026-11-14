# nexTOp · Luoghi e attività di Torino e provincia

Negozi, locali, servizi e attività della zona servita dalla rete **GTT** (Torino e
provincia), estratti ogni mese dal dataset aperto
[Overture Maps Places](https://docs.overturemaps.org/guides/places).

Sono i dati con cui l'app **nexTOp** trova anche i luoghi che mancano dalla mappa libera
di OpenStreetMap, per calcolare come arrivarci con i mezzi pubblici.

*Shops, venues and businesses in the area served by Turin's GTT public transport network,
extracted monthly from the open Overture Maps Places dataset.*

## Cosa c'è

| | |
|---|---|
| **Zona** | riquadro della rete GTT, latitudine 44,35–45,57 e longitudine 7,10–8,50 |
| **Luoghi** | circa 190.000, aperti e con affidabilità almeno 0,5 |
| **Aggiornamento** | il 3 di ogni mese, con l'ultima versione di Overture |
| **Download** | [`places.jsonl.gz`](../../releases/download/places/places.jsonl.gz) nella release [`places`](../../releases/tag/places) |
| **Indice** | [`latest.json`](latest.json): versione, numero di luoghi, impronta SHA-256, indirizzo del file |

## Formato

`places.jsonl.gz` è un file di testo compresso con gzip, con un oggetto JSON per riga. La
prima riga indica la versione di Overture, le altre sono i luoghi:

```json
{"release": "2026-10-21.0"}
{"id": "39c459aa-…", "n": "Bealab - Beauty Studio", "a": "Corso Giovanni Agnelli 52", "t": "Torino", "c": "personal_or_beauty_service", "y": 45.040119, "x": 7.646342, "k": 0.5}
```

| Campo | Contenuto |
|---|---|
| `id` | identificativo del luogo in Overture |
| `n` | nome |
| `a` | via e numero civico (può mancare) |
| `t` | comune |
| `c` | categoria di Overture (`basic_category`) |
| `y`, `x` | latitudine e longitudine |
| `k` | affidabilità indicata da Overture, da 0 a 1 |

## Come viene preparato

[`overture_places.py`](overture_places.py) legge con [DuckDB](https://duckdb.org) i file
pubblici di Overture e tiene i luoghi della zona. Rispetto all'originale:

- scarta i luoghi chiusi o con affidabilità sotto 0,5;
- scarta i nomi che sono solo un indirizzo;
- riscrive in forma normale indirizzi e comuni scritti in maiuscolo nei registri
  ("CORSO GIOVANNI AGNELLI 52" → "Corso Giovanni Agnelli 52", "TURIN" → "Torino").

L'estrazione la esegue ogni mese [GitHub Actions](.github/workflows/places.yml).

Per rifarla in locale:

```sh
pip install duckdb
python3 overture_places.py --out places.jsonl.gz
```

## Licenze

I dati vengono da **Overture Maps Foundation** e non contengono dati di OpenStreetMap.
Ogni luogo ha la licenza della sua fonte: **CDLA Permissive 2.0**, **Apache 2.0** o
**CC0 1.0**. I dettagli sono in [LICENSE-DATA.md](LICENSE-DATA.md).

I dati sono forniti «così come sono», senza garanzie di completezza o esattezza.
