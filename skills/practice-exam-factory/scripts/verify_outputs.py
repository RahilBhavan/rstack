"""Check the built outputs before reporting done.

  uv run --with pymupdf python verify_outputs.py --work W

1. PDF: one answer-key line per question (N x questions per exam), one key section per exam, and no raw \\( in the text.
2. App: opens out/exams.html in headless Chrome, answers exam 1 correctly except question 2, submits,
   opens the mistakes view, and checks the score and the mistake count.
Exits nonzero on any failure.
"""
import argparse, json, re, subprocess, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from harness import load_config  # noqa: E402
from build_exams import chrome  # noqa: E402


def main(work):
    work = pathlib.Path(work).resolve()
    cfg = load_config(work)
    out = work / "out"
    n, per = cfg["n_exams"], sum(s["count"] for s in cfg["sections"])
    total = sum(s["count"] * s["points"] for s in cfg["sections"])
    fails = []

    import pymupdf
    text = "".join(p.get_text() for p in pymupdf.open(out / "exams.pdf"))
    keys = len(re.findall(r"\n(\d+)\. (True|False|[A-H])\.", text))
    sections = len(re.findall(r"Practice Exam \d+: answer key", text))
    print(f"PDF: {keys} key lines (want {n * per}), {sections} key sections (want {n}), raw \\( {text.count(chr(92) + '(')}")
    if keys != n * per or sections != n or chr(92) + "(" in text:
        fails.append("PDF counts")

    points = [s["points"] for s in cfg["sections"] for _ in range(s["count"])]
    want = total - points[1]
    page = (out / "exams.html").read_text().replace("fillPick(); show(); record();\n</script>", """fillPick(); show(); record();
EXAMS[cur].qs.forEach((q,k)=>{ if(k!==1) document.querySelector(`#q${k} input[value="${q.ans}"]`).checked=true; });
submit();
const sc = document.querySelector(".score").textContent;
document.getElementById("missed").click();
const mm = (document.body.innerHTML.match(/Your mistakes \\((\\d+)\\)/) || [])[1];
document.body.insertAdjacentHTML("beforeend", `<p id="pef-test">${sc}|${mm}|${document.querySelectorAll(".katex-error").length}</p>`);
</script>""")
    test = out / "_apptest.html"
    test.write_text(page)
    dom = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--virtual-time-budget=30000", "--dump-dom", f"file://{test}"],
                         capture_output=True, text=True, timeout=300).stdout
    test.unlink()
    m = re.findall(r'id="pef-test">Score: (\d+) / (\d+)[^|]*\|(\d+)\|(\d+)', dom)
    print(f"App: {m[-1] if m else 'no result'} (want score {want}/{total}, 1 mistake, 0 KaTeX errors)")
    if not m or (int(m[-1][0]), int(m[-1][1]), int(m[-1][2]), int(m[-1][3])) != (want, total, 1, 0):
        fails.append("app test")
    if fails:
        sys.exit("FAILED: " + ", ".join(fails))
    print("ALL OUTPUT CHECKS PASSED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    main(ap.parse_args().work)
