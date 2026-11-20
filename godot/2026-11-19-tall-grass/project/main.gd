extends Node2D
## Demo root: three meadows side by side (naive / y-sort only / full) plus the HUD.

@onready var meadow_c: Node2D = $MeadowC
@onready var stats: Label = $HUD/Stats
@onready var verify: Label = $HUD/Verify
@onready var overlay_c: Node2D = $MeadowC/Overlay

var t := 0.0


func _process(delta: float) -> void:
	t += delta
	verify.add_theme_color_override("font_color", Color(1, 0.85, 0.45))
	verify.visible = t > 11.0
	var lean: float = meadow_c.get("nearest_lean")
	var press: float = meadow_c.get("nearest_press")
	var rows: int = meadow_c.get("hidden_rows")
	var above: int = meadow_c.get("hide_above")
	var vis: int = meadow_c.get("visible_px")
	var n: int = meadow_c.get("tuft_count")
	stats.text = "panel 3:  %d tufts   nearest tuft lean %5.2f px   press %.2f   hidden rows %2d   hidden above his feet %2d (limit 13)   visible px %4d" % [n, lean, press, rows, above, vis]
