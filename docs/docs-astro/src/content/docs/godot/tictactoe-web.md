---
title: 'Tic-Tac-Toe: Web Deploy'
description: 'Deploy as WebGL with instant loading. Embed in any website seamlessly.'
---

# Tic-Tac-Toe: Web Deploy

Export as WebGL and host on EVOID with instant loading. Embed seamlessly in any website.

## 1. Export to HTML5

1. Project → Export → Add → HTML5
2. Set export path: `builds/tic-tac-toe/`
3. Enable Progressive Web App
4. Export

!!! info "Export Plugin"
    `EvoidExportPlugin` automatically injects SW registration and generates `manifest.json`.

## 2. Server: Host the Game

```python
# server/main.py — add hosting

from evoid_godot import GameHost, SplashConfig

# Standalone mode (splash screen)
host = GameHost()
host.register_build(
    "tic-tac-toe",
    "builds/tic-tac-toe/",
    title="Tic-Tac-Toe",
    splash=SplashConfig(
        bg_color="#1a1a2e",
        accent_color="#e94560",
        subtitle="Online Multiplayer",
    ),
)

# OR embed mode (seamless iframe integration)
host_embed = GameHost(embed_mode=True)
host_embed.register_build(
    "tic-tac-toe",
    "builds/tic-tac-toe/",
    title="Tic-Tac-Toe",
)

from starlette.routing import Mount

app = Starlette(
    routes=[
        Mount("/game", app=host.create_router()),
        Mount("/embed", app=host_embed.create_router()),
        WebSocketRoute("/ws", ws_endpoint),
    ],
)
```

!!! tip "Standalone vs Embed"
    - **Standalone** (`embed_mode=False`): Full splash screen, custom colors, works as a standalone game
    - **Embed** (`embed_mode=True`): Minimal loader, transparent background, communicates with parent page via postMessage

## 3. Client: Auto-Connect

Update `scripts/main.gd`:

```gdscript
func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)

    # Auto-connect — works for both desktop and WebGL
    EvoidApp.auto_connect()
```

## 4. Embed in a Website

### Basic Embed (iframe)

The game runs at `/game/tic-tac-toe/`. Embed it in any HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Play Tic-Tac-Toe</title>
    <style>
        .game-container {
            width: 400px;
            height: 600px;
            border: 2px solid #333;
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <h1>Play Tic-Tac-Toe Online</h1>
    <div class="game-container">
        <iframe
            src="/game/tic-tac-toe/"
            width="400"
            height="600"
            frameborder="0"
        ></iframe>
    </div>
    <p>Share this link with a friend to play together!</p>
</body>
</html>
```

### Seamless Embed (with postMessage API)

For deeper integration, use the embed endpoint and postMessage API:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Site — Play Games</title>
    <style>
        #game-frame {
            width: 100%;
            max-width: 600px;
            height: 700px;
            border: none;
            border-radius: 12px;
        }
        #status { margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <h1>My Website</h1>
    <iframe id="game-frame" src="/embed/tic-tac-toe/"></iframe>
    <div id="status">Loading game...</div>

    <script>
    const frame = document.getElementById("game-frame");
    const status = document.getElementById("status");

    // Listen to game events
    frame.addEventListener("message", (e) => {
        if (!e.data || !e.data.type) return;

        switch (e.data.type) {
            case "evoid:ready":
                status.textContent = "Game ready!";
                break;
            case "evoid:loading":
                status.textContent = `Loading... ${e.data.progress}%`;
                break;
            case "evoid:player_joined":
                status.textContent = `Player joined: ${e.data.player_id}`;
                break;
            case "evoid:player_left":
                status.textContent = `Player left: ${e.data.player_id}`;
                break;
            case "evoid:state_sync":
                // Update your UI with game state
                break;
        }
    });

    // Send commands to game
    function pauseGame() {
        frame.contentWindow.postMessage({
            type: "evoid:send_intent",
            name: "pause_game",
            metadata: {}
        }, "*");
    }

    function focusGame() {
        frame.contentWindow.postMessage({
            type: "evoid:focus"
        }, "*");
    }
    </script>
</body>
</html>
```

### Game Side: Receive from Parent

```gdscript
# scripts/main.gd — handle embed messages

func _ready() -> void:
    EvoidWebLoader.embed_message.connect(_on_embed_message)

func _on_embed_message(message: Dictionary):
    match message.get("type"):
        "evoid:send_intent":
            var intent_name = message.get("name", "")
            var metadata = message.get("metadata", {})
            EvoidApp.send_intent(intent_name, metadata)
        "evoid:focus":
            grab_focus()
        "evoid:resize":
            # Handle resize from parent
            pass
```

### Game Side: Send to Parent

```gdscript
# Notify parent when game events happen
func _on_game_event(payload: Dictionary):
    match payload.get("type"):
        "player_joined":
            EvoidWebLoader.post_to_parent("player_joined", {
                "player_id": payload.get("player_id")
            })
        "game_over":
            EvoidWebLoader.post_to_parent("game_over", {
                "winner": payload.get("winner")
            })
```

!!! info "postMessage API"
    **Game → Parent:**
    - `evoid:ready` — game loaded and connected
    - `evoid:loading` — loading progress (phase, progress %)
    - `evoid:player_joined` — player joined the game
    - `evoid:player_left` — player left the game
    - `evoid:state_sync` — game state update

    **Parent → Game:**
    - `evoid:send_intent` — send intent to game (name, metadata)
    - `evoid:focus` — focus the game canvas
    - `evoid:resize` — resize the canvas (width, height)

## 5. Share Link

Share the game URL:
```
https://your-server.com/game/tic-tac-toe/
```

Both players open the link, enter the same room, and play.

## 6. How It Works

The game doesn't download — it **streams** from the server:

```
Player 1 opens link
    ↓
HTML splash loads (<100ms)
    ↓
Service Worker registers + caches game
    ↓
engine.wasm streams in background (~5-10MB)
    ↓
game.pck loads in chunks (256KB each)
    ↓
Game starts — splash fades
    ↓
WebSocket connects to /ws
    ↓
Player joins room
    ↓
Waiting for opponent...
    ↓
Player 2 opens same link
    ↓
(From cache — <1 second)
    ↓
Joins same room → Game starts!
```

### First Visit vs Repeat

| Visit | What Happens | Time |
|-------|-------------|------|
| **First** | HTML → engine.wasm → game.pck chunks → Game | ~8-10s |
| **Repeat** | HTML → cache hit → Game | <1s |

The Service Worker caches engine.wasm and game.pck. Second visit loads from disk.

## 7. Custom Domain

For production, use a custom domain:

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name games.yourdomain.com;

    location /game/ {
        proxy_pass http://localhost:8000/game/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /embed/ {
        proxy_pass http://localhost:8000/embed/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## What You Learned

| Concept | What It It |
|---------|-----------|
| HTML5 export | Build WebGL game |
| `GameHost` | Serve with instant loading |
| `GameHost(embed_mode)` | Seamless iframe embed |
| `postMessage` API | Parent ↔ game communication |
| `auto_connect()` | Auto-detect WebGL |
| Share link | Direct URL to game |
| Custom domain | Production deployment |

## Congratulations

You've built a complete online tic-tac-toe with:
- Turn-based gameplay
- Server-side validation (no cheating)
- Room system
- Win/draw detection
- WebGL deployment
- Instant loading
- Embeddable in any website
- Seamless parent page integration

## Summary: What You Built

| Project | What It Teaches |
|---------|----------------|
| **Arena Shooter** | Real-time sync, movement, shooting, health |
| **Tic-Tac-Toe** | Turn-based, validation, rooms, win detection, embed |

Both use the same EVOID plugins:
- **evoid_godot** (GDScript) — client connection, web loading, embed API
- **evoid-godot** (Python) — server logic + hosting + embed mode

## Next

- Try building your own game with these patterns
- Check the [Plugin Collection](../learn/plugin-collection.md) for more tools
- Read the [Security](../learn/security.md) docs for production deployment
