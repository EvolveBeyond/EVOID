---
title: 'Shooter: Web Export'
description: 'Export the shooter as WebGL and host it on EVOID.'
---

# Shooter: Web Export

Export the shooter as a WebGL game and host it on the EVOID server.

## 1. Export Godot to HTML5

### Install Export Template

1. Godot → Editor → Manage Export Templates
2. Download "HTML5" template
3. Install

### Create Export Preset

1. Project → Export → Add → HTML5
2. Set:
   - **Export Path**: `builds/arena-shooter/`
   - **Variant**: Release
   - **Progressive Web App**: Enabled

### Export

1. Click "Export Project"
2. Check "Export Debug" for testing
3. Click "Export"

Output:
```
builds/arena-shooter/
├── index.html
├── index.js
├── index.wasm
├── game.pck
└── icon.png
```

!!! info "Export Plugin"
    The `EvoidExportPlugin` automatically:
    - Injects Service Worker registration into `index.html`
    - Generates `manifest.json` for chunk-aware loading
    - No manual setup needed

## 2. Server: Host the Game

Update `server/main.py` to serve the game:

```python
from evoid_godot import GameHost, SplashConfig

# Create game host
host = GameHost()
host.register_build(
    "arena-shooter",
    "builds/arena-shooter/",
    title="Arena Shooter",
    splash=SplashConfig(
        bg_color="#0d1117",
        accent_color="#e94560",
        subtitle="Multiplayer Arena Shooter",
    ),
)

# Add to routes
from starlette.routing import Route, Mount

app = Starlette(
    routes=[
        # Game hosting
        Mount("/game", app=host.create_router()),

        # Game API
        Route("/health", health),
        Route("/state", game_state),
        WebSocketRoute("/ws", ws_endpoint),
    ],
)
```

## 3. Client: Auto-Connect in WebGL

Update the player script to auto-detect WebGL:

```gdscript
# scripts/player.gd — update _ready

func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)
    EvoidBus.subscribe(EvoidTopics.GAME_STATE_SYNC, _on_state_sync)

    # Auto-connect — detects WebGL, resolves same-origin URL
    EvoidApp.auto_connect()
```

!!! tip "Why auto_connect?"
    `auto_connect()` does three things:
    1. Checks `OS.has_feature("web")` — if desktop, falls back to `connect_to_server()`
    2. Resolves WebSocket URL from `window.location` (same-origin)
    3. Connects with configured `game_id`

## 4. Run

```bash
cd server
python main.py
```

Open `http://localhost:8000/game/arena-shooter/`

## 5. How It Works

The game doesn't download — it **streams** from the server:

```
User visits /game/arena-shooter/
    ↓
1. HTML splash loads instantly (<100ms)
   └─ Just a div with progress bar
    ↓
2. Service Worker registers (auto-injected by ExportPlugin)
   └─ Caches engine.wasm + game.pck for instant repeat visits
    ↓
3. engine.wasm streams in background (~5-10MB)
   └─ Godot engine as WebAssembly
    ↓
4. game.pck loads in chunks (256KB each)
   └─ Server splits game data, client loads with progress bar
    ↓
5. Game starts — splash fades
    ↓
6. WebSocket connects to /ws
   └─ Player joins game
```

### First Visit vs Repeat

| Visit | What Happens | Time |
|-------|-------------|------|
| **First** | HTML → engine.wasm → game.pck chunks → Game | ~8-10s |
| **Repeat** | HTML → cache hit → Game | <1s |

The Service Worker caches everything. Second visit loads from disk, not network.

## 6. Binary Intents (Optional)

For bandwidth optimization, use binary WebSocket frames (~60% smaller than JSON):

```gdscript
# Instead of:
EvoidApp.send_intent("player_shot", {"origin": pos, "direction": dir})

# Use binary:
EvoidClient.send_intent_binary("player_shot", {"origin": pos, "direction": dir})
```

!!! info "Binary format"
    - 4 bytes: intent name length
    - N bytes: intent name (UTF-8)
    - 4 bytes: metadata length
    - N bytes: JSON-encoded metadata

    Server must handle both formats. Binary is optional — JSON always works.

## 7. Multi-Player in Browser

Open two browser tabs:
- Tab 1: `http://localhost:8000/game/arena-shooter/`
- Tab 2: `http://localhost:8000/game/arena-shooter/`

Both connect to the same server. See each other's movements and shots.

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Godot HTML5 export | Build WebGL game |
| `EvoidExportPlugin` | Auto SW injection + manifest generation |
| `GameHost` | Serve game with instant loading |
| `SplashConfig` | Custom splash screen |
| `auto_connect()` | Detect WebGL, connect to same-origin |
| `send_intent_binary()` | Binary WebSocket frames (optional) |
| Service Worker | Cache game for instant repeat visits |

## Congratulations

You've built a complete multiplayer shooter with:
- Real-time movement sync
- Shot detection
- Health system
- Score tracking
- WebGL deployment
- Instant loading
- Binary intent support

## Next

Try the [Tic-Tac-Toe](tictactoe-overview.md) tutorial for a turn-based game with embed support.
