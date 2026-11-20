extends Node2D
## Tall grass that reacts to the player. Each tuft is a Sprite2D in the same y-sorted parent as the player,
## with its origin at its base. Call step() once per physics tick, then update_sprites().
##
## Source: SpriteCook, "How to make interactive tall grass for a top-down pixel art game"
## https://spritecook.ai/blog/interactive-tall-grass-top-down-pixel-art (2026-11-19, tested Godot 4.6).
## The code below is the author's, as published for agents to copy into their own project.
## LOCAL CHANGES are marked LOCAL: a per-tick image cache and an idle fast path, so a patch of
## hundreds of tufts does not rebuild every tuft's image twice per frame.

@export var feel_x := 12.0          ## a tuft feels the player when it is less than this far to his side ...
@export var feel_back := 4.0        ## ... and its base is less than this far above his feet ...
@export var feel_front := 10.0      ## ... or less than this far below them
@export var lean_px := 7.0          ## how far the tip leans away at the closest point
@export var front_x := 9.0          ## tufts in front of his legs (closer than this to the side) ...
@export var front_lean_px := 2.0    ## ... lean at most this much, so they keep covering him
@export var max_lean_px := 8.0
@export var spring_hz := 2.6
@export var damping := 0.22
@export var press_x := 7.0          ## tufts he steps on: closer than this to the side ...
@export var press_back := 10.0      ## ... with a base up to this far above his feet
@export var press_time := 0.12      ## seconds to press flat
@export var recover_time := 0.7     ## seconds to grow back
@export var press_squash := 0.67    ## a pressed tuft loses this share of its height
@export var cover_time := 0.35
@export var cover_squash := 0.1     ## a tuft covering him eases down this much, so it stays below his face
@export var shake_px := 1.3
@export var shake_speed := 55.0
@export var shake_time := 0.35
@export var touch_lean := 1.5       ## a lean target above this counts as a touch (shake, leaf specks)
@export var touch_cooldown := 0.7
@export var sort_offset := 1        ## the player sorts as if this many px above his feet
@export var enabled := true

signal touched(tuft: Dictionary)    ## connect a CPUParticles2D burst of leaf specks here

var tufts: Array[Dictionary] = []

## art: [normal, one shade darker, two shades darker], each an Image with the tuft's base on its bottom row.
func add_tuft(base: Vector2i, art: Array, edge: bool, phase: float, flip := false, sprite: Sprite2D = null) -> Dictionary:
	var images: Array[Image] = []
	for a in art:
		var img: Image = a.duplicate()
		if flip:
			img.flip_x()
		images.append(img)
	var f := {"x": base.x, "y": base.y, "art": images, "edge": edge, "phase": phase,
		"lean": 0.0, "vel": 0.0, "press": 0.0, "cover": 0.0, "touch": -9.0, "side": 0,
		"sprite": sprite, "look": ""}
	if sprite:
		sprite.centered = false
		sprite.position = Vector2(base)
	tufts.append(f)
	return f

func step(t: float, feet: Vector2) -> void:
	if not enabled:
		return
	var dt := 1.0 / Engine.physics_ticks_per_second
	var w := TAU * spring_hz
	for f in tufts:
		var dx: float = f.x - feet.x
		var dy: float = f.y - feet.y
		var target := 0.0
		if absf(dx) < feel_x and dy > -feel_back and dy < feel_front:
			if f.side == 0:
				f.side = 1 if dx > 0 or (dx == 0 and f.phase > 0.5) else -1
			target = f.side * lean_px * minf(1.0, (feel_x - absf(dx)) / 6.0) * minf(1.0, (feel_front - absf(dy - 3)) / 5.0)
			if dy > -sort_offset and absf(dx) < front_x:
				target = clampf(target, -front_lean_px, front_lean_px)
			if absf(target) > touch_lean and t - f.touch > touch_cooldown:
				f.touch = t
				touched.emit(f)
			elif absf(target) > touch_lean:
				f.touch = maxf(f.touch, t - 0.5)  # he is still pushing it: no new rustle until he lets go
		else:
			f.side = 0
		if absf(dx) < press_x and dy > -press_back and dy <= -sort_offset and not f.edge:
			f.press = minf(1.0, f.press + dt / press_time)
		else:
			f.press = maxf(0.0, f.press - dt / recover_time)
		var ddy := dy + sort_offset
		var near := 0.0
		if ddy > 0:
			near = clampf((11 - absf(dx)) / 3.0, 0.0, 1.0) * clampf((10 - ddy) / 3.0, 0.0, 1.0) * minf(1.0, ddy / 3.0)
		f.cover += clampf(near - f.cover, -dt / cover_time, dt / cover_time)
		var acc: float = w * w * (target - f.lean) - 2.0 * damping * w * f.vel
		f.vel += acc * dt
		f.lean = clampf(f.lean + f.vel * dt, -max_lean_px, max_lean_px)

## The tuft as drawn at time t: {"image": Image, "offset": x of its left edge relative to the base}.
func tuft_image(f: Dictionary, t: float) -> Dictionary:
	# LOCAL: one image per tuft per tick. The wading pass asks for the same tufts again in the
	# same tick, and the reference implementation rebuilt every image from scratch there.
	if f.get("_cache_tick", -1.0) == t:
		return f["_cache"]
	var res := _build_tuft_image(f, t)
	f["_cache_tick"] = t
	f["_cache"] = res
	return res

func _build_tuft_image(f: Dictionary, t: float) -> Dictionary:
	var img: Image = f.art[0]
	var h := img.get_height()
	var w := img.get_width()
	if not enabled:
		return {"image": img, "offset": -(w / 2), "idle": true}
	var age: float = t - f.touch
	# LOCAL fast path: a tuft that is not leaning, not pressed and not covering him is plain art.
	if absf(f.lean) < 0.001 and f.press < 0.001 and f.cover < 0.001 and age >= shake_time:
		return {"image": img, "offset": -(w / 2), "idle": true}
	var shake := 0.0
	if age >= 0:
		shake = shake_px * sin(age * shake_speed + f.phase * 6.0) * maxf(0.0, 1.0 - age / shake_time)
	var p: float = f.press
	var src: Image = f.art[2] if p > 0.6 else (f.art[1] if p > 0.3 else img)
	var ease_p := p * p * (3.0 - 2.0 * p)
	var nh := maxi(1, int(floor(h * (1.0 - press_squash * ease_p) * (1.0 - cover_squash * f.cover) + 0.5)))
	if nh < h:
		var squashed := Image.create_empty(w, nh, false, Image.FORMAT_RGBA8)
		for i in nh:
			var row := 0 if nh == 1 else int(floor(i * (h - 1) / float(nh - 1) + 0.5))
			squashed.blit_rect(src, Rect2i(0, row, w, 1), Vector2i(0, i))
		src = squashed
	var lean: float = f.lean + shake
	var sh := src.get_height()
	if absf(lean) < 0.5:
		return {"image": src, "offset": -(w / 2), "idle": false}
	var pad := int(ceil(absf(lean))) + 1
	var out := Image.create_empty(w + 2 * pad, sh, false, Image.FORMAT_RGBA8)
	for r in sh:
		var k := pow(float(sh - 1 - r) / (sh - 1), 1.6) if sh > 1 else 0.0
		var s := int(floor(lean * k + 0.5))
		out.blit_rect(src, Rect2i(0, r, w, 1), Vector2i(pad + s, r))
	return {"image": out, "offset": -(w / 2) - pad, "idle": false}

## Give each tuft's Sprite2D its current look. Only tufts whose look changed get a new texture.
func update_sprites(t: float) -> void:
	for f in tufts:
		var sprite: Sprite2D = f.sprite
		if sprite == null:
			continue
		var d := tuft_image(f, t)
		var img: Image = d.image
		var look := ""
		if d.get("idle", false):
			look = "idle"  # LOCAL: the plain art never changes, so skip hashing it every frame
		else:
			look = "%d,%d,%d" % [img.get_width(), img.get_height(), hash(img.get_data())]
		if look != f.look:
			f.look = look
			sprite.texture = ImageTexture.create_from_image(img)
		sprite.offset = Vector2(d.offset, -img.get_height())
