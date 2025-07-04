#!/bin/bash

# ==========================================
# Lynis Audit Script - Compatibile Debian 11
# ==========================================

# Nome dell'auditor
AUTHOR='Marius Berinde'

# Timestamp (formattato per usare nei nomi file)
TIME_OF_TEST=$(date '+%d-%m-%Y_%H-%M-%S')
# Nome file di output
OUTPUT="./lynis_audit_${TIME_OF_TEST}.txt"

# (Facoltativo) profilo personalizzato Lynis
# Decommenta e imposta il percorso corretto se vuoi usarlo
PROFILE="deb.prt"

echo "== Avvio dell'audit system con Lynis =="
echo "Data: $TIME_OF_TEST"
echo "Auditor: $AUTHOR"
echo "Output: $OUTPUT"
echo "----------------------------------------"

# Comando principale con filtro per rimuovere codici ANSI (usando perl)
if [[ -n "$PROFILE" && -f "$PROFILE" ]]; then
	lynis audit system --profile "$PROFILE" --quick --auditor "$AUTHOR"
else
	lynis audit system --quick --auditor "$AUTHOR"
	fi | perl -pe 's/\e\[[0-9;?]*[ -\/]*[@-~]//g' > "$OUTPUT"

# Verifica dell'esito
if [[ $? -eq 0 ]]; then
	echo "✅ Audit completato con successo."
	echo "📄 Report salvato in: $OUTPUT"
else
	echo "❌ Errore durante l'esecuzione di Lynis." >&2
	exit 1
fi

