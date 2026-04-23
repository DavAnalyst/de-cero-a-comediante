# De Cero a Comediante — LMS de Stand-Up Comedy

Plataforma de aprendizaje para el curso profesional de stand-up comedy. Backend Flask + Frontend HTML/CSS/JS vanilla. Deploy en Hostinger VPS con Gunicorn + Nginx.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12, Flask, SQLAlchemy, Flask-Migrate |
| Base de datos | MySQL (Hostinger hPanel) |
| Frontend | HTML5, CSS3, JavaScript Vanilla |
| Videos | Cloudinary (dev) → Bunny.net (prod) |
| Pagos | Wompi (Colombia) |
| Auth | JWT (PyJWT + bcrypt) |
| Email | SendGrid |
| Servidor | Gunicorn + Nginx + systemd (Ubuntu 22.04) |

---

## Correr localmente

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales

# Inicializar base de datos
export FLASK_APP=run.py
export FLASK_ENV=development
flask db init       # Solo la primera vez
flask db migrate -m "initial"
flask db upgrade

# Correr el servidor de desarrollo
flask run
# → http://localhost:5000
```

### 2. Frontend

El frontend es HTML estático. Abre los archivos directamente en el navegador **o** usa un servidor estático simple:

```bash
cd frontend
python3 -m http.server 3000
# → http://localhost:3000
```

> En desarrollo, Nginx no está corriendo. Para que el frontend hable con el backend, abre `js/api.js` y cambia temporalmente `BASE_URL` a `http://localhost:5000/api`.

### 3. Correr tests

```bash
cd backend
pytest tests/ -v
```

Los tests usan `sqlite:///:memory:` — no necesitas MySQL para correr el CI.

---

## Crear el primer usuario admin

```bash
cd backend
source venv/bin/activate
flask shell
```

```python
from app.extensions import db, bcrypt
from app.models import User

admin = User(
    email="admin@tudominio.com",
    name="Admin",
    password_hash=bcrypt.generate_password_hash("TU_PASSWORD_SEGURO").decode(),
    is_admin=True,
)
db.session.add(admin)
db.session.commit()
print("Admin creado:", admin.id)
```

---

## Setup inicial en Hostinger VPS

### Requisitos previos

1. VPS Ubuntu 22.04 con acceso SSH root
2. Dominio apuntando a la IP del VPS (registros A)
3. Base de datos MySQL creada en Hostinger hPanel:
   - Ve a **hPanel → Bases de datos → MySQL**
   - Crea una BD, un usuario y asigna todos los permisos
   - Anota: `usuario`, `password`, `nombre_bd`
   - El host es siempre `localhost` desde el mismo VPS

### Obtener credenciales MySQL de Hostinger hPanel

1. Inicia sesión en [hPanel](https://hpanel.hostinger.com)
2. Selecciona tu hosting / VPS
3. Ve a **Bases de datos → MySQL**
4. Crea nueva base de datos → guarda el nombre (`u123456789_nombre`)
5. Crea usuario MySQL → guarda usuario y contraseña
6. Asocia el usuario a la BD con todos los privilegios
7. Tu `DATABASE_URL` será:
   ```
   mysql+pymysql://u123456789_usuario:PASSWORD@localhost:3306/u123456789_nombre
   ```

### Instalación desde cero

```bash
# En tu máquina local — copiar el .env al VPS
scp backend/.env root@TU_IP:/tmp/.env

# Conectar al VPS
ssh root@TU_IP

# Clonar repo y correr el setup
git clone https://github.com/TU_USUARIO/de-cero-a-comediante.git /tmp/setup
bash /tmp/setup/deploy/setup_server.sh

# Mover el .env al lugar correcto
mv /tmp/.env /var/www/de-cero-a-comediante/backend/.env

# Correr migraciones
cd /var/www/de-cero-a-comediante/backend
../venv/bin/flask db upgrade

# Instalar SSL
certbot --nginx -d tudominio.com -d www.tudominio.com

# Verificar
systemctl status dca
curl http://tudominio.com/api/health
```

---

## Deploy de actualizaciones

### Manual (SSH)

```bash
ssh root@TU_IP
bash /var/www/de-cero-a-comediante/deploy/deploy.sh
```

### Automático con GitHub Actions

Cada push a `main` ejecuta:
1. `pytest tests/ -v` contra SQLite en memoria
2. Si los tests pasan → SSH al VPS y corre `deploy.sh`

**Secrets necesarios en GitHub** → Settings → Secrets and variables → Actions:

| Secret | Valor |
|--------|-------|
| `VPS_HOST` | IP pública del VPS (ej. `185.12.34.56`) |
| `VPS_USER` | `root` o el usuario SSH configurado |
| `VPS_SSH_KEY` | Clave SSH privada (la pública debe estar en `~/.ssh/authorized_keys` del VPS) |

---

## Variables de entorno

Ver [backend/.env.example](backend/.env.example) para la lista completa documentada.

---

## Estructura del proyecto

```
de-cero-a-comediante/
├── backend/
│   ├── app/
│   │   ├── __init__.py        Flask factory
│   │   ├── extensions.py      db, migrate, bcrypt
│   │   ├── models.py          User, Course, Lesson, Progress, Purchase
│   │   ├── config.py          dev/prod/testing
│   │   ├── routes/            auth, courses, lessons, progress, payments, admin
│   │   ├── services/          video (Cloudinary/Bunny), wompi, email
│   │   └── utils/auth.py      @require_auth, @require_admin
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── index.html             Landing page
│   ├── login.html             Login / registro
│   ├── dashboard.html         Vista del estudiante
│   ├── lesson.html            Video player
│   ├── checkout.html          Pago Wompi
│   ├── admin.html             Panel admin
│   ├── css/
│   └── js/
├── deploy/
│   ├── nginx.conf
│   ├── gunicorn.service
│   ├── setup_server.sh
│   └── deploy.sh
└── .github/workflows/deploy.yml
```

---

## API Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/register` | No | Crear cuenta |
| POST | `/api/auth/login` | No | Login → JWT |
| GET | `/api/auth/me` | JWT | Usuario actual |
| GET | `/api/courses` | No | Lista cursos publicados |
| GET | `/api/courses/<id>` | Opcional | Detalle del curso |
| GET | `/api/courses/<id>/lessons` | JWT + inscrito | Lecciones con progreso |
| GET | `/api/lessons/<id>` | JWT + inscrito | Lección + URL firmada |
| GET | `/api/progress` | JWT | Progreso del usuario |
| POST | `/api/progress` | JWT | Actualizar progreso |
| POST | `/api/checkout/wompi` | JWT | Iniciar pago |
| POST | `/api/webhook/wompi` | Pública* | Confirmación de pago |
| GET/POST | `/api/admin/courses` | Admin | CRUD cursos |
| GET/POST | `/api/admin/lessons` | Admin | CRUD lecciones |
| GET | `/api/admin/users` | Admin | Lista usuarios |

*El webhook valida firma HMAC-SHA256 con `WOMPI_EVENTS_SECRET`

---

## Comandos útiles en producción

```bash
# Ver logs en tiempo real
journalctl -u dca -f

# Ver logs de acceso Nginx
tail -f /var/log/gunicorn/dca_access.log

# Reiniciar servicio
systemctl restart dca

# Recargar Nginx sin downtime
systemctl reload nginx

# Estado del servicio
systemctl status dca
```
