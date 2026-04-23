#!/bin/bash
set -e
PROJECT_DIR=/var/www/de-cero-a-comediante
VENV=$PROJECT_DIR/venv

echo "=== Deploy De Cero a Comediante ==="

# 1. Traer cambios del repo
cd $PROJECT_DIR
git pull origin main

# 2. Instalar dependencias nuevas (si hay)
$VENV/bin/pip install -r backend/requirements.txt --quiet

# 3. Correr migraciones de BD
cd backend
../$VENV/bin/flask db upgrade

# 4. Reiniciar Gunicorn
systemctl restart dca

echo "=== Deploy completado ==="
systemctl status dca --no-pager
