# nexTOp — luoghi e attività

Negozi, locali e attività della zona della rete GTT (Torino e provincia) presi dal
dataset aperto [Overture Maps Places](https://docs.overturemaps.org/guides/places),
per la ricerca dell'app nexTOp quando la mappa libera (OpenStreetMap) non li ha.

- `overture_places.py` estrae i luoghi (DuckDB, lettura diretta dai file pubblici di
  Overture) e scrive `places.jsonl.gz`.
- `.github/workflows/places.yml` lo esegue il 3 di ogni mese (o a mano da *Actions ›
  Luoghi Overture › Run workflow*), pubblica il file nella release `places` e aggiorna
  `latest.json` (versione, numero di luoghi, impronta SHA-256, indirizzo del file).
- Il server di nexTOp legge `latest.json` ogni giorno e, se l'impronta è cambiata,
  scarica il file e lo importa.

## Prima pubblicazione (una volta)

1. Su GitHub crea un repository **pubblico** vuoto (es. `nextop-places`): per i repository
   pubblici GitHub Actions è gratuito.
2. Da questa cartella:
   ```sh
   git init -b main && git add . && git commit -m "Luoghi della zona GTT da Overture"
   git remote add origin https://github.com/<utente>/nextop-places.git && git push -u origin main
   ```
3. Su GitHub: *Settings › Actions › General › Workflow permissions* › «Read and write
   permissions» (serve per pubblicare la release e aggiornare `latest.json`).
4. *Actions › Luoghi Overture › Run workflow* per il primo file (circa 10 minuti), poi va da
   solo ogni mese.
5. Nel server, in `inc/config.php`:
   `'places' => ['feed_url' => 'https://raw.githubusercontent.com/<utente>/nextop-places/main/latest.json']`.

Licenze dei dati: [LICENSE-DATA.md](LICENSE-DATA.md).
