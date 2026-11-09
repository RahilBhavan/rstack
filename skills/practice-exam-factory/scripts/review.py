"""Blind-review plumbing: make keyless question files, then compare reviewer grades with the keys.

  python3 review.py blind   --work W --round R [--per-family 2] [--handwritten all|sample|changed|none]
  python3 review.py compare --work W --round R

blind writes the question files to the BLIND folder, outside WORK, so a reviewer never learns where keys and
generators live: BLIND = factory.json "blind_dir", default /tmp/pef_blind/<course-exam>.
  BLIND/blind<R>_<U>.txt    what the reviewer reads
  BLIND/grades<R>_<U>.json  what the reviewer writes: [{"q","ans","difficulty","exam_like","in_slides","note"}]
Keys and family fingerprints stay in W/review/ (key<R>_<U>.json, fingerprint<R>.json).

--handwritten changed picks what needs a new look, computed by the scripts rather than reported by writers:
  families whose 22 variants differ from the last fingerprint, hand-written items whose stem no round has graded,
  and items a reviewer skipped (W/review/ungraded_<U>.json, written by compare).
compare prints exact-match agreement, every disagreement or AMBIGUOUS with the item, flagged families,
and writes W/review/notes<R>_<U>.txt (every note or not-exam-like item) for the writers' fix round.
"""
import argparse, hashlib, json, random, re, sys, pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from harness import build, load_config  # noqa: E402

VALID = {"A", "B", "C", "D", "E", "F", "G", "H", "T"}


def units(cfg):
    return [u["id"] for u in cfg["units"]]


def blind_dir(cfg):
    slug = re.sub(r"[^a-z0-9]+", "-", f"{cfg['course']}-{cfg['exam']}".lower()).strip("-")
    d = pathlib.Path(cfg.get("blind_dir", f"/tmp/pef_blind/{slug}"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def tf_items(work, unit):
    f = pathlib.Path(work) / f"tf_{unit}.json"
    return json.loads(f.read_text()) if f.exists() else []


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def fingerprint(items):
    by = defaultdict(list)
    for i in items:
        if i["family"] != "concept":
            by[i["family"]].append(i["stem"] + "|".join(i["opts"]) + i["ans"] + i["explain"])
    return {f: hashlib.sha1("\n".join(v).encode()).hexdigest() for f, v in by.items()}


def graded_stems(rev, upto):
    seen = set()
    for kf in rev.glob("key*_*.json"):
        m = re.match(r"key(\d+)_", kf.name)
        if m and int(m.group(1)) < upto:
            seen |= {norm(k["stem"]) for k in json.loads(kf.read_text())}
    return seen


def last_fingerprint(rev, upto):
    rounds = sorted(int(m.group(1)) for f in rev.glob("fingerprint*.json") if (m := re.match(r"fingerprint(\d+)", f.name)) and int(m.group(1)) < upto)
    return json.loads((rev / f"fingerprint{rounds[-1]}.json").read_text()) if rounds else {}


def blind(work, rnd, per_family, handwritten):
    cfg = load_config(work)
    rev, bd = pathlib.Path(work) / "review", blind_dir(cfg)
    rev.mkdir(exist_ok=True)
    seen, old_fp, new_fp = graded_stems(rev, rnd), last_fingerprint(rev, rnd), {}
    for u in units(cfg):
        items, problems = build(work, u)
        if problems:
            sys.exit(f"{u}: fix harness problems first: {problems}")
        fp = fingerprint(items)
        new_fp.update({f"{u}/{f}": h for f, h in fp.items()})
        r = random.Random(f"round{rnd}-{u}")
        con = [i for i in items if i["family"] == "concept"]
        tf = tf_items(work, u)
        fams = sorted(fp)
        uf = pathlib.Path(rev) / f"ungraded_{u}.json"
        skipped = json.loads(uf.read_text()) if uf.exists() else {"concept": [], "tf": [], "families": []}
        if handwritten == "changed":
            fams = sorted({f for f in fams if old_fp.get(f"{u}/{f}") != fp[f]} | set(skipped["families"]))
            cidx = sorted({k for k, c in enumerate(con) if norm(c["stem"]) not in seen} | set(skipped["concept"]))
            tfi = sorted({k for k, t in enumerate(tf) if norm(t["stem"]) not in seen} | set(skipped["tf"]))
        elif handwritten == "all":
            cidx, tfi = list(range(len(con))), list(range(len(tf)))
        elif handwritten == "sample":
            cidx = sorted(r.sample(range(len(con)), min(10, len(con))))
            tfi = sorted(r.sample(range(len(tf)), min(25, len(tf))))
        else:
            cidx, tfi = [], []
        mc = []
        for f in fams:
            pool = [i for i in items if i["family"] == f]
            mc += r.sample(pool, min(per_family, len(pool)))
        mc += [con[k] for k in cidx]
        lines, key = [], []
        for n, i in enumerate(mc, 1):
            lines.append(f"M{n}. {i['stem']}\n" + "\n".join(f"   {'ABCDEFGH'[j]}) {o}" for j, o in enumerate(i["opts"])))
            key.append(dict(q=f"M{n}", id=i["id"], family=i["family"], ans=i["ans"], stem=i["stem"],
                            cidx=int(i["id"].rsplit("-", 1)[1]) - 1 if i["family"] == "concept" else None))
        for n, j in enumerate(tfi, 1):
            lines.append(f"T{n}. {tf[j]['stem']}  (True or False)")
            key.append(dict(q=f"T{n}", idx=j, family="tf", ans=tf[j]["ans"], stem=tf[j]["stem"]))
        (bd / f"blind{rnd}_{u}.txt").write_text("\n\n".join(lines))
        (rev / f"key{rnd}_{u}.json").write_text(json.dumps(key, ensure_ascii=False, indent=0))
        print(f"{u}: {len(mc)} MC ({len(fams)} families), {len(tfi)} T/F -> {bd / f'blind{rnd}_{u}.txt'}")
    (rev / f"fingerprint{rnd}.json").write_text(json.dumps(new_fp, indent=0))
    print(f"\nReviewers write their grades to {bd}/grades{rnd}_<UNIT>.json")


def compare(work, rnd):
    cfg = load_config(work)
    rev, bd = pathlib.Path(work) / "review", blind_dir(cfg)
    drop = {tuple(d) for d in cfg.get("drop", [])}
    agree = total = 0
    fam = defaultdict(list)
    for u in units(cfg):
        key = {k["q"]: k for k in json.loads((rev / f"key{rnd}_{u}.json").read_text())}
        gf = bd / f"grades{rnd}_{u}.json"
        if not gf.exists():
            print(f"{u}: no grades file yet at {gf}")
            continue
        grades = json.loads(gf.read_text())
        missing = [key[q] for q in sorted(set(key) - {g["q"] for g in grades})]
        un = {"concept": [k["cidx"] for k in missing if k["family"] == "concept"],
              "tf": [k["idx"] for k in missing if k["family"] == "tf"],
              "families": sorted({k["family"] for k in missing if k["family"] not in ("concept", "tf")})}
        (rev / f"ungraded_{u}.json").write_text(json.dumps(un))  # rewritten every compare, so it holds this round's gaps only
        if missing:
            print(f"{u}: {len(missing)} UNGRADED ({[k['q'] for k in missing]}). The next 'blind --handwritten changed' includes them.")
        items = {i["id"]: i for i in build(work, u)[0]}
        tf = tf_items(work, u)
        notes = []
        for g in grades:
            k = key[g["q"]]
            total += 1
            ans = str(g["ans"]).strip().upper()
            ans = {"TRUE": "T", "FALSE": "F"}.get(ans, ans)
            ok = ans == k["ans"]  # exact match: "AMBIGUOUS" must never count as "A"
            agree += ok
            if k["family"] not in ("concept", "tf"):
                fam[(u, k["family"])].append(g)
            body = items.get(k.get("id"))
            if not ok:
                label = "AMBIGUOUS" if ans not in VALID else f"reviewer {ans}"
                print(f"\n--- {u} {g['q']} [{k['family']}] key {k['ans']} vs {label}\n    note: {g.get('note', '')}\n    stem: {k['stem'][:400]}")
                if body:
                    print(f"    opts: {body['opts']}\n    explain: {body['explain'][:500]}")
                elif "idx" in k and k["idx"] < len(tf):
                    print(f"    explain: {tf[k['idx']]['explain'][:400]}")
            if (u, k["family"]) in drop:
                continue
            if g.get("note") or not g.get("exam_like", True) or not ok:
                where = (f"family {k['family']}" if k["family"] not in ("concept", "tf")
                         else f"concept_{u}.json index {k['cidx']}" if k["family"] == "concept" else f"tf_{u}.json index {k['idx']}")
                opts = f"\nOPTIONS: {body['opts']}" if body else ""
                notes.append(f"[{where}] key={k['ans']} reviewer={ans} exam_like={g.get('exam_like')} "
                             f"in_slides={g.get('in_slides')} difficulty={g.get('difficulty')}\nREVIEWER: {g.get('note', '')}\nSTEM: {k['stem']}{opts}")
        (rev / f"notes{rnd}_{u}.txt").write_text("\n\n".join(notes))
        print(f"{u}: {len(notes)} notes -> review/notes{rnd}_{u}.txt")
    print(f"\nAGREEMENT {agree} of {total} (exact match; solve every miss yourself before deciding who is right)")
    print("\nFLAGGED FAMILIES (exam-like in at most 1/3 of samples, mean difficulty >= 4.5, or mostly beyond the slides):")
    for f, gs in sorted(fam.items()):
        n = len(gs)
        like = sum(bool(g.get("exam_like", True)) for g in gs)
        inside = sum(bool(g.get("in_slides", True)) for g in gs)
        d = sum(g.get("difficulty", 3) for g in gs) / n
        if like * 3 <= n or d >= 4.5 or inside * 2 < n:
            print(f"  {list(f)}: difficulty {d:.1f}, exam-like {like}/{n}, in slides {inside}/{n}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["blind", "compare"])
    ap.add_argument("--work", required=True)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--per-family", type=int, default=2)
    ap.add_argument("--handwritten", choices=["all", "sample", "changed", "none"], default="all")
    a = ap.parse_args()
    if a.cmd == "blind":
        blind(a.work, a.round, a.per_family, a.handwritten)
    else:
        compare(a.work, a.round)
