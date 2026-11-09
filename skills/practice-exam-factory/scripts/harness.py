"""Item harness for the practice-exam factory.

A unit file WORK/fam_<UNIT>.py defines FAMILIES, a list of generator functions f(r) -> dict:
  topic    short label
  stem     the full question text (story, numbers, question); math in KaTeX \\( \\) only
  correct  display string of the right answer
  wrong    list of >= (options-1) display strings, each a real student mistake, most tempting first
  explain  worked solution a student can follow
  nota     optional bool: lets the harness use the "None of the above" option (numeric answers only)
  _p       optional dict of raw parameters, for the selftest
A family raises Reject to skip a bad parameter draw. Set f.n to the number of variants (default 22).
Family files import helpers with:  from harness import Reject, num, money, frac_tex
(`harness.py --init --work WORK` copies this file into WORK so family files and selftests can import it.)

WORK/concept_<UNIT>.json holds hand-written MC: [{"topic","stem","opts":[...],"ans":"A".."E","explain"}].
WORK/tf_<UNIT>.json holds true/false: [{"topic","stem","ans":"T"|"F","explain"}].

Run:  python3 harness.py --work WORK UNIT   -> builds the unit, checks MC and T/F, prints counts and 3 samples per family
"""
import argparse, json, random, re, sys, pathlib
from fractions import Fraction as Fr

MINUS = "−"


class Reject(Exception):
    pass


# ---------------------------------------------------------------- display helpers for family files
def num(x):
    """Integers plain, small fractions as a/b, else up to 2 decimals. Uses a true minus sign."""
    if isinstance(x, str):
        return x
    if isinstance(x, Fr):
        if x.denominator == 1:
            x = int(x)
        elif x.denominator <= 9 and abs(x.numerator) < 200:
            return (MINUS if x < 0 else "") + f"{abs(x.numerator)}/{x.denominator}"
        else:
            x = float(x)
    if isinstance(x, float):
        if abs(x - round(x)) < 1e-9:
            x = int(round(x))
        else:
            s = f"{abs(x):,.2f}".rstrip("0").rstrip(".")
            return (MINUS if x < 0 else "") + s
    s = f"{abs(x):,}" if abs(x) >= 10000 else str(abs(x))
    return (MINUS if x < 0 else "") + s


def money(x):
    s = num(x)
    return s.replace(MINUS, MINUS + "$") if s.startswith(MINUS) else "$" + s


def frac_tex(f):
    f = Fr(f)
    return str(f.numerator) if f.denominator == 1 else rf"\tfrac{{{f.numerator}}}{{{f.denominator}}}"


# ---------------------------------------------------------------- config
def load_config(work):
    cfg = json.loads((pathlib.Path(work) / "factory.json").read_text())
    cfg.setdefault("options", 5)
    cfg.setdefault("nota", "None of the above")
    for d in cfg.get("drop", []):
        if not (isinstance(d, list) and len(d) == 2):
            sys.exit(f'factory.json "drop" entries must be [unit, family] pairs, got {d!r}')
    for key in ("course", "exam", "n_exams", "units", "sections"):
        if key not in cfg:
            sys.exit(f"factory.json is missing {key!r}")
    return cfg


def shape(o):
    """Number format of an option: int, dec, frac or other."""
    o = o.replace(",", "").replace("$", "").replace(MINUS, "-").replace("%", "").strip()
    for name, pat in (("int", r"-?\d+"), ("dec", r"-?\d+\.\d+"), ("frac", r"-?\d+/\d+")):
        if re.fullmatch(pat, o):
            return name
    return "other"


def assemble(q, r, k, nota):
    """Pick k options. Rejects draws whose key gives itself away by its number format."""
    wrong = []
    for w in q["wrong"]:
        if w != q["correct"] and w not in wrong and w != nota:
            wrong.append(w)
    if len(wrong) < k - 1:
        raise Reject("too few distinct distractors")
    shapes = [shape(o) for o in [q["correct"]] + wrong[:k - 1]]
    if "other" not in shapes and shapes.count(shapes[0]) == 1:
        raise Reject("key is the only option of its number format")
    explain, roll = q["explain"], r.random()
    if q.get("nota") and roll < 0.12:  # the right value is missing, so NOTA is the answer
        opts = wrong[:k - 1]
        r.shuffle(opts)
        opts.append(nota)
        return opts, k - 1, f"The correct value is {q['correct']}, which is not listed. " + explain
    if q.get("nota") and roll < 0.3:  # NOTA shown as a distractor
        opts = [q["correct"]] + wrong[:k - 2]
        r.shuffle(opts)
        opts.append(nota)
    else:
        opts = [q["correct"]] + wrong[:k - 1]
        r.shuffle(opts)
    return opts, opts.index(q["correct"]), explain


def build(work, unit):
    """All MC items for one unit, plus a list of problems found."""
    work = pathlib.Path(work).resolve()
    cfg = load_config(work)
    k, nota = cfg["options"], cfg["nota"]
    letters = "ABCDEFGH"[:k]
    sys.modules.setdefault("harness", sys.modules[__name__])  # family files see this module, so Reject matches
    if str(work) not in sys.path:
        sys.path.insert(0, str(work))
    items, problems = [], []
    fam_file = work / f"fam_{unit}.py"
    if fam_file.exists():
        mod = __import__(f"fam_{unit}")
        for fam in mod.FAMILIES:
            want, seen, made = getattr(fam, "n", 22), set(), 0
            for seed in range(4000):
                if made >= want:
                    break
                r = random.Random(f"{unit}-{fam.__name__}-{seed}")
                try:
                    q = fam(r)
                    opts, ai, explain = assemble(q, r, k, nota)
                except Reject:
                    continue
                if q["stem"] in seen:
                    continue
                seen.add(q["stem"])
                made += 1
                items.append(dict(id=f"X-{unit}-{fam.__name__}-{made}", unit=unit, kind="mc", topic=q["topic"],
                                  family=fam.__name__, stem=q["stem"], opts=opts, ans=letters[ai], explain=explain))
            if made < want:
                problems.append(f"{fam.__name__}: only {made} of {want} variants")
    cfile = work / f"concept_{unit}.json"
    if cfile.exists():
        for n, c in enumerate(json.loads(cfile.read_text()), 1):
            items.append(dict(id=f"XC-{unit}-{n}", unit=unit, kind="mc", topic=c["topic"], family="concept",
                              stem=c["stem"], opts=c["opts"], ans=c["ans"], explain=c["explain"]))
    tfile = work / f"tf_{unit}.json"
    if tfile.exists():
        for n, t in enumerate(json.loads(tfile.read_text())):
            miss = [f for f in ("topic", "stem", "ans", "explain") if not t.get(f)]
            if miss or t.get("ans") not in ("T", "F"):
                problems.append(f"tf_{unit}.json index {n}: " + (f"missing {miss}" if miss else f"ans must be T or F, got {t.get('ans')!r}"))
            elif t["stem"].count(r"\(") != t["stem"].count(r"\)") or any("$" in m for m in re.findall(r"\\\((.*?)\\\)", t["stem"])):
                problems.append(f"tf_{unit}.json index {n}: math delimiters")
    for it in items:
        t = it["stem"] + " ".join(it["opts"]) + it["explain"]
        if len(it["opts"]) != k or len(set(it["opts"])) != k:
            problems.append(f"{it['id']}: options are not {k} distinct strings")
        if it["ans"] not in letters:
            problems.append(f"{it['id']}: bad answer letter {it['ans']}")
        if t.count(r"\(") != t.count(r"\)"):
            problems.append(f"{it['id']}: unbalanced \\( \\)")
        if any("$" in m for m in re.findall(r"\\\((.*?)\\\)", t, flags=re.S)):
            problems.append(f"{it['id']}: $ inside math")
        if re.search(r"\bnan\b|\binf\b", t):
            problems.append(f"{it['id']}: nan/inf")
    return items, problems


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--init", action="store_true", help="copy harness.py and a factory.json template into WORK")
    ap.add_argument("unit", nargs="?")
    a = ap.parse_args()
    if a.init:
        import shutil
        w = pathlib.Path(a.work)
        w.mkdir(parents=True, exist_ok=True)
        shutil.copy(__file__, w / "harness.py")  # family files and selftests import this copy
        if not (w / "factory.json").exists():
            shutil.copy(pathlib.Path(__file__).resolve().parent.parent / "assets" / "factory.example.json", w / "factory.json")
        print(f"initialized {w}: harness.py copied; edit factory.json")
        sys.exit(0)
    sys.modules["harness"] = sys.modules["__main__"]
    items, problems = build(a.work, a.unit)
    from collections import Counter
    print(f"{a.unit}: {len(items)} items", dict(Counter(i["family"] for i in items)))
    print("answer letters", dict(Counter(i["ans"] for i in items)))
    print("PROBLEMS:", problems or "none")
    shown = Counter()
    for it in items:
        if it["family"] != "concept" and shown[it["family"]] < 3:
            shown[it["family"]] += 1
            print(f"\n[{it['family']}] {it['stem']}\n  " + " | ".join(f"{'ABCDEFGH'[j]}) {o}" for j, o in enumerate(it["opts"]))
                  + f"\n  ANS {it['ans']}: {it['explain'][:300]}")
