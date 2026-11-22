"""Sweep an animated prop and report parts that pass through each other.

usage: blender -b --factory-startup -P overlap_check.py -- in.(glb|blend)
           [--action NAME | --all-actions] [--step N] [--rest FRAME] [--ignore a,b] [--strict]
           [--out report.json]

Every mesh object is one part. Two parts that do not touch at the rest frame (default: the first frame
of the action) must not touch at any other frame: that is a clash, and it fails the check. Parts that
already touch at rest (a lid on its hinge barrel, a tyre on the road, a bolted bracket) are "joined":
a spinning or sliding joined part keeps bringing new triangles into contact, which is not a clash, so
those are only listed as "contact changed". --strict fails on them too (use it for parts that should
keep exactly the contact they have at rest). Meshes are read after modifiers and armatures, so skinned meshes are checked too (between
separate objects only; a single skinned mesh is not checked against itself).

--all-actions checks every clip (the param-clip export of bpy_kit makes one clip per 0-1 control, so
this sweeps every control over its whole range). Exit 1 on any clash. Method after AnyMachine's
check.py (apekshik/anymachine, MIT): overlaps relative to the rest pose, every frame, machine-read.
"""
import json
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def args():
    a = sys.argv[sys.argv.index("--") + 1:]
    o = {"path": a[0], "action": None, "all": False, "step": 1, "rest": None, "ignore": [], "out": None,
         "strict": False}
    i = 1
    while i < len(a):
        k = a[i]
        if k == "--all-actions":
            o["all"] = True
        elif k == "--strict":
            o["strict"] = True
        else:
            v = a[i + 1]
            i += 1
            if k == "--action":
                o["action"] = v
            elif k == "--step":
                o["step"] = max(1, int(v))
            elif k == "--rest":
                o["rest"] = int(v)
            elif k == "--ignore":
                o["ignore"] = [s.strip() for s in v.split(",") if s.strip()]
            elif k == "--out":
                o["out"] = v
        i += 1
    return o


def load(path):
    if path.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=path)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=path)


def use_action(name):
    """Make `name` the active action on every object that has it in an NLA strip (glTF import puts each
    clip in a muted strip and leaves only one clip active)."""
    hits = 0
    for ob in bpy.data.objects:
        ad = ob.animation_data
        if not ad:
            continue
        found = None
        for t in ad.nla_tracks:
            for s in t.strips:
                if s.action and s.action.name == name:
                    found = s
        if found:
            ad.action = found.action
            if hasattr(ad, "action_slot") and getattr(found, "action_slot", None):
                ad.action_slot = found.action_slot
            hits += 1
        elif ad.action and ad.action.name != name:
            ad.action = None  # another clip would leak into this sweep
    act = bpy.data.actions.get(name)
    return act, hits


def tree(ob, dg):
    """World-space BVH of the evaluated mesh (modifiers and armature applied)."""
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys, all_triangles=False) if polys else None


def deforms(ob):
    return any(m.type in ("ARMATURE", "MESH_DEFORM", "LATTICE", "HOOK") for m in ob.modifiers) or \
        (ob.data.shape_keys is not None)


def drift(corners, r, r0):
    """How far b's bounding-box corners moved in a's space between the rest pose and now."""
    return max((r @ c - r0 @ c).length for c in corners)


def snapshot(parts, frame, rest_rel=None):
    """Triangle pairs that intersect, per part pair. With rest_rel, a pair whose relative transform is
    the same as at rest (riding on one hinge, e.g. a glass pane in its hatch) and that does not deform is
    skipped: it cannot clash anew, and coplanar faces only produce float noise."""
    sc = bpy.context.scene
    sc.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    mats = {ob.name: ob.evaluated_get(dg).matrix_world.copy() for ob in parts}
    rigid = {ob.name: not deforms(ob) for ob in parts}
    trees = {ob.name: tree(ob, dg) for ob in parts}
    boxes = {ob.name: [Vector(c) for c in ob.bound_box] for ob in parts}
    size = {n: (max(bx, key=lambda v: v.x + v.y + v.z) - min(bx, key=lambda v: v.x + v.y + v.z)).length
            for n, bx in boxes.items()}
    out, rel = {}, {}
    names = sorted(trees)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = mats[a].inverted_safe() @ mats[b]
            rel[(a, b)] = r
            if rest_rel is not None and rigid[a] and rigid[b] and drift(boxes[b], r, rest_rel[(a, b)]) <= \
                    1e-3 * size[b]:
                continue  # b has not moved relative to a (0.1 % of its size): keyframe float noise only
            if trees[a] and trees[b]:
                hit = trees[a].overlap(trees[b])
                if hit:
                    out[(a, b)] = set(hit)
    return out, rel


def sweep(parts, first, last, step, rest):
    base, rest_rel = snapshot(parts, rest)
    rows, clashes, changed = [], {}, {}
    frames = list(range(first, last + 1, step))
    if frames[-1] != last:
        frames.append(last)
    for f in frames:
        now, _ = snapshot(parts, f, rest_rel)
        new = {}
        for pair, hit in now.items():
            extra = hit - base.get(pair, set())
            if extra:
                k = f"{pair[0]} x {pair[1]}"
                new[k] = len(extra)
                c = (changed if pair in base else clashes).setdefault(k, {"frames": [], "max_tris": 0})
                c["frames"].append(f)
                c["max_tris"] = max(c["max_tris"], len(extra))
        rows.append({"frame": f, "new_triangle_pairs": new})
    return {"rest_frame": rest, "frames": [first, last, step],
            "joined_at_rest": sorted(f"{a} x {b}" for a, b in base),
            "clashes": clashes, "contact_changed": changed, "rows": rows}


def main():
    o = args()
    load(o["path"])
    parts = [ob for ob in bpy.data.objects if ob.type == "MESH" and ob.name not in o["ignore"]]
    sc = bpy.context.scene
    if o["all"]:
        names = [a.name for a in bpy.data.actions]
    elif o["action"]:
        names = [o["action"]]
    else:
        names = [None]
    report, ok = {"file": o["path"], "parts": len(parts), "actions": {}}, True
    for name in names:
        if name:
            act, hits = use_action(name)
            if not act or not hits:
                print(f"OVERLAP_CHECK no objects carry action {name!r}")
                ok = False
                continue
            first, last = (int(round(x)) for x in act.frame_range)
        else:
            acts = [ob.animation_data.action for ob in bpy.data.objects
                    if ob.animation_data and ob.animation_data.action]
            if acts:
                first = min(int(round(a.frame_range[0])) for a in acts)
                last = max(int(round(a.frame_range[1])) for a in acts)
            else:
                first, last = sc.frame_start, sc.frame_end
        rest = o["rest"] if o["rest"] is not None else first
        r = sweep(parts, first, last, o["step"], rest)
        label = name or "active"
        report["actions"][label] = r
        bad = dict(r["clashes"], **(r["contact_changed"] if o["strict"] else {}))
        info = {} if o["strict"] else r["contact_changed"]
        if bad:
            ok = False
            print(f"OVERLAP_CHECK {label}: FAIL {len(bad)} part pairs pass through each other")
        else:
            print(f"OVERLAP_CHECK {label}: PASS no clash, {len(parts)} parts, frames {first}..{last} "
                  f"step {o['step']}, {len(r['joined_at_rest'])} pairs joined at rest")
        for tag, group in (("clash", bad), ("contact changed (joined at rest, not a failure)", info)):
            for k, c in sorted(group.items(), key=lambda kv: -kv[1]["max_tris"])[:8]:
                print(f"OVERLAP_CHECK   {tag}: {k}: frames {c['frames'][0]}..{c['frames'][-1]} "
                      f"({len(c['frames'])} sampled), up to {c['max_tris']} new triangle pairs")
    if o["out"]:
        with open(o["out"], "w") as fh:
            json.dump(report, fh, indent=1)
    print("OVERLAP_CHECK " + ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


main()
