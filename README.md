# Kaizen 2.0 · Test

Prototipo dell'app Kaizen in un solo file (`index.html`), costruito dalle schermate del canvas di Claude Design.

## Aggiornare l'app
1. Scarica dal canvas i file `project/*.dc.html`, `project/kaizen-dati.js` e `artifact-type/dc-runtime.js` in una cartella.
2. Esegui (Python 3; per le icone serve `pip install fonttools brotli` e il file `material-symbols-outlined.woff2` del pacchetto npm `material-symbols` 0.47.5):

```
python3 tools/build.py CARTELLA_CANVAS material-symbols-outlined.woff2
```

## Sul telefono
- L'app si adatta allo schermo e lascia libera la zona della tacca e della barra di stato.
- In orizzontale compare "Gira il telefono": su iPhone una web app aggiunta alla Home non può bloccare la rotazione; su Android, installata, resta in verticale (`manifest.webmanifest`).
