"""Assemble N practice exams from the verified pools, with no question repeated across exams.

  python3 build_exams.py --work W [--pdf]

Reads W/factory.json, W/fam_<U>.py + W/concept_<U>.json (MC, via harness), W/tf_<U>.json (T/F),
optional W/import_*.json (already-verified items: unit, kind, topic, stem, opts, ans, explain),
and every W/review/key<R>_<U>.json with BLIND/grades<R>_<U>.json (blind grades; later rounds win).

Rules: each exam follows factory.json "sections"; each section spreads its count over the units, rotating
the remainder; one exam never gets two variants of one family; families in "drop" and hand-written items
graded not exam-like are left out; caps limit beyond-the-slides and very hard (>= 4.5) items per exam.
Writes W/out/exams.html (exam app) and W/out/exams_print.html; --pdf also prints W/out/exams.pdf
with headless Chrome and counts KaTeX errors.
"""
import argparse, json, random, re, statistics, subprocess, shutil, sys, pathlib
from collections import Counter, defaultdict

SKILL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
from harness import build, load_config  # noqa: E402
from review import blind_dir  # noqa: E402


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def esc_math(t):
    """A raw < or > inside \\( \\) reads as an HTML tag in the browser, so escape it."""
    return re.sub(r"\\\((.*?)\\\)", lambda m: m.group(0).replace("<", "&lt;").replace(">", "&gt;"), t, flags=re.S)


def load_grades(work, unit_ids, bd):
    rev = pathlib.Path(work) / "review"
    fam_by_round, by_stem = defaultdict(dict), {}
    rounds = sorted({int(m.group(1)) for f in bd.glob("grades*_*.json") if (m := re.match(r"grades(\d+)_", f.name))})
    for rnd in rounds:
        for u in unit_ids:
            kf, gf = rev / f"key{rnd}_{u}.json", bd / f"grades{rnd}_{u}.json"
            if not (kf.exists() and gf.exists()):
                continue
            key = {k["q"]: k for k in json.loads(kf.read_text())}
            for g in json.loads(gf.read_text()):
                k = key.get(g["q"])
                if not k:
                    continue
                if k["family"] in ("concept", "tf"):
                    by_stem[norm(k["stem"])] = g
                else:
                    fam_by_round[(u, k["family"])].setdefault(rnd, []).append(g)
    fgrade = {}
    for f, by_r in fam_by_round.items():
        gs = by_r[max(by_r)]  # the latest round that sampled this family
        fgrade[f] = dict(difficulty=statistics.mean(g.get("difficulty", 3) for g in gs),
                         beyond=sum(not g.get("in_slides", True) for g in gs) * 2 > len(gs))
    return fgrade, by_stem


def split(count, n_units, e):
    """Spread count over n_units; the remainder rotates with the exam number."""
    base, rem = divmod(count, n_units)
    return [base + (1 if (j - e * rem) % n_units < rem else 0) for j in range(n_units)]


def main(work, pdf):
    work = pathlib.Path(work).resolve()
    cfg = load_config(work)
    uids = [u["id"] for u in cfg["units"]]
    caps = dict(beyond_mc=3, beyond_tf=2, hard_mc=1) | cfg.get("caps", {})
    drop = {tuple(d) for d in cfg.get("drop", [])}
    r = random.Random(cfg.get("seed", 1))
    fgrade, by_stem = load_grades(work, uids, blind_dir(cfg))
    skipped = Counter()

    def keep_single(it):
        g = by_stem.get(norm(it["stem"]))
        if g and not g.get("exam_like", True):
            skipped[f"{it['kind']} graded not exam-like"] += 1
            return False
        it["difficulty"] = g.get("difficulty", 3) if g else 3
        it["beyond"] = bool(g) and not g.get("in_slides", True)
        return True

    # pools: MC as per-unit family queues; T/F as per-unit lists
    mcq, tfq = {}, defaultdict(list)
    for u in uids:
        items, problems = build(work, u)
        if problems:
            sys.exit(f"{u}: harness problems, fix them first: {problems}")
        fams = defaultdict(list)
        for it in items:
            if (u, it["family"]) in drop:
                skipped["dropped family"] += 1
                continue
            if it["family"] == "concept":
                if not keep_single(it):
                    continue
            else:
                fg = fgrade.get((u, it["family"]), dict(difficulty=3, beyond=False))
                it["difficulty"], it["beyond"] = round(fg["difficulty"], 1), fg["beyond"]
            fams[it["family"]].append(it)
        for v in fams.values():
            r.shuffle(v)
        # each generated type has about 22 items; give the hand-written pool one slot per 22 items so it is drawn at its share
        order = list(fams) + ["concept"] * max(0, len(fams.get("concept", [])) // 22 - 1)
        r.shuffle(order)
        mcq[u] = [order, fams, 0]
        f = work / f"tf_{u}.json"
        for n, t in enumerate(json.loads(f.read_text()) if f.exists() else [], 1):
            it = dict(id=f"T-{u}-{n}", unit=u, kind="tf", topic=t["topic"], stem=t["stem"], opts=None, ans=t["ans"], explain=t["explain"])
            if keep_single(it):
                tfq[u].append(it)
    for f in sorted(work.glob("import_*.json")):
        for n, t in enumerate(json.loads(f.read_text()), 1):
            bad = [k for k in ("unit", "kind", "topic", "stem", "ans", "explain") if not t.get(k)]
            if bad or t["unit"] not in uids or t["kind"] not in ("mc", "tf") or (t["kind"] == "mc" and len(t.get("opts") or []) != cfg["options"]):
                sys.exit(f"{f.name} item {n}: missing {bad}, unknown unit or kind, or wrong option count")
            it = dict(t, id=f"I-{f.stem}-{n}", difficulty=t.get("difficulty", 3), beyond=t.get("beyond", False), family=f.stem)
            if it["kind"] == "tf":
                tfq[it["unit"]].append(it)
            else:
                mcq[it["unit"]][1].setdefault(f"{f.stem}-{n}", []).append(it)
                mcq[it["unit"]][0].append(f"{f.stem}-{n}")
    for v in tfq.values():
        r.shuffle(v)

    # feasibility: say exactly how many exams the pools support before assembling
    n = cfg["n_exams"]
    for kind in ("mc", "tf"):
        need = sum(s["count"] for s in cfg["sections"] if s["kind"] == kind) * n
        have = sum(sum(len(v) for v in mcq[u][1].values()) for u in uids) if kind == "mc" else sum(len(v) for v in tfq.values())
        if need > have:
            per = max(1, need // n)
            sys.exit(f"Not enough {kind.upper()} items: {n} exams need {need}, the pool has {have} "
                     f"(enough for {have // per} exams). Write more items or lower n_exams.")

    def take_mc(u, used, chosen):
        order, fams, pos = mcq[u]
        nb = sum(i["beyond"] for i in chosen if i["kind"] == "mc")
        nh = sum(i["difficulty"] >= 4.5 for i in chosen if i["kind"] == "mc")
        for relax in (False, True):  # relax the caps only if the unit has nothing else left
            for step in range(len(order)):
                f = order[(pos + step) % len(order)]
                if not fams[f] or (u, f) in used:
                    continue
                it = fams[f][-1]
                if not relax and ((it["beyond"] and nb >= caps["beyond_mc"]) or (it["difficulty"] >= 4.5 and nh >= caps["hard_mc"])):
                    continue
                mcq[u][2] = (pos + step + 1) % len(order)
                if f != "concept":  # hand-written items are all different, so several may share an exam
                    used.add((u, f))
                return fams[f].pop()
        return None

    def take_tf(u, chosen):
        pool = tfq[u]
        if not pool:
            return None
        nb = sum(i["beyond"] for i in chosen if i["kind"] == "tf")
        idx = [j for j in range(len(pool)) if not (pool[j]["beyond"] and nb >= caps["beyond_tf"])] or list(range(len(pool)))
        return pool.pop(idx[-1])

    exams = []
    for e in range(n):
        qs, used = [], set()
        for sec in cfg["sections"]:
            chosen = []
            for j, c in enumerate(split(sec["count"], len(uids), e)):
                for _ in range(c):
                    # preferred unit first, then whichever unit has the most left
                    for u in [uids[j]] + sorted(uids, key=lambda x: -(len(tfq[x]) if sec["kind"] == "tf" else sum(len(v) for v in mcq[x][1].values()))):
                        it = take_mc(u, used, qs + chosen) if sec["kind"] == "mc" else take_tf(u, qs + chosen)
                        if it:
                            chosen.append(it)
                            break
            r.shuffle(chosen)
            qs += chosen
        mcs = [i for i in qs if i["kind"] == "mc"]
        exams.append(dict(n=e + 1, difficulty=round(statistics.mean(i["difficulty"] for i in mcs), 2) if mcs else None, qs=qs))

    ids = [i["id"] for ex in exams for i in ex["qs"]]
    per_exam = sum(s["count"] for s in cfg["sections"])
    assert len(ids) == len(set(ids)) == n * per_exam, "a question repeats or an exam is short"
    for ex in exams:
        for i in ex["qs"]:
            i["stem"], i["explain"] = esc_math(i["stem"]), esc_math(i["explain"])
            if i.get("opts"):
                i["opts"] = [esc_math(o) for o in i["opts"]]
    keep = ("id", "unit", "kind", "topic", "stem", "opts", "ans", "explain", "difficulty", "beyond")
    data = [dict(n=ex["n"], difficulty=ex["difficulty"], qs=[{k: i.get(k) for k in keep} for i in ex["qs"]]) for ex in exams]
    out = work / "out"
    out.mkdir(exist_ok=True)
    conf = dict(title=f"{cfg['course']} {cfg['exam']} · {n} Practice Exams", minutes=cfg.get("minutes"),
                sections=cfg["sections"], total=sum(s["count"] * s["points"] for s in cfg["sections"]),
                key=f"pef:{re.sub(r'[^a-z0-9]+', '-', (cfg['course'] + cfg['exam']).lower())}:v1",
                units={u["id"]: u.get("name", u["id"]) for u in cfg["units"]})
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    app = (SKILL / "assets" / "exams_app.html").read_text().replace("/*__CONFIG__*/{}", js(conf)).replace("/*__EXAMS__*/[]", js(data))
    (out / "exams.html").write_text(app.replace("__TITLE__", conf["title"]))
    (out / "exams_print.html").write_text(print_html(conf, data))

    d = [ex["difficulty"] for ex in exams if ex["difficulty"] is not None]
    print(f"{n} exams x {per_exam} questions, {len(ids)} distinct")
    if d:
        print(f"MC difficulty per exam: min {min(d)}, mean {statistics.mean(d):.2f}, max {max(d)}")
    print("by unit:", dict(Counter(i["unit"] for i in ids_items(exams))))
    print("MC answer letters:", dict(Counter(i["ans"] for i in ids_items(exams) if i["kind"] == "mc")))
    print("left out:", dict(skipped))
    print("beyond-slides MC per exam:", dict(Counter(sum(i["beyond"] for i in ex["qs"] if i["kind"] == "mc") for ex in exams)))
    print("wrote", out / "exams.html", "and", out / "exams_print.html")
    if pdf:
        print_pdf(out)


def ids_items(exams):
    return [i for ex in exams for i in ex["qs"]]


def print_html(conf, exams):
    L = "ABCDEFGH"
    parts, toc = [], []
    for ex in exams:
        n = ex["n"]
        toc.append(f'<a href="#e{n}">{n}</a>')
        qs, keys, k, kinds = [], [], 0, []
        for sec in conf["sections"]:
            qs.append(f'<h3>{sec["title"]} ({sec["points"]} points each)</h3>')
            for _ in range(sec["count"]):
                i = ex["qs"][k]
                k += 1
                body = ('<ol class="opts">' + "".join(f"<li>{L[j]}) {o}</li>" for j, o in enumerate(i["opts"])) + "</ol>") if i["kind"] == "mc" else ""
                qs.append(f'<div class="q"><b>{k}.</b> {i["stem"]}{body}</div>')
                ans = i["ans"] if i["kind"] == "mc" else ("True" if i["ans"] == "T" else "False")
                tag = f'{conf["units"].get(i["unit"], i["unit"])} · {i["topic"]}' + (f' · difficulty {i["difficulty"]}' if i["kind"] == "mc" else "")
                if i.get("beyond"):
                    tag += " · textbook, beyond the slides"
                keys.append(f'<div class="a"><b>{k}. {ans}.</b> <span class="k">{tag}</span> {i["explain"]}</div>')
        diff = f' · multiple-choice difficulty {ex["difficulty"]} of 5' if ex["difficulty"] is not None else ""
        mins = f' · {conf["minutes"]} minutes' if conf.get("minutes") else ""
        parts.append(f'<section><h2 id="e{n}">Practice Exam {n}</h2><p class="meta">{conf["total"]} points{mins}{diff}</p>{"".join(qs)}'
                     f'<h2 class="key">Practice Exam {n}: answer key</h2>{"".join(keys)}</section>')
    fmt = ", then ".join(f'{s["count"]} {s["title"].lower()} ({s["points"]} points each)' for s in conf["sections"])
    return PRINT.replace("__TITLE__", conf["title"]).replace("__FORMAT__", fmt).replace("__TOC__", " · ".join(toc)).replace("__BODY__", "".join(parts))


def chrome():
    for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium", "chromium-browser"]:
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    sys.exit("No Chrome or Chromium found for the PDF step.")


def print_pdf(out):
    ch, page = chrome(), f"file://{out / 'exams_print.html'}"
    budget = "--virtual-time-budget=150000"  # KaTeX loads from a CDN and renders tens of thousands of formulas
    subprocess.run([ch, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", budget, f"--print-to-pdf={out / 'exams.pdf'}", page],
                   capture_output=True, timeout=900)
    dom = subprocess.run([ch, "--headless=new", "--disable-gpu", budget, "--dump-dom", page], capture_output=True, text=True, timeout=900).stdout
    rendered, errors = dom.count('class="katex"'), dom.count("katex-error")
    pdf = out / "exams.pdf"
    if not pdf.exists() or pdf.stat().st_size < 10000:
        sys.exit("PDF step failed: no PDF written. Check Chrome and network access to the KaTeX CDN.")
    if errors or (rendered == 0 and "\\(" in (out / "exams_print.html").read_text()):
        sys.exit(f"PDF math check failed: KaTeX rendered {rendered}, errors {errors}. The CDN may be unreachable, or a formula is malformed.")
    print(f"PDF: {pdf} · KaTeX rendered {rendered}, errors {errors}")


PRINT = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>__TITLE__</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
@page{size:Letter;margin:0.6in 0.6in 0.7in}
body{font:10.5pt/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif;color:#111}
h1{font-size:22pt;margin:0 0 6px}
h2{font-size:16pt;color:#1e3a8a;border-bottom:2px solid #1e3a8a;padding-bottom:3px;break-before:page;margin:0 0 4px}
h2.key{color:#7c2d12;border-color:#7c2d12}
h3{font-size:11.5pt;margin:12px 0 6px}
.meta{color:#555;font-size:9.5pt;margin:0 0 8px}
.q{break-inside:avoid;margin:0 0 12px}
.a{break-inside:avoid;margin:0 0 8px;font-size:9.5pt}
.k{font-size:8.5pt;color:#555}
.opts{list-style:none;margin:3px 0 0;padding-left:16px}
a{color:#1e3a8a}
</style></head><body>
<h1>__TITLE__</h1>
<p>Each exam copies the real format: __FORMAT__. No question appears twice across the exams. The answer key follows each exam, with the unit, the topic, a 1 to 5 difficulty (3 = a typical question on the instructor's practice exam) and a worked solution. "Textbook, beyond the slides" marks content the lecture slides do not teach.</p>
<p>Take one exam under time, score it, then read the solution to every question you missed or guessed.</p>
<p><b>Exams:</b> __TOC__</p>
__BODY__
<script>renderMathInElement(document.body,{delimiters:[{left:"\\[",right:"\\]",display:true},{left:"\\(",right:"\\)",display:false}],throwOnError:false});</script>
</body></html>"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    main(a.work, a.pdf)
