#!/usr/bin/env bash
set -euo pipefail
: "${MYSQL_HOST:=127.0.0.1}"
: "${MYSQL_PORT:=3306}"
: "${MYSQL_USER:=eduturnos}"
: "${MYSQL_DATABASE:=eduturnos}"
: "${BACKUP_DIR:=./backups}"
mkdir -p "$BACKUP_DIR"
mysqldump --host="$MYSQL_HOST" --port="$MYSQL_PORT" --user="$MYSQL_USER" --single-transaction --routines --triggers "$MYSQL_DATABASE" > "$BACKUP_DIR/eduturnos_$(date +%Y%m%d_%H%M%S).sql"
echo "Backup creado en $BACKUP_DIR"
