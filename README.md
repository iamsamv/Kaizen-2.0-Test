# Kaizen 2.0 · Test

Prototipo dell'app Kaizen in un solo file (`index.html`), costruito dalle schermate del canvas di Claude Design.

## Aggiornare l'app
1. Scarica dal canvas i file `project/*.dc.html`, `project/kaizen-dati.js` e `artifact-type/dc-runtime.js` in una cartella.
2. Esegui (Python 3; per le icone serve `pip install fonttools brotli` e il file `material-symbols-outlined.woff2` del pacchetto npm `material-symbols` 0.47.5):

```
python3 tools/build.py CARTELLA_CANVAS material-symbols-outlined.woff2
```

## Carattere
Manrope è incluso nel file (`tools/fonts`, pacchetto npm `@fontsource-variable/manrope` 5.3.0, licenza OFL in `tools/fonts/MANROPE-OFL.txt`).

## Sul telefono
- Tema chiaro o scuro si sceglie nel Profilo. Su iPhone il colore della barra di stato (orologio, batteria) segue il tema dalla prossima apertura dell'app.
- L'app si adatta allo schermo e lascia libera la zona della tacca e della barra di stato.
- La barra di stato è opaca (nera con il tema scuro). Con la barra "trasparente" iOS 26 accorcia la finestra di un'app aggiunta alla Home e lascia una fascia nera in fondo (bug WebKit 301108). **Dopo questo cambio bisogna togliere l'app dalla Home e aggiungerla di nuovo**: iOS legge queste impostazioni solo quando la aggiungi.
- In orizzontale compare "Gira il telefono": su iPhone una web app aggiunta alla Home non può bloccare la rotazione; su Android, installata, resta in verticale (`manifest.webmanifest`).
