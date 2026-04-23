#!/bin/bash
set -e
echo "=== Setup De Cero a Comediante en Hostinger VPS ==="

# 1. Actualizar sistema
apt update && apt upgrade -y

# 2. Instalar dependencias del sistema
apt install -y python3.12 python3.12-venv python3-pip nginx certbot python3-certbot-nginx git curl

# 3. Crear directorio del proyecto
mkdir -p /var/www/de-cero-a-comediante
mkdir -p /var/log/gunicorn

# 4. Clonar el repo (ajustar URL)
git clone https://github.com/TU_USUARIO/de-cero-a-comediante.git /var/www/de-cero-a-comediante

# 5. Crear entorno virtual Python
python3.12 -m venv /var/www/de-cero-a-comediante/venv
/var/www/de-cero-a-comediante/venv/bin/pip install --upgrade pip
/var/www/de-cero-a-comediante/venv/bin/pip install -r /var/www/de-cero-a-comediante/backend/requirements.txt

# 6. Copiar y activar configuración Nginx
cp /var/www/de-cero-a-comediante/deploy/nginx.conf /etc/nginx/sites-available/dca
ln -sf /etc/nginx/sites-available/dca /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 7. Copiar y activar servicio systemd Gunicorn
cp /var/www/de-cero-a-comediante/deploy/gunicorn.service /etc/systemd/system/dca.service
systemctl daemon-reload
systemctl enable dca
systemctl start dca

# 8. Permisos
chown -R www-data:www-data /var/www/de-cero-a-comediante
chown -R www-data:www-data /var/log/gunicorn

echo ""
echo "=== PRÓXIMOS PASOS MANUALES ==="
echo "1. Copia tu .env al servidor: scp .env root@TU_IP:/var/www/de-cero-a-comediante/backend/.env"
echo "2. Corre las migraciones: cd /var/www/de-cero-a-comediante/backend && ../venv/bin/flask db upgrade"
echo "3. SSL con Certbot: certbot --nginx -d tudominio.com -d www.tudominio.com"
echo "4. Verifica el servicio: systemctl status dca"
