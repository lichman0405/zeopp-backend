"""End-to-end smoke test using a real Zeo++ binary on HKUST-1.cif.

Exercises every analysis whose parser was rewritten to confirm:
  - No silent zeros / "is not in list" warnings
  - Optional channel/pocket extension fields populate when emitted
  - Strict-mode errors do not trigger on real Zeo++ output
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from app.core.runner import ZeoRunner
from app.utils import parser as P

runner = ZeoRunner()


CIF = Path("examples/sample_structures/HKUST-1.cif").resolve()


def run(args: list[str], outputs: list[str], tag: str) -> dict:
    with TemporaryDirectory() as tmp:
        wd = Path(tmp)
        shutil.copy(CIF, wd / CIF.name)
        # Ensure runner writes into our scratch dir by overriding the
        # workspace lookup: easiest is to call _run_with_sh directly.
        zeo_args = list(args) + [CIF.name]
        ok, code, out, err = runner._run_with_sh(zeo_args, wd)  # noqa: SLF001
        result = {"ok": ok, "code": code, "tag": tag, "outputs": {}}
        for name in outputs:
            p = wd / name
            if p.exists():
                result["outputs"][name] = p.read_text()
        if not ok:
            result["stderr"] = err
            result["stdout"] = out
        return result


def main() -> None:
    base = CIF.stem

    cases = [
        ("sa", ["-ha", "-sa", "1.86", "1.86", "2000"], [f"{base}.sa"]),
        ("vol", ["-ha", "-vol", "1.86", "1.86", "50000"], [f"{base}.vol"]),
        ("volpo", ["-ha", "-volpo", "1.86", "1.86", "50000"], [f"{base}.volpo"]),
        ("res", ["-res"], [f"{base}.res"]),
        ("chan", ["-chan", "1.86"], [f"{base}.chan"]),
    ]

    for tag, args, outs in cases:
        print(f"\n=== {tag}: {' '.join(args)} ===")
        r = run(args, outs, tag)
        if not r["ok"]:
            print(f"  FAILED exit={r['code']}\n  stderr={r.get('stderr','')[:400]}")
            continue
        for name, text in r["outputs"].items():
            print(f"  --- {name} ({len(text)} bytes) ---")
            print("  " + text.replace("\n", "\n  ")[:800])
            try:
                if name.endswith(".sa"):
                    parsed = P.parse_sa_from_text(text)
                elif name.endswith(".vol"):
                    parsed = P.parse_vol_from_text(text)
                elif name.endswith(".volpo"):
                    parsed = P.parse_volpo_from_text(text)
                elif name.endswith(".res"):
                    parsed = P.parse_res_from_text(text)
                elif name.endswith(".chan"):
                    parsed = P.parse_chan_from_text(text)
                else:
                    parsed = {"_": "no parser"}
                print(f"  PARSED: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
            except Exception as exc:  # noqa: BLE001
                print(f"  PARSE ERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
