---
title: 'Tic-Tac-Toe: Client'
description: 'Godot client — board rendering, cell clicks, move submission.'
---

# Tic-Tac-Toe: Client Setup

The Godot client renders the board, handles clicks, and communicates with the server.

## 1. Scene Structure

Create these scenes:

```
scenes/
├── main.tscn        # Board + UI
├── cell.tscn        # Single cell (3x3 grid)
└── lobby.tscn       # Room selection
```

## 2. Cell Script

Create `scripts/cell.gd`:

```gdscript
extends Area2D
## Cell — a single tic-tac-toe cell.

signal clicked(position: int)

@export var cell_position: int = 0
@export var mark: String = ""

@onready var x_sprite: Sprite2D = $XSprite
@onready var o_sprite: Sprite2D = $OSprite


func _ready() -> void:
    input_event.connect(_on_input_event)
    _update_visual()


func set_mark(new_mark: String) -> void:
    mark = new_mark
    _update_visual()


func _update_visual() -> void:
    x_sprite.visible = mark == "X"
    o_sprite.visible = mark == "O"


func _on_input_event(_viewport: Node, event: InputEvent, _shape_idx: int) -> void:
    if event is InputEventMouseButton:
        if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
            if mark == "":  # Only click empty cells
                clicked.emit(cell_position)
```

## 3. Board Script

Create `scripts/board.gd`:

```gdscript
extends Node2D
## Board — manages the 3x3 grid.

const CELL_SIZE := 120
const GRID_OFFSET := Vector2(60, 60)

var cells: Array[Area2D] = []
var board_state: Array[String] = [""] * 9


func _ready() -> void:
    _create_grid()
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)


func _create_grid() -> void:
    var cell_scene = preload("res://scenes/cell.tscn")

    for i in range(9):
        var cell = cell_scene.instantiate()
        cell.cell_position = i

        var row = i / 3
        var col = i % 3
        cell.position = Vector2(col * CELL_SIZE, row * CELL_SIZE) + GRID_OFFSET

        cell.clicked.connect(_on_cell_clicked)
        add_child(cell)
        cells.append(cell)


func _on_cell_clicked(position: int) -> void:
    # Send move to server
    EvoidApp.send_intent("make_move", {"position": position})


func _on_game_event(payload: Dictionary) -> void:
    var event_type: String = payload.get("type", "")

    match event_type:
        "move_made":
            _update_cell(payload)
        "game_over":
            _show_result(payload)


func _update_cell(payload: Dictionary) -> void:
    var position: int = payload.get("position", 0)
    var mark: String = payload.get("mark", "")

    if position >= 0 and position < 9:
        board_state[position] = mark
        cells[position].set_mark(mark)


func _show_result(payload: Dictionary) -> void:
    var winner = payload.get("winner")
    var is_draw = payload.get("draw", false)

    var label = $ResultLabel
    if is_draw:
        label.text = "Draw!"
    elif winner:
        label.text = "%s wins!" % winner
    label.visible = true

    # Disable all cells
    for cell in cells:
        cell.set_process(false)
        cell.set_physics_process(false)


func reset() -> void:
    board_state = [""] * 9
    for cell in cells:
        cell.set_mark("")
    $ResultLabel.visible = false
```

## 4. Main Script

Create `scripts/main.gd`:

```gdscript
extends Node2D
## Main — manages game lifecycle.

var player_id: String = ""
var room_id: String = ""
var my_mark: String = ""


func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)

    # Auto-connect — detects WebGL, resolves same-origin URL
    EvoidApp.auto_connect()


func _on_connected(_data: Dictionary) -> void:
    print("Connected to server!")

    # Generate IDs
    player_id = "player_%d" % randi() % 10000
    room_id = "room_%d" % randi() % 1000

    # Join game
    EvoidApp.send_intent("player_join", {
        "player_id": player_id,
        "room_id": room_id,
    })


func _on_game_event(payload: Dictionary) -> void:
    var event_type: String = payload.get("type", "")

    match event_type:
        "player_joined":
            _on_player_joined(payload)
        "player_left":
            _on_player_left(payload)


func _on_player_joined(payload: Dictionary) -> void:
    if payload.get("player_id") == player_id:
        my_mark = payload.get("mark", "")
        $HUD/InfoLabel.text = "You are: %s" % my_mark
        $HUD/RoomLabel.text = "Room: %s" % room_id


func _on_player_left(payload: Dictionary) -> void:
    if payload.get("player_id") != player_id:
        $HUD/InfoLabel.text = "Opponent left!"
```

## 5. HUD Script

Create `scripts/hud.gd`:

```gdscript
extends CanvasLayer
## HUD — room info, player info, controls.

@onready var info_label: Label = $InfoLabel
@onready var room_label: Label = $RoomLabel
@onready var reset_button: Button = $ResetButton


func _ready() -> void:
    reset_button.pressed.connect(_on_reset_pressed)


func _on_reset_pressed() -> void:
    # Leave current game and create new one
    EvoidApp.send_intent("leave_game", {})
    get_tree().reload_current_scene()
```

## 6. Lobby Script

Create `scripts/lobby.gd`:

```gdscript
extends Control
## Lobby — room selection.

@onready var room_input: LineEdit = $RoomInput
@onready var join_button: Button = $JoinButton
@onready var status_label: Label = $StatusLabel


func _ready() -> void:
    join_button.pressed.connect(_on_join_pressed)
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)


func _on_join_pressed() -> void:
    var room = room_input.text.strip_edges()
    if room.is_empty():
        status_label.text = "Enter a room name"
        return

    status_label.text = "Connecting..."
    # Configure and auto-connect
    var config = EvoidConfig.new()
    config.game_id = room
    EvoidApp.config = config
    EvoidApp.auto_connect()


func _on_connected(_data: Dictionary) -> void:
    status_label.text = "Connected!"
    await get_tree().create_timer(0.5).timeout
    get_tree().change_scene_to_file("res://scenes/main.tscn")
```

## 7. Run

1. Start server: `python server/main.py`
2. Open Godot project
3. Press Play (F5)
4. Enter a room name, click Join
5. Open second instance, join same room
6. Play!

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `EvoidApp.auto_connect()` | Auto-detect WebGL, connect to same-origin |
| `EvoidConfig` | Configure game ID, server URL |
| Cell clicks | Detect player input |
| Board rendering | 3x3 grid of cells |
| Move submission | Send to server via Intent |
| Game events | Receive updates from server |
| Turn display | Show whose turn it is |
| Win/draw display | Show game result |

## Next

Now let's add room system — [Multiplayer](tictactoe-multiplayer.md).
