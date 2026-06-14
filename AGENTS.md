# Party Roulette — Agents.md

## Project Overview

**Party Roulette** (El Juego de Beber) es una app web PWA tipo party-game. Los jugadores crean una partida (2–12 jugadores), eligen genero (M/F/Any), y responden preguntas filtradas por categoria y genero. 20 rondas con temporizador de 30s. Sistema de puntuacion, castigos personalizables, y leaderboard.

## Tech Stack

| Capa | Tecnologia |
|------|-----------|
| **Frontend** | HTML5 + CSS3 + Vanilla JS (sin frameworks). Tailwind CSS v3 via CDN |
| **Backend** | Node.js + Express.js |
| **Base de datos** | PostgreSQL via Supabase (BaaS) |
| **Auth** | Supabase Auth (email/password, Google OAuth, Facebook OAuth) |
| **Pagos** | PayPal SDK (sandbox, server-side con webhooks) |
| **Hosting** | Hostinger Managed Node.js Hosting |
| **PWA** | manifest.json, beforeinstallprompt |
| **Graficos** | Chart.js v4 (dashboard) |
| **CDN** | jsDelivr, CDNJS |

## Estructura del Proyecto

```
/
├── public/                     # Archivos estaticos (frontend SPA)
│   ├── index.html              # App principal
│   ├── dashboard.html          # Panel admin con Chart.js
│   ├── insert_question.html    # Formulario para insertar preguntas
│   ├── terms.html              # Terminos y condiciones
│   ├── manifest.json           # PWA manifest
│   ├── favicon.png
│   └── icon-512.png
├── server.js                   # Servidor Express (entry point)
├── routes/
│   ├── questions.js            # Endpoints de preguntas
│   ├── payments.js             # PayPal server-side (create-order)
│   └── webhooks.js             # Webhook PayPal (capture)
├── services/
│   ├── supabase.js             # Cliente Supabase (service_role)
│   └── paypal.js               # PayPal SDK server-side
├── middleware/
│   └── auth.js                 # Middleware de autenticacion
├── package.json                # Dependencias Node.js
├── .env                        # Variables de entorno (gitignored)
├── .env.example                # Template de .env
├── plan.md                     # Plan de migracion
└── AGENTS.md                   # Este archivo
```

## Arquitectura

**SPA frontend** servida por Express, con **API REST** en los mismos endpoints. Navegacion por pantallas via `display: none/block`:

- `#setup-screen` — Configuracion de partida
- `#game-screen` — Juego activo (timer, pregunta, botones)
- `#end-screen` — Puntuacion final
- Modales: `#account-modal`, `#exit-modal`, `#custom-alert-modal`, `#custom-question-modal`, `#ios-install-modal`

El estado global se maneja con un objeto `gameState` en window.

## Base de Datos (PostgreSQL/Supabase)

**Tablas principales:**
- `questions` — id, text, category, difficulty, gender (M/F/null), created_at
- `profiles` — id (UUID ref auth.users), name, email, birth_date, games_available, total_score
- `scores` — id, user_id, score, mode, played_at
- `invitaciones` — remitente_id, email_invitado
- `user_submitted_questions` — preguntas enviadas por usuarios

## Convenciones de Codigo

- **No anadir comentarios** a menos que se solicite explicitamente
- **No anadir emojis** en el codigo
- Seguir el estilo existente: indentacion con 2 espacios, comillas dobles en JS, nombres de funciones en camelCase, IDs/clases en kebab-case
- El frontend usa Tailwind CSS con clases utilitarias (no CSS personalizado salvo estilos neon/glow)
- Los estilos neon se definen en el bloque `<style>` inline de cada HTML
- Las queries a Supabase se hacen directamente desde el frontend con la anon key (RLS policies)
- El backend usa service_role_key para operaciones privilegiadas

## Desarrollo Local

```bash
# Instalar dependencias
npm install

# Iniciar servidor en desarrollo
npm run dev

# Iniciar en produccion local
npm start

# Verificar health
curl http://localhost:3000/health
```

No hay test suite ni linter configurados. No hay type-checking.

## Variables de Entorno (`.env`)

```
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
PORT=3000
NODE_ENV=production
FRONTEND_ORIGIN=https://tudominio.com
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_CLIENT_SECRET=tu_paypal_client_secret
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=wh_...
```

En Hostinger las variables se configuran desde hPanel (no en `.env`).

## Despliegue (Hostinger)

```bash
# Crear zip excluyendo node_modules
zip -r deploy.zip . -x "node_modules/*" ".git/*" ".env"

# Desplegar via MCP (disponible en opencode)
# Usar: hostinger_hosting_deployJsApplication
```

Hostinger auto-detecta Express, ejecuta `npm install` y `npm start`.

## Notas para Agentes

- Todo el frontend esta en `public/index.html`
- Las pantallas se muestran/ocultan con clases `hidden` de Tailwind
- El `gameState` es un objeto global que persiste durante la sesion
- Las preguntas se filtran por categoria y compatibilidad de genero
- PayPal usa server-side SDK con webhooks (no client-side)
- Las queries a Supabase se hacen desde el frontend con anon key
- El backend usa service_role key para inserts/admin via API
- Despliegues via MCP: crear zip, llamar a `hostinger_hosting_deployJsApplication`
- No usar librerias npm en el frontend — todo via CDN
