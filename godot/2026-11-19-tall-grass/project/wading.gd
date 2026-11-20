extends RefCounted
## Hides the parts of the player that the tall grass in front of him should hide.
##
## Source: SpriteCook, "How to make interactive tall grass for a top-down pixel art game"
## https://spritecook.ai/blog/interactive-tall-grass-top-down-pixel-art (2026-11-19, tested Godot 4.6).
## The author's code, as published.

const TIP_SHOW := 2        ## he shows through the top 2 rows of the grass in front of him
const MAX_HIDE := 13       ## never hide more than 13 rows of him
const SMOOTH_COLUMNS := 5
const MIN_PIECE := 12      ## pieces of him smaller than this, cut off by the grass, are hidden too

## frame: his current animation frame (square, feet on the bottom row of the art), drawn with its
## bottom-center at the feet (fx, fy). grass: the TallGrass node. Returns {"image": Image, "cuts": Array}.
static func wade(frame: Image, fx: int, fy: int, grass, t: float) -> Dictionary:
	var n := frame.get_width()
	var cuts := []
	if not grass.enabled:
		cuts.resize(n)
		cuts.fill(n)
		return {"image": frame, "cuts": cuts}
	var ox := fx - n / 2
	var oy := fy - n
	# 1. Which of his pixels sit under grass that is drawn in front of him
	var cover := []
	cover.resize(n * n)
	cover.fill(false)
	for f in grass.tufts:
		if f.y <= fy - grass.sort_offset:
			continue  # behind him
		var d: Dictionary = grass.tuft_image(f, t)
		var img: Image = d.image
		var x0: int = f.x + d.offset - ox
		var y0: int = f.y - img.get_height() - oy
		for r in img.get_height():
			var yy := y0 + r
			if yy < 0 or yy >= n:
				continue
			for c in img.get_width():
				var xx := x0 + c
				if xx >= 0 and xx < n and img.get_pixel(c, r).a > 0:
					cover[yy * n + xx] = true
	# 2. Per column, cut him off just below the top of that grass
	for c in n:
		var cut := n
		for y in n:
			if cover[y * n + c]:
				cut = y + TIP_SHOW
				break
		cuts.append(cut)
	# 3. Smooth: each column takes the highest cut within 2 columns either side (mirrored at the edges)
	var half := SMOOTH_COLUMNS / 2
	var smooth := []
	for c in n:
		var best := n
		for k in range(-half, half + 1):
			var j := c + k
			if j < 0:
				j = -j - 1
			elif j >= n:
				j = 2 * n - j - 1
			best = mini(best, cuts[j])
		smooth.append(best)
	# 4. Never deeper than MAX_HIDE rows above his lowest pixel
	var bottom := n - 1
	for y in range(n - 1, -1, -1):
		var any := false
		for x in n:
			if frame.get_pixel(x, y).a > 0:
				any = true
				break
		if any:
			bottom = y
			break
	for c in n:
		smooth[c] = maxi(smooth[c], bottom + 1 - MAX_HIDE)
	var out := frame.duplicate()
	for c in n:
		for y in range(smooth[c], n):
			out.set_pixel(c, y, Color(0, 0, 0, 0))
	# 5. Hide small pieces of him that the cut separated from the rest
	var seen := []
	seen.resize(n * n)
	seen.fill(false)
	for y in n:
		for x in n:
			if seen[y * n + x] or out.get_pixel(x, y).a == 0:
				continue
			var stack := [Vector2i(x, y)]
			var piece := []
			seen[y * n + x] = true
			while not stack.is_empty():
				var p: Vector2i = stack.pop_back()
				piece.append(p)
				for yy in range(p.y - 1, p.y + 2):
					for xx in range(p.x - 1, p.x + 2):
						if yy >= 0 and yy < n and xx >= 0 and xx < n and not seen[yy * n + xx] and out.get_pixel(xx, yy).a > 0:
							seen[yy * n + xx] = true
							stack.append(Vector2i(xx, yy))
			if piece.size() < MIN_PIECE:
				for p in piece:
					out.set_pixel(p.x, p.y, Color(0, 0, 0, 0))
	return {"image": out, "cuts": smooth}
