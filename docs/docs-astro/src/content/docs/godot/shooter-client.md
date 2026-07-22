---
title: 'Shooter: Client'
description: 'Godot client for the arena shooter — player movement, shooting, networking.'
---

# Shooter: Client Setup

The Godot client handles player input, renders the game, and communicates with the EVOID server.

## 1. Godot Project Setup

### Create Project

1. Open Godot 4.4+
2. Create new project: `arena-shooter`
3. Copy the EVOID plugin:

```bash
cp -r /path/to/evoid-godot/evoid_godot addons/
```

4. Enable plugin: Project → Project Settings → Plugins → EVOID → Enable

!!! info "What gets registered"
    The plugin auto-registers 5 autoloads + 1 export plugin:
    - `EvoidBus`, `EvoidClient`, `EvoidUDP`, `EvoidApp`, `EvoidWebLoader`
    - `EvoidExportPlugin` (auto-injects SW on web export)

### Scene Structure

Create these scenes:

```
scenes/
├── main.tscn          # Main game scene
├── player.tscn        # Player prefab
├── bullet.tscn        # Bullet prefab
└── hud.tscn           # Health/score UI
```

## 2. Player Script

Create `scripts/player.gd`:

```gdscript
extends CharacterBody2D
## Player — handles movement, shooting, and network sync.

@export var speed: float = 300.0
@export var player_id: String = ""

var health: int = 100
var is_local: bool = false

@onready var sprite: Sprite2D = $Sprite2D
@onready var muzzle: Marker2D = $Muzzle


func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)
    EvoidBus.subscribe(EvoidTopics.GAME_STATE_SYNC, _on_state_sync)


func _physics_process(delta: float) -> void:
    if not is_local:
        return

    # Movement
    var direction := Vector2.ZERO
    direction.x = Input.get_axis("move_left", "move_right")
    direction.y = Input.get_axis("move_up", "move_down")

    if direction.length() > 0:
        direction = direction.normalized()
        velocity = direction * speed
        move_and_slide()

        # Send position to server
        EvoidApp.send_intent("player_move", {
            "x": global_position.x,
            "y": global_position.y,
        })

    # Shooting
    if Input.is_action_just_pressed("shoot"):
        _shoot()


func _shoot() -> void:
    var direction := (get_global_mouse_position() - global_position).normalized()

    EvoidApp.send_intent("player_shot", {
        "origin": [global_position.x, global_position.y],
        "direction": [direction.x, direction.y],
    })


func _on_game_event(payload: Dictionary) -> void:
    var event_type: String = payload.get("type", "")

    match event_type:
        "shot_fired":
            if payload.get("player_id") != player_id:
                _show_remote_bullet(payload)
        "health_updated":
            if payload.get("player_id") == player_id:
                health = payload.get("health", 100)
                _update_health_ui()
        "player_killed":
            if payload.get("target_id") == player_id:
                _on_killed()


func _on_state_sync(payload: Dictionary) -> void:
    if payload.get("player_id") == player_id:
        # Update remote player position
        var target_pos = Vector2(payload.get("x", 0), payload.get("y", 0))
        global_position = target_pos


func _show_remote_bullet(payload: Dictionary) -> void:
    var bullet_scene = preload("res://scenes/bullet.tscn")
    var bullet = bullet_scene.instantiate()
    bullet.global_position = Vector2(
        payload.get("origin", [0, 0])[0],
        payload.get("origin", [0, 0])[1]
    )
    bullet.direction = Vector2(
        payload.get("direction", [0, 1])[0],
        payload.get("direction", [0, 1])[1]
    )
    get_tree().current_scene.add_child(bullet)


func _update_health_ui() -> void:
    EvoidBus.emit_event("health_changed", {"health": health})


func _on_killed() -> void:
    # Respawn after 2 seconds
    await get_tree().create_timer(2.0).timeout
    global_position = Vector2(960, 540)
    health = 100
```

## 3. Main Game Script

Create `scripts/main.gd`:

```gdscript
extends Node2D
## Main — manages game lifecycle and player spawning.

@export var game_id: String = "arena-shooter"

var players: Dictionary = {}  # player_id → player node
var local_player_id: String = ""


func _ready() -> void:
    # Auto-connect — detects WebGL, resolves same-origin URL
    EvoidApp.auto_connect()

    # Wait for connection
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)
    EvoidBus.subscribe(EvoidTopics.GAME_PLAYER_JOINED, _on_player_joined)
    EvoidBus.subscribe(EvoidTopics.GAME_PLAYER_LEFT, _on_player_left)


func _on_connected(_data: Dictionary) -> void:
    print("Connected to server!")

    # Generate player ID
    local_player_id = "player_%d" % randi() % 10000

    # Join game
    EvoidApp.send_intent("player_join", {
        "player_id": local_player_id,
    })

    # Spawn local player
    _spawn_player(local_player_id, true)


func _on_player_joined(payload: Dictionary) -> void:
    var player_id: String = payload.get("player_id", "")
    if player_id != local_player_id and player_id not in players:
        _spawn_player(player_id, false)


func _on_player_left(payload: Dictionary) -> void:
    var player_id: String = payload.get("player_id", "")
    if player_id in players:
        players[player_id].queue_free()
        players.erase(player_id)


func _spawn_player(player_id: String, is_local: bool) -> void:
    var player_scene = preload("res://scenes/player.tscn")
    var player = player_scene.instantiate()
    player.player_id = player_id
    player.is_local = is_local

    # Set initial position
    if is_local:
        player.global_position = Vector2(960, 540)
    else:
        player.global_position = Vector2(200, 540)

    add_child(player)
    players[player_id] = player
```

## 4. Bullet Script

Create `scripts/bullet.gd`:

```gdscript
extends Area2D
## Bullet — moves in a direction, hits players.

@export var speed: float = 800.0
@export var direction: Vector2 = Vector2.UP
@export var lifetime: float = 2.0

var time_alive: float = 0.0


func _ready() -> void:
    # Rotate to face direction
    rotation = direction.angle()


func _process(delta: float) -> void:
    global_position += direction * speed * delta
    time_alive += delta

    if time_alive >= lifetime:
        queue_free()


func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        body.take_damage(25)
        queue_free()
```

## 5. Input Map

In Godot, set up input mappings:

| Action | Keys |
|--------|------|
| `move_left` | A, Left |
| `move_right` | D, Right |
| `move_up` | W, Up |
| `move_down` | S, Down |
| `shoot` | Left Click |

## 6. Run It

1. Start the EVOID server (from previous tutorial)
2. Open the Godot project
3. Press Play (F5)
4. Two browser windows → two players

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `EvoidApp.auto_connect()` | Auto-detect WebGL, connect to same-origin |
| `EvoidApp.send_intent()` | Send player actions |
| `EvoidBus.subscribe()` | Receive server events |
| `EvoidTopics.*` | Event type constants |
| `EvoidConfig` | Configure server URL, game ID, UDP, export |
| Remote player sync | Server broadcasts positions |
| Local input | Only local player sends movement |

## Next

Now let's connect two players — [Multiplayer](shooter-multiplayer.md).
