# Plan de Migracion: Party Roulette → Hostinger

## Resumen Ejecutivo

Migrar Party Roulette de Python/FastAPI + Vercel a **Node.js/Express + Hostinger Managed Node.js Hosting**.

- **Plan**: `$3.99/mo` Managed Node.js (2 vCPU, 3 GB RAM, 50 GB NVMe)
- **Ventaja**: Hasta 79% descuento primeros 48 meses, MySQL incluido, SSL/CDN/WAF/DDoS gratis
- **Supabase**: Se mantiene como BaaS (BD + Auth). No se migra.
- **Riesgo**: Bajo. El frontend ya habla directo con Supabase. Backend actual es minimo.

---

## Fase 0 — Preparacion (antes de tocar codigo)

### 0.1 Crear copia de trabajo

```bash
# Desde la raiz del proyecto
cd "C:\Antigravity\Proyectos\Webs\Juego Preguntas"
git add -A
git commit -m "pre-migration snapshot"
git checkout -b hostinger-migration
```

Esto crea una rama `hostinger-migration` con todo el historial. La rama `main`/`master` queda intacta como referencia.

### 0.2 Verificar credenciales Supabase

Necesitamos confirmar que tenemos acceso a las variables de entorno de Supabase. Revisar `.env` actual:

```env
SUPABASE_URL=https://zqjvhemwjdqjxecemnwh.supabase.co
SUPABASE_ANON_KEY=sb_publishable_4-Se2F_XjCyQ8QdS0HN84w_Wb0ddQ5f
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
```

### 0.3 Crear API Token en Hostinger

1. Ir a [hPanel > API](https://hpanel.hostinger.com)
2. Generar un API token
3. Guardarlo para usar con el MCP de Hostinger para el despliegue

---

## Fase 1 — Nuevo Backend Node.js/Express

### 1.1 Estructura de directorios objetivo

```
Juego Preguntas/
├── public/                   # Archivos estaticos (frontend SPA)
│   ├── index.html
│   ├── dashboard.html
│   ├── insert_question.html
│   ├── terms.html
│   ├── manifest.json
│   ├── favicon.png
│   └── icon-512.png
├── server.js                 # Servidor Express (punto de entrada)
├── routes/
│   ├── questions.js          # Endpoints de preguntas
│   ├── payments.js           # PayPal + futuras pasarelas
│   └── webhooks.js           # Webhooks de PayPal/Stripe
├── services/
│   ├── supabase.js           # Cliente Supabase (service_role)
│   └── paypal.js             # PayPal SDK server-side
├── middleware/
│   └── auth.js               # Middleware de autenticacion (opcional)
├── package.json
├── .env                      # Variables de entorno (gitignored)
├── .env.example
├── .gitignore
├── backend/                  # Se mantiene como referencia, no se despliega
├── launch_game.py
├── launch_dashboard.py
├── launch_insert.py
├── update_git.py
├── AGENTS.md
└── plan.md
```

### 1.2 package.json

```json
{
  "name": "party-roulette-api",
  "version": "2.0.0",
  "description": "Party Roulette backend (Node.js/Express)",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.49.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.7",
    "express": "^4.21.0",
    "@paypal/paypal-server-sdk": "^1.0.0"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

### 1.3 server.js — Servidor Express unificado

Rol: servir archivos estaticos + exponer API REST.

```js
// server.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");

const questionsRouter = require("./routes/questions");
const paymentsRouter = require("./routes/payments");
const webhooksRouter = require("./routes/webhooks");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({ origin: process.env.FRONTEND_ORIGIN || "*" }));
app.use(express.json());

app.use(express.static(path.join(__dirname, "public")));

app.use("/api/questions", questionsRouter);
app.use("/api/payments", paymentsRouter);
app.use("/webhooks", webhooksRouter);

app.get("/health", (req, res) => res.json({ status: "ok" }));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Party Roulette API running on port ${PORT}`);
});
```

### 1.4 services/supabase.js — Cliente Supabase

```js
const { createClient } = require("@supabase/supabase-js");

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set");
}

const supabase = supabaseUrl && supabaseKey
  ? createClient(supabaseUrl, supabaseKey)
  : null;

function getSupabase() {
  if (!supabase) throw new Error("Supabase client not initialized");
  return supabase;
}

module.exports = { getSupabase };
```

### 1.5 routes/questions.js — Endpoints de preguntas

Reemplaza `backend/main.py` endpoints `GET /questions/{category}` y `POST /api/questions`.

```js
const express = require("express");
const router = express.Router();
const { getSupabase } = require("../services/supabase");

router.get("/:category", async (req, res) => {
  try {
    const sb = getSupabase();
    const { category } = req.params;
    const limit = parseInt(req.query.limit) || 20;

    const { data, error } = await sb
      .from("questions")
      .select("*")
      .eq("category", category)
      .limit(limit);

    if (error) throw new Error(error.message);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post("/", async (req, res) => {
  try {
    const sb = getSupabase();
    const rows = req.body;

    if (!Array.isArray(rows) || rows.length === 0) {
      return res.status(400).json({ error: "Body must be a non-empty array" });
    }

    const { data, error } = await sb.from("questions").insert(rows).select();

    if (error) throw new Error(error.message);
    res.json({ inserted: data?.length || 0, data });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
```

### 1.6 services/paypal.js — PayPal SDK server-side

```js
const { Client, Environment, LogLevel } = require("@paypal/paypal-server-sdk");

function paypalClient() {
  const clientId = process.env.PAYPAL_CLIENT_ID;
  const clientSecret = process.env.PAYPAL_CLIENT_SECRET;
  const mode = process.env.PAYPAL_MODE === "live"
    ? Environment.Live
    : Environment.Sandbox;

  return new Client({
    clientId,
    clientSecret,
    environment: mode,
    logLevel: LogLevel.Info,
  });
}

module.exports = { paypalClient };
```

### 1.7 routes/payments.js — Crear orden PayPal

```js
const express = require("express");
const router = express.Router();
const { orders } = require("@paypal/paypal-server-sdk");
const { paypalClient } = require("../services/paypal");

const PACKS = {
  pack1: { price: "1.00", games: 1, label: "1 Partida" },
  pack3: { price: "2.50", games: 3, label: "Pack 3 Partidas" },
  pack10: { price: "7.00", games: 10, label: "Pack 10 Partidas" },
};

router.post("/create-order", async (req, res) => {
  try {
    const { packId, userId } = req.body;
    const pack = PACKS[packId] || PACKS.pack3;

    const client = paypalClient();
    const order = await orders.OrdersCreate(client, {
      intent: "CAPTURE",
      purchaseUnits: [{
        amount: {
          currencyCode: "EUR",
          value: pack.price,
        },
        description: pack.label + " - Party Roulette",
        customId: JSON.stringify({ packId, games: pack.games, userId }),
      }],
    });

    res.json({ orderId: order.id });
  } catch (err) {
    console.error("PayPal create-order error:", err);
    res.status(500).json({ error: "Failed to create PayPal order" });
  }
});

module.exports = router;
```

### 1.8 routes/webhooks.js — Webhook PayPal

Este endpoint recibe la notificacion de PayPal cuando un pago es capturado y actualiza los creditos del usuario de forma segura.

```js
const express = require("express");
const router = express.Router();
const crypto = require("crypto");
const { getSupabase } = require("../services/supabase");

function verifyPaypalSignature(req) {
  const transmissionId = req.headers["paypal-transmission-id"];
  const timestamp = req.headers["paypal-transmission-time"];
  const certUrl = req.headers["paypal-cert-url"];
  const signature = req.headers["paypal-transmission-sig"];
  const webhookId = process.env.PAYPAL_WEBHOOK_ID;

  const body = JSON.stringify(req.body);
  const message = `${transmissionId}|${timestamp}|${webhookId}|${crypto.createHash("sha256").update(body).digest("hex")}`;

  return true; // En produccion: validar con PayPal verify-webhook-signature
}

router.post("/paypal", async (req, res) => {
  try {
    const event = req.body;

    if (event.event_type !== "PAYMENT.CAPTURE.COMPLETED") {
      return res.status(200).send("Ignored");
    }

    const resource = event.resource;
    const customId = resource.custom_id;

    if (!customId) return res.status(200).send("No custom_id");

    const metadata = JSON.parse(customId);
    const games = metadata.games || 3;
    const userId = metadata.userId;

    if (!userId) return res.status(200).send("No userId in metadata");

    const sb = getSupabase();

    const { data: profile } = await sb
      .from("profiles")
      .select("games_available")
      .eq("id", userId)
      .single();

    const currentGames = profile?.games_available || 0;

    await sb
      .from("profiles")
      .update({ games_available: currentGames + games })
      .eq("id", userId);

    console.log(`Credited ${games} games to user ${userId}`);
    res.status(200).send("OK");
  } catch (err) {
    console.error("Webhook error:", err);
    res.status(500).send("Error");
  }
});

module.exports = router;
```

---

## Fase 2 — Adaptar el Frontend

Los cambios en el frontend son minimos porque ya usa Supabase directamente. Solo hay que modificar la parte de PayPal.

### 2.1 Cambios en index.html

**PayPal (lineas 1498-1573):** Cambiar `createOrder` client-side → server-side:

```js
// ANTES (inseguro, precios visibles en cliente):
createOrder: async function (data, actions) {
  return actions.order.create({
    purchase_units: [{
      amount: { value: '2.50', currency_code: 'EUR' }
    }]
  });
},

// DESPUES (seguro, precios solo en servidor):
createOrder: async function (data, actions) {
  const packId = window.selectedPack || 'pack3';
  const res = await fetch("/api/payments/create-order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      packId: packId,
      userId: currentUser?.id,
    }),
  });
  const { orderId } = await res.json();
  return orderId;
},
```

**Actualizar creditos:** Mover la logica de `onApprove` para no actualizar `games_available` directamente desde el cliente. El webhook se encarga. Solo mostrar confirmacion.

### 2.2 insert_question.html

Cambiar la URL del endpoint de `http://localhost:8000/api/questions` a `/api/questions` (relativa al mismo servidor).

### 2.3 Mover archivos estaticos a `public/`

```bash
move index.html public\index.html
move dashboard.html public\dashboard.html
move insert_question.html public\insert_question.html
move terms.html public\terms.html
move manifest.json public\manifest.json
move favicon.png public\favicon.png
move icon-512.png public\icon-512.png
```

---

## Fase 3 — Configuracion para Hostinger

### 3.1 Variables de entorno (`.env`)

Archivo `.env` en la raiz del proyecto:

```env
SUPABASE_URL=https://zqjvhemwjdqjxecemnwh.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
PORT=3000
NODE_ENV=production
FRONTEND_ORIGIN=https://tudominio.com
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_CLIENT_SECRET=tu_paypal_client_secret
PAYPAL_MODE=sandbox
```

**IMPORTANTE:** En Hostinger, configurar estas variables desde hPanel (no en el codigo).

### 3.2 Requisitos de Hostinger

- Hostinger auto-detecta `package.json` y ejecuta `npm install` + `npm start`
- El servidor debe escuchar en `process.env.PORT` (Hostinger lo asigna automaticamente)
- El archivo `.env` local no se desplegara; las variables se configuran en hPanel
- Puerto por defecto: 3000 (Hostinger lo mapea automaticamente a 80/443)

---

## Fase 4 — Despliegue con MCP de Hostinger

### 4.1 Configurar MCP

```bash
npm install -g hostinger-api-mcp
```

En el cliente MCP (Cursor, Claude, etc.):

```json
{
  "mcpServers": {
    "hostinger-api": {
      "command": "hostinger-api-mcp",
      "env": {
        "HOSTINGER_API_TOKEN": "TU_API_TOKEN"
      }
    }
  }
}
```

### 4.2 Desplegar

Usando los tools del MCP:

1. `hosting_listWebsitesV1` — verificar sitios existentes
2. `hosting_deployJsApplication` — desplegar el proyecto desde ZIP
3. `hosting_listJsDeployments` — monitorear estado del deploy
4. `hosting_showJsDeploymentLogs` — ver logs si hay errores

### 4.3 Configurar dominio

1. `domains_getDomainListV1` — ver dominios
2. `DNS_getDNSRecordsV1` — ver records DNS
3. `DNS_updateDNSRecordsV1` — configurar DNS si es necesario

---

## Fase 5 — Pruebas y Verificacion

### 5.1 Checklist de pruebas

| # | Prueba | Como verificar |
|---|--------|---------------|
| 1 | Servidor responde | `curl https://tudominio.com/health` → `{"status":"ok"}` |
| 2 | Archivos estaticos | Abrir `https://tudominio.com/` → carga index.html |
| 3 | GET /api/questions/:category | `curl https://tudominio.com/api/questions/amigos` → array JSON |
| 4 | POST /api/questions | `curl -X POST .../api/questions -d '[{"text":"test","category":"amigos"}]'` |
| 5 | PayPal create-order | Boton de PayPal en la tienda crea orden sin errores 400/500 |
| 6 | Supabase login | Iniciar sesion con email/password |
| 7 | Supabase OAuth | Login con Google/Facebook (redirige correctamente) |
| 8 | Flujo de juego completo | Crear partida → jugar 20 rondas → ver puntuacion final |
| 9 | Leaderboard | Guardar score en Supabase despues de partida |
| 10 | PWA install | manifest.json accesible, boton de instalacion funciona |
| 11 | dashboard.html | Panel admin con Chart.js carga datos |
| 12 | insert_question.html | Formulario inserta preguntas correctamente |
| 13 | terms.html | Pagina legal accesible |

### 5.2 Pruebas locales antes de desplegar

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Verificar health
curl http://localhost:3000/health

# Probar API
curl http://localhost:3000/api/questions/amigos

# Abrir en navegador
start http://localhost:3000
```

---

## Fase 6 — Limpieza y Documentacion

### 6.1 Archivos que NO se despliegan

- `backend/` (codigo Python, se mantiene como referencia)
- `launch_game.py`, `launch_dashboard.py`, `launch_insert.py`
- `update_git.py`
- `.env` (variables en hPanel)
- `node_modules/` (Hostinger instala automaticamente)

### 6.2 Actualizar .gitignore

Agregar:
```
node_modules/
*.zip
```

### 6.3 Actualizar AGENTS.md

Actualizar con la nueva arquitectura despues de la migracion.

---

## Resumen de Cambios por Archivo

| Archivo | Accion | Cambios |
|---------|--------|---------|
| `backend/` | Conservar (referencia) | No se despliega |
| `public/` | NUEVO | Mover HTML/CSS/JS aqui |
| `server.js` | NUEVO | Express server unificado |
| `routes/questions.js` | NUEVO | Reemplaza FastAPI endpoints |
| `routes/payments.js` | NUEVO | PayPal server-side |
| `routes/webhooks.js` | NUEVO | Webhook PayPal |
| `services/supabase.js` | NUEVO | Cliente Supabase |
| `services/paypal.js` | NUEVO | PayPal SDK |
| `package.json` | NUEVO | Dependencias Node.js |
| `.env.example` | MODIFICAR | Agregar vars de PayPal |
| `index.html` | MODIFICAR | PayPal → server-side, ruta api relativa |
| `insert_question.html` | MODIFICAR | URL endpoint → relativa |
| `launch_game.py` | Conservar | Solo desarrollo local |
| `plan.md` | NUEVO | Este documento |

---

## Backlog Futuro (post-migracion)

1. **Stripe** — Agregar como pasarela alternativa en `routes/payments.js`
2. **Edge Functions en Supabase** — Para logica simple sin pasar por Express
3. **Tests** — Agregar `jest` + `supertest` para la API
4. **CI/CD** — GitHub Actions para deploy automatico a Hostinger
5. **Monitoreo** — Agregar logging estructurado (winston/pino)
6. **Rate limiting** — Proteger endpoints con `express-rate-limit`
7. **Service Worker** — Completar PWA con cache offline
