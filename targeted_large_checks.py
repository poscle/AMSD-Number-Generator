"""Build and verify perfect AMSD sequences for a fixed list of large N.

All of the construction lives in amsd.py; this script only runs the
targeted checks reported in Section 10 of the paper.
"""
from __future__ import annotations

from amsd import build, decomposition, verify


def run_targeted_checks() -> None:
    targets = [
        5_000,
        9_999,
        10_000,
        12_345,
        20_000,
        50_000,
        99_991,
        100_000,
    ]

    print("Targeted large checks")
    print("cycle = AMSD, start = 2")
    print()
    print(f"{'N':>10} {'moves':>10} {'parent':>10} {'c':>4} {'verified':>10}")
    print("-" * 50)

    for N in targets:
        P, c = decomposition(N)
        chain = build(N)
        ok, msg = verify(chain, N)
        print(f"{N:>10,} {len(chain):>10,} {P:>10,} {c:>4} {str(ok):>10}")
        if not ok:
            raise AssertionError(f"N={N}: {msg}")


if __name__ == "__main__":
    run_targeted_checks()
