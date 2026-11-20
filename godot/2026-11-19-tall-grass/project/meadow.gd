extends Node2D
## One meadow panel of the demo.
##
## mode 0  grass painted on the floor (the naive way, nothing reacts)
## mode 1  grass as separate sprites, y-sorted, but no wading cut and no interaction
## mode 2  the full technique: wading cut, spring lean, trample + regrow, leaf specks

const TallGrass := preload("res://tall_grass.gd")
const Wading := preload("res://wading.gd")
const TUFT_SCENE := preload("res://tuft.tscn")
const CREATURE_SHEET := preload("res://assets/creature.png")
const FLOOR_TEX := preload("res://assets/grass_floor.png")

const GROUND_COLOR := Color(0.1176, 0.2275, 0.1490)
const FRAME := 32

@export var mode := 2
@export var panel_width := 144.0
@export var ground_top := 36.0
@export var ground_bottom := 250.0
@export var patch_left := 34.0
@export var patch_right := 118.0
@export var patch_top := 76.0
@export var patch_bottom := 188.0
@export var spacing_x := 13.0
@export var spacing_y := 8.0
@export var walk_top := 48.0
@export var walk_bottom := 214.0
@export var walk_speed := 42.0

var grass: Node2D = null
var player: Sprite2D = null
var sheet: Image = null
var cuts: Array = []
var frame_origin := Vector2.ZERO
var nearest_lean := 0.0
var nearest_press := 0.0
var hidden_rows := 0
var hide_above := 0
var visible_px := FRAME * FRAME
var tuft_count := 0
var t := 0.0
var going_up := false


func _ready() -> void:
	sheet = CREATURE_SHEET.get_image()
	if mode > 0:
		_build_grass()
	_build_player()
	$Overlay.meadow = self
	queue_redraw()


func _load_image(path: String) -> Image:
	var tex: Texture2D = load(path)
	var img: Image = tex.get_image()
	if img.is_compressed():
		img.decompress()
	return img


func _build_grass() -> void:
	grass = TallGrass.new()
	grass.name = "Grass"
	add_child(grass)
	grass.enabled = (mode == 2)
	var art := []
	for k in 4:
		art.append([
			_load_image("res://assets/tuft_%d.png" % k),
			_load_image("res://assets/tuft_%d_dark1.png" % k),
			_load_image("res://assets/tuft_%d_dark2.png" % k),
		])
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261119
	var sorted := $Sorted
	var x := patch_left
	while x <= patch_right:
		# LOCAL: the patch is jittered so it does not read as a brick wall and its top edge
		# is ragged. The article lays its patch out in a strict grid.
		var col_top := patch_top + rng.randf_range(-5.0, 5.0)
		var y := col_top
		while y <= patch_bottom:
			var variant := rng.randi_range(0, 3)
			var flip := rng.randf() < 0.5
			var phase := rng.randf()
			var edge := y <= col_top + 0.1 or y >= patch_bottom - 0.1
			var px := int(x + rng.randf_range(-2.0, 2.0))
			var py := int(y + rng.randf_range(-1.5, 1.5))
			var s := TUFT_SCENE.instantiate()
			sorted.add_child(s)
			grass.add_tuft(Vector2i(px, py), art[variant], edge, phase, flip, s)
			tuft_count += 1
			y += spacing_y + rng.randf_range(-1.6, 1.6)
		x += spacing_x + rng.randf_range(-2.0, 2.0)
	grass.touched.connect(_on_touched)


func _build_player() -> void:
	player = Sprite2D.new()
	player.name = "Player"
	player.centered = false
	$Sorted.add_child(player)   # added after the tufts: on a tie in y he draws in front


func _draw() -> void:
	var rect := Rect2(0, ground_top, panel_width, ground_bottom - ground_top)
	if mode == 0:
		draw_texture_rect(FLOOR_TEX, rect, true)
	else:
		draw_rect(rect, GROUND_COLOR)
	draw_rect(rect, Color(0.06, 0.12, 0.07), false, 1.0)


func _physics_process(delta: float) -> void:
	t += delta
	var feet := _walk(t)
	if grass != null:
		grass.step(t, feet)
		grass.update_sprites(t)
	var fx := int(floor(feet.x + 0.5))
	var fy := int(floor(feet.y + 0.5))
	var frame := _frame_image()
	var out := frame
	if mode > 0:
		var w: Dictionary = Wading.wade(frame, fx, fy, grass, t)
		out = w["image"]
		cuts = w["cuts"]
		hidden_rows = 0
		hide_above = 0
		var lowest := FRAME - 1
		for y in range(FRAME - 1, -1, -1):
			var found := false
			for x in FRAME:
				if frame.get_pixel(x, y).a > 0:
					found = true
					break
			if found:
				lowest = y
				break
		for c in cuts:
			hidden_rows = maxi(hidden_rows, FRAME - c)
			hide_above = maxi(hide_above, lowest + 1 - c)
	else:
		cuts = []
		hidden_rows = 0
		hide_above = 0
	visible_px = _count_opaque(out)
	player.texture = ImageTexture.create_from_image(out)
	# the player's node sits on the sort line (fy - sort_offset): a tuft whose base is on that line
	# ties with him and draws behind (he is the later child); a tuft a pixel lower draws in front.
	var sort_offset := 1
	if grass != null:
		sort_offset = grass.sort_offset
	player.position = Vector2(fx, fy - sort_offset)
	player.offset = Vector2(-FRAME / 2, -FRAME + sort_offset)
	frame_origin = Vector2(fx - FRAME / 2, fy - FRAME)
	_track_nearest(feet)


func _count_opaque(img: Image) -> int:
	var n := 0
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0:
				n += 1
	return n


func _track_nearest(feet: Vector2) -> void:
	if grass == null:
		return
	var best := 100000.0
	nearest_lean = 0.0
	nearest_press = 0.0
	for f in grass.tufts:
		var dx := float(f.x) - feet.x
		var dy := float(f.y) - feet.y
		var d := sqrt(dx * dx + dy * dy)
		if d < best:
			best = d
			nearest_lean = f.lean
			nearest_press = f.press


func _walk(time: float) -> Vector2:
	var length := walk_bottom - walk_top
	var hold := 14.0
	var u := fmod(time * walk_speed, 2.0 * length + 2.0 * hold)
	var y := walk_top
	going_up = false
	if u < length:
		y = walk_top + u
	elif u < length + hold:
		y = walk_bottom
	elif u < 2.0 * length + hold:
		y = walk_bottom - (u - length - hold)
		going_up = true
	else:
		y = walk_top
		going_up = true
	return Vector2(panel_width * 0.5, y)


func _frame_image() -> Image:
	var idx := int(fmod(t * 6.0, 4.0))
	var img := sheet.get_region(Rect2i(idx * FRAME, 0, FRAME, FRAME))
	if going_up:
		img.flip_y()
	return img


func _on_touched(f: Dictionary) -> void:
	$Specks.spawn(Vector2(f.x, f.y - 9.0))
