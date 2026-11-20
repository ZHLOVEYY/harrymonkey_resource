extends Node2D
## Draws the wading cut line (LOCAL to this demo, not in the article):
## the per-column row where the player stops being drawn, so you can see that the
## cut follows the grass that is actually drawn.

var meadow: Node = null
var show_line := true


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	if meadow == null or not show_line:
		return
	var cuts: Array = meadow.get("cuts")
	if cuts.is_empty():
		return
	var origin: Vector2 = meadow.get("frame_origin")
	var col := Color(1.0, 0.28, 0.28, 0.95)
	for c in cuts.size():
		var cut: int = cuts[c]
		if cut >= 32:
			continue
		draw_rect(Rect2(origin + Vector2(c, cut), Vector2(1, 1)), col)
		if c + 1 < cuts.size():
			var cut2: int = cuts[c + 1]
			if cut2 >= 32:
				continue
			var lo := mini(cut, cut2)
			var hi := maxi(cut, cut2)
			draw_rect(Rect2(Vector2(origin.x + c + 1, origin.y + lo), Vector2(1, hi - lo + 1)), col)
