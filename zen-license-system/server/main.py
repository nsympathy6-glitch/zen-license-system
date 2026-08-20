from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid, hashlib, os, httpx
from dotenv import load_dotenv
from database import init_db, get_db, get_order_by_serial_and_discord, create_order, Order, get_user_by_discord, create_or_update_user, bind_zen_serial

load_dotenv()
app = FastAPI(title="Shoot 3P License Server")

SECRET = os.getenv("LICENSE_SECRET", "shoot3p-secret-2024")
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "1520636366331973803")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/api/auth/callback")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "1415672033559183462")
APP_USER_ROLE = os.getenv("APP_USER_ROLE_ID", "")
PORT = int(os.getenv("PORT", "8000"))

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

connected_users = {}

class OrderReq(BaseModel):
    discord_id: str
    zen_serial: str
    product: str
    tier: str = "standard"

@app.on_event("startup")
async def startup():
    init_db()

# ── Discord OAuth ──

@app.get("/api/auth/discord")
async def discord_auth():
    url = (f"https://discord.com/api/oauth2/authorize"
           f"?client_id={CLIENT_ID}"
           f"&redirect_uri={REDIRECT_URI}"
           f"&response_type=code"
           f"&scope=identify%20guilds.members.read"
           f"&prompt=consent")
    return RedirectResponse(url)

@app.get("/api/auth/callback")
async def discord_callback(code: str = ""):
    if not code:
        return HTMLResponse("<h1 style='color:white;background:#0d0d1a;font-family:sans-serif;text-align:center;padding:60px;'>No code provided. You can close this window.</h1>")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://discord.com/api/oauth2/token", data={
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI
        })
        if token_resp.status_code != 200:
            return HTMLResponse("<h1 style='color:white;background:#0d0d1a;font-family:sans-serif;text-align:center;padding:60px;'>Token exchange failed. Close this and try again.</h1>")

        access_token = token_resp.json()["access_token"]

        user_resp = await client.get("https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"})
        if user_resp.status_code != 200:
            return HTMLResponse("<h1 style='color:white;background:#0d0d1a;font-family:sans-serif;text-align:center;padding:60px;'>Failed to get user info.</h1>")

        user = user_resp.json()
        discord_id = user["id"]
        username = user.get("username", "Unknown")
        avatar = user.get("avatar", "")

        connected_users[discord_id] = {
            "username": username, "avatar": avatar, "discriminator": user.get("discriminator", "0")
        }

        create_or_update_user(discord_id, username)
        await assign_app_user_role(discord_id)

    return HTMLResponse(f"""
    <html><head><title>Login Successful</title></head>
    <body style="margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;
    background:linear-gradient(135deg,#0d0d1a,#1a1a3e);font-family:'Segoe UI',sans-serif;">
    <div style="text-align:center;color:white;padding:40px;">
        <div style="font-size:48px;margin-bottom:16px;">&#10004;</div>
        <h1 style="margin:0 0 8px;font-size:24px;">Connected!</h1>
        <p style="color:#888;margin:0 0 24px;">Logged in as <strong style="color:#6C63FF;">{username}</strong></p>
        <p style="color:#555;font-size:14px;">You can close this window and return to the app.</p>
    </div></body></html>
    """)

async def assign_app_user_role(discord_id: str):
    if not BOT_TOKEN or not APP_USER_ROLE or not GUILD_ID:
        return
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"https://discord.com/api/guilds/{GUILD_ID}/members/{discord_id}/roles/{APP_USER_ROLE}",
                headers={"Authorization": f"Bot {BOT_TOKEN}"})
    except:
        pass

@app.get("/api/auth/user/{discord_id}")
async def get_user(discord_id: str):
    if discord_id in connected_users:
        return {"connected": True, **connected_users[discord_id]}
    return {"connected": False}

@app.get("/api/auth/status")
async def get_latest_connection():
    if connected_users:
        latest_id = list(connected_users.keys())[-1]
        return {"connected": True, "discord_id": latest_id, **connected_users[latest_id]}
    return {"connected": False}

# ── License endpoints ──

@app.post("/api/login")
async def login(req: dict):
    d = req.get("discord_id", "")
    s = req.get("zen_serial", "")
    user = get_user_by_discord(d)
    if user and user.get("zen_serial") and user["zen_serial"] != s:
        raise HTTPException(403, "This Discord account is already locked to a different Zen serial")
    if user and not user.get("zen_serial"):
        bind_zen_serial(d, s)
    elif not user:
        create_or_update_user(d, "", s)
    return {"ok": True, "has_scripts": True}

@app.get("/api/scripts/{discord_id}/{zen_serial}")
async def get_user_scripts(discord_id: str, zen_serial: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE discord_id=? AND zen_serial=? ORDER BY purchased_at DESC",
                (discord_id, zen_serial))
    orders = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"orders": orders}

@app.post("/api/export")
async def export_script(req: dict):
    order_id = req.get("order_id")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
    order = cur.fetchone()
    conn.close()
    if not order:
        raise HTTPException(404, "Order not found")
    order = dict(order)
    seed = hashlib.sha256(f"{order['order_id']}:{SECRET}".encode()).hexdigest()[:8]
    return {"order_id": order['order_id'], "seed": seed, "zen_serial": order['zen_serial'],
            "product": order['product'], "tier": order['tier'], "expires_at": order['expires_at']}

@app.post("/api/orders")
async def new_order(req: OrderReq):
    order_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow()
    delta = {"trial": __import__('datetime').timedelta(hours=24),
             "plus": __import__('datetime').timedelta(days=365),
             "standard": __import__('datetime').timedelta(days=30)}.get(req.tier, __import__('datetime').timedelta(days=30))
    order = Order(order_id=order_id, discord_id=req.discord_id, zen_serial=req.zen_serial,
                  product=req.product, tier=req.tier, purchased_at=now, expires_at=now+delta, status="active")
    create_order(order)
    seed = hashlib.sha256(f"{order_id}:{SECRET}".encode()).hexdigest()[:8]
    return {"order_id": order_id, "seed": seed, "expires_at": (now+delta).isoformat()}

@app.post("/api/challenge")
async def get_challenge(req: dict):
    discord_id = req.get("discord_id")
    zen_serial = req.get("zen_serial")
    if not discord_id or not zen_serial:
        raise HTTPException(400, "discord_id and zen_serial required")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE discord_id=? AND zen_serial=? ORDER BY purchased_at DESC",
                (discord_id, zen_serial))
    order = cur.fetchone()
    conn.close()
    if not order:
        raise HTTPException(404, "No order found for this Discord/Serial combination")
    order = dict(order)
    if order["status"] == "banned":
        raise HTTPException(403, "This device is banned")
    if order["expires_at"] and datetime.fromisoformat(order["expires_at"]) < datetime.utcnow():
        raise HTTPException(403, "License expired")
    seed = hashlib.sha256(f"{order['order_id']}:{SECRET}".encode()).hexdigest()[:8]
    combined = seed + zen_serial + order["order_id"]
    challenge = 5381
    for ch in combined:
        challenge = ((challenge << 5) + challenge + ord(ch)) & 0x7FFFFFFF
    challenge = challenge % 1000000
    return {"challenge": challenge, "order_id": order["order_id"]}

@app.post("/api/generate_key")
async def generate_key(req: dict):
    order_id = req.get("order_id")
    zen_serial = req.get("zen_serial")
    challenge = req.get("challenge")
    if not all([order_id, zen_serial, challenge]):
        raise HTTPException(400, "order_id, zen_serial, and challenge required")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id=? AND zen_serial=?", (order_id, zen_serial))
    order = cur.fetchone()
    conn.close()
    if not order:
        raise HTTPException(404, "Order not found or serial mismatch")
    order = dict(order)
    if order["status"] == "banned":
        raise HTTPException(403, "This device is banned")
    if order["expires_at"] and datetime.fromisoformat(order["expires_at"]) < datetime.utcnow():
        raise HTTPException(403, "License expired")
    seed = hashlib.sha256(f"{order['order_id']}:{SECRET}".encode()).hexdigest()[:8]
    expected = seed + zen_serial + order_id + str(challenge)
    key_hash = 5381
    for ch in expected:
        key_hash = ((key_hash << 5) + key_hash + ord(ch)) & 0x7FFFFFFF
    return {"key": str(key_hash), "order_id": order_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
