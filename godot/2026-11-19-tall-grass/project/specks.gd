extends Node2D
## A tiny burst of pale leaf specks when a tuft is first pushed.

var parts: Array = []


func spawn(pos: Vector2) -> void:
	for i in 8:
		parts.append({
			"p": pos + Vector2(randf_range(-3.0, 3.0), randf_range(-4.0, 0.0)),
			"v": Vector2(randf_range(-16.0, 16.0), randf_range(-28.0, -10.0)),
			"life": randf_range(0.35, 0.6),
		})


func _process(delta: float) -> void:
	var alive := []
	for s in parts:
		s.life -= delta
		s.v.y += 70.0 * delta
		s.p += s.v * delta
		if s.life > 0.0:
			alive.append(s)
	parts = alive
	queue_redraw()


func _draw() -> void:
	for s in parts:
		draw_rect(Rect2(s.p, Vector2(2, 2)), Color(0.86, 0.97, 0.55, clampf(s.life * 2.2, 0.0, 1.0)))
