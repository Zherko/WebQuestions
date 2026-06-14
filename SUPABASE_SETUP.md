# Configuración rápida de Supabase

1) Obtener credenciales

- Entra en el panel de tu proyecto Supabase → Settings → API.
- Copia `URL` (SUPABASE_URL) y la `anon` key o la `service_role` key según lo que necesites.

2) Variables de entorno

- Copia `.env.example` a `.env` en la raíz del proyecto y pega tus valores.
- `SERVICE_ROLE_KEY` es sensible: no la publiques ni la subas al repo.
- El archivo `.gitignore` ya incluye `.env` para evitar subirlo.

3) Instalar herramientas (CLI y extensión VS Code)

- Instalar Supabase CLI (npm):

```bash
npm install -g supabase
```

- Alternativa (Windows): descarga el binario desde la release oficial si prefieres no usar npm.
- Instalar la extensión de VS Code (desde la línea de comandos):

```bash
code --install-extension supabase.supabase
```

4) Dependencias Python

- En `backend/requirements.txt` ya están listadas `supabase` y `python-dotenv`.
- Instala con pip en tu entorno virtual:

```bash
pip install -r backend/requirements.txt
```

5) Probar la conexión desde el proyecto

- Crea `.env` con tus credenciales y luego ejecuta (desde la raíz del proyecto):

```bash
python -c "from backend.supabase_client import fetch_questions; print(fetch_questions(5))"
```

Si todo está correcto verás la lista (posible vacía) de filas desde la tabla `questions`.

6) Uso en el backend

- Importa el cliente con `from backend.supabase_client import get_supabase`.
- Usa `get_supabase()` para operar con tablas, autenticación y storage.

7) Seguridad y despliegue

- En despliegues, configura las variables de entorno en la plataforma (no subas `.env`).
- Usa la `ANON` key en clientes públicos y la `SERVICE_ROLE_KEY` solo en backends de confianza.
