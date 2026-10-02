"""Perfect AMSD sequences: make every number from 1 to N in N-1 moves.

Start with 2. Each move combines two numbers already made, using the
operations in the fixed order +, x, -, / (A, M, S, D), and a division must
be exact. For every N >= 9 this program writes down a sequence of exactly
N-1 moves that makes all of 1..N, following the construction in

    T. Tjugiarto and S. Lesmana, "Making Every Number from 1 to N
    Under a Fixed Cycle of +, x, -, /".

    N = 9..33     explicit sequences (Section 3 and Appendix D)
    N = 3P + c    base cases (Appendix A), tripling (Section 6),
                  reduction of q (Section 7) and patches (Appendix B),
                  combined as in Section 11 ("Computing the Sequence").

For 2 <= N <= 8 no perfect sequence exists (exhaustive search, Section 9).

Usage:
    python amsd.py 100            print a perfect sequence for N = 100
    python amsd.py                ask for N
    python amsd.py 100000 --quiet build and verify only
    python amsd.py 500 --explain  show how N reduces to a base case
    python amsd.py 500 --format csv --out seq.csv
    python amsd.py --check 9 5000 verify every N in a range
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys

from dataclasses import dataclass
from typing import List, Tuple, Dict

CYCLE = ("A", "M", "S", "D")
OFFSET_TABLE = {
    0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11,
    6: 0, 7: 1, 8: 2, 9: 15, 10: 4, 11: 5,
}

@dataclass(frozen=True)
class Step:
    op: str
    left: int
    right: int
    result: int


def calc(op: str, a: int, b: int) -> int:
    if op == "A":
        return a + b
    if op == "M":
        return a * b
    if op == "S":
        return a - b
    if op == "D":
        if b == 0 or a % b != 0:
            raise ValueError(f"Invalid integer division: {a}/{b}")
        return a // b
    raise ValueError(op)


def make_step(op: str, a: int, b: int) -> Step:
    return Step(op, a, b, calc(op, a, b))


def verify(steps: List[Step], N: int, start: int = 2, cycle=CYCLE) -> Tuple[bool, str]:
    """Independent checker for a claimed perfect chain."""
    available = {start}

    for i, step in enumerate(steps):
        required = cycle[i % len(cycle)]
        if step.op != required:
            return False, f"step {i+1}: expected {required}, got {step.op}"
        if step.left not in available:
            return False, f"step {i+1}: left operand {step.left} unavailable"
        if step.right not in available:
            return False, f"step {i+1}: right operand {step.right} unavailable"
        try:
            actual = calc(step.op, step.left, step.right)
        except ValueError as e:
            return False, f"step {i+1}: {e}"
        if actual != step.result:
            return False, f"step {i+1}: recorded {step.result}, actual {actual}"
        if not (1 <= step.result <= N):
            return False, f"step {i+1}: result {step.result} outside [1,{N}]"
        if step.result in available:
            return False, f"step {i+1}: duplicate result {step.result}"
        available.add(step.result)

    if len(steps) != N - 1:
        return False, f"length {len(steps)} != N-1={N-1}"
    target = set(range(1, N + 1))
    if available != target:
        missing = sorted(target - available)[:10]
        extra = sorted(available - target)[:10]
        return False, f"coverage mismatch; missing={missing}, extra={extra}"
    return True, "OK"


# ---------------------------------------------------------------------------
# Five finite AMSD base chains.  Every one starts at 2.
# ---------------------------------------------------------------------------

def base_10() -> List[Step]:
    return [
        make_step("A",2,2),       # 4
        make_step("M",2,4),       # 8
        make_step("S",8,2),       # 6
        make_step("D",8,8),       # 1
        make_step("A",1,4),       # 5
        make_step("M",2,5),       # 10
        make_step("S",8,1),       # 7
        make_step("D",6,2),       # 3
        make_step("A",1,8),       # 9
    ]


def base_14() -> List[Step]:
    return [
        make_step("A",2,2),       # 4
        make_step("M",2,4),       # 8
        make_step("S",8,2),       # 6
        make_step("D",8,8),       # 1
        make_step("A",1,2),       # 3
        make_step("M",2,6),       # 12
        make_step("S",12,2),      # 10
        make_step("D",10,2),      # 5
        make_step("A",2,12),      # 14
        make_step("M",3,3),       # 9
        make_step("S",12,1),      # 11
        make_step("D",14,2),      # 7
        make_step("A",1,12),      # 13
    ]


def base_18() -> List[Step]:
    return [
        make_step("A",2,2), make_step("M",2,4), make_step("S",8,2), make_step("D",8,8),
        make_step("A",1,2), make_step("M",2,6), make_step("S",12,2), make_step("D",10,2),
        make_step("A",1,10), make_step("M",2,8), make_step("S",16,2), make_step("D",14,2),
        make_step("A",1,12), make_step("M",3,6), make_step("S",16,1), make_step("D",18,2),
        make_step("A",1,16),
    ]


def base_22() -> List[Step]:
    return [
        make_step("A",2,2), make_step("M",2,4), make_step("S",8,2), make_step("D",8,8),
        make_step("A",1,2), make_step("M",2,6), make_step("S",12,2), make_step("D",10,2),
        make_step("A",1,12), make_step("M",2,8), make_step("S",16,2), make_step("D",14,2),
        make_step("A",1,14), make_step("M",2,10), make_step("S",20,2), make_step("D",18,2),
        make_step("A",2,20), make_step("M",3,7), make_step("S",18,1), make_step("D",22,2),
        make_step("A",1,18),
    ]


def base_26() -> List[Step]:
    return [
        make_step("A",2,2), make_step("M",2,4), make_step("S",8,2), make_step("D",8,8),
        make_step("A",1,2), make_step("M",2,6), make_step("S",12,2), make_step("D",10,2),
        make_step("A",2,12), make_step("M",2,8), make_step("S",16,1), make_step("D",14,2),
        make_step("A",1,16), make_step("M",2,10), make_step("S",20,2), make_step("D",18,2),
        make_step("A",1,18), make_step("M",2,12), make_step("S",24,2), make_step("D",22,2),
        make_step("A",2,24), make_step("M",3,7), make_step("S",24,1), make_step("D",26,2),
        make_step("A",1,24),
    ]

BASES: Dict[int, callable] = {
    10: base_10,
    14: base_14,
    18: base_18,
    22: base_22,
    26: base_26,
}


# ---------------------------------------------------------------------------
# P -> 3P extension.
# ---------------------------------------------------------------------------
def extend_3p(parent: List[Step], P: int) -> List[Step]:
    steps = list(parent)
    H = 3 * P // 2

    # Boundary MSDA block.
    steps.append(make_step("M", 3, P))            # 3P
    steps.append(make_step("S", 3*P, 1))          # 3P-1
    steps.append(make_step("D", 3*P, 2))          # H
    steps.append(make_step("A", H, 1))            # H+1

    # Regular MSDA blocks.
    for j in range(1, P // 2):
        C = 3 * P - 3 * j
        steps.append(make_step("M", 3, P - j))    # C
        steps.append(make_step("S", C, 1))        # C-1

        if j == 1:
            D_out = H - 2
        elif j == 2:
            D_out = H - 1
        else:
            D_out = H - j
        numerator = 2 * D_out
        steps.append(make_step("D", numerator, 2))
        steps.append(make_step("A", C, 1))        # C+1

    return steps


# ---------------------------------------------------------------------------
# Fixed endpoint patches. Each starts from a perfect parent P = 2 (mod 4).
# We construct the full P->3P chain, cut one/two final MSDA blocks, and append
# a formula-only replacement tail.
# ---------------------------------------------------------------------------
def apply_patch(parent: List[Step], P: int, c: int) -> List[Step]:
    if c == 0:
        return extend_3p(parent, P)

    q = (P - 2) // 4
    H = 3 * P // 2
    T = 3 * P
    L = lambda i: P + i
    Hv = lambda i: H + i
    Tv = lambda i: T + i

    cut_blocks = 2 if c in (1, 15) else 1
    full = extend_3p(parent, P)
    steps = full[:-4 * cut_blocks]

    def add(op, a, b):
        steps.append(make_step(op, a, b))

    if c == 1:
        if P < 14:
            raise ValueError("c=1 requires P>=14")
        add("M", 3, 2*q+2)             # H3
        add("S", Hv(3), 1)             # H2
        add("D", 8*q+6, 2)             # L1
        add("A", Hv(3), 1)             # H4
        add("M", 2, 3*q+4)             # H5
        add("S", Hv(8), 2)             # H6
        add("D", 8*q+8, 2)             # L2
        add("A", T, 1)                 # T1
        add("M", 2, 3*q+5)             # H7

    elif c == 2:
        add("M", 3, 2*q+2)             # H3
        add("S", Hv(3), 1)             # H2
        add("D", 8*q+6, 2)             # L1
        add("A", Hv(3), 1)             # H4
        add("M", 4, 3*q+2)             # T2
        add("S", Tv(2), 1)             # T1

    elif c == 4:
        add("M", 3, 2*q+2)             # H3
        add("S", Hv(5), 1)             # H4
        add("D", 8*q+6, 2)             # L1
        add("A", T, 4)                 # T4
        add("M", 4, 3*q+2)             # T2
        add("S", Tv(2), 1)             # T1
        add("D", Tv(4), 2)             # H2
        add("A", Tv(2), 1)             # T3

    elif c == 5:
        add("M", 3, 2*q+2)             # H3
        add("S", Hv(5), 1)             # H4
        add("D", 8*q+6, 2)             # L1
        add("A", T, 4)                 # T4
        add("M", 4, 3*q+2)             # T2
        add("S", Tv(2), 1)             # T1
        add("D", Tv(4), 2)             # H2
        add("A", Tv(4), 1)             # T5
        add("M", 3, L(1))              # T3

    elif c == 6:
        add("M", 3, 2*q+2)             # H3
        add("S", Hv(5), 1)             # H4
        add("D", 8*q+6, 2)             # L1
        add("A", T, 1)                 # T1
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 2)             # T4
        add("D", Tv(4), 2)             # H2
        add("A", Tv(1), 1)             # T2
        add("M", 3, L(1))              # T3
        add("S", Tv(6), 1)             # T5

    elif c == 7:
        add("M", 4, 3*q+2)             # T2
        add("S", Hv(5), 1)             # H4
        add("D", 8*q+6, 2)             # L1
        add("A", T, 1)                 # T1
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 2)             # T4
        add("D", Tv(4), 2)             # H2
        add("A", Tv(6), 1)             # T7
        add("M", 3, L(1))              # T3
        add("S", Tv(6), 1)             # T5
        add("D", Tv(6), 2)             # H3

    elif c == 8:
        add("M", 4, 3*q+2)             # T2
        add("S", Hv(5), 3)             # H2
        add("D", 8*q+6, 2)             # L1
        add("A", T, 1)                 # T1
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 3)             # T3
        add("D", Tv(6), 2)             # H3
        add("A", Tv(6), 2)             # T8
        add("M", 2, Hv(2))             # T4
        add("S", Tv(6), 1)             # T5
        add("D", Tv(8), 2)             # H4
        add("A", Tv(6), 1)             # T7

    elif c == 9:
        add("M", 4, 3*q+2)             # T2
        add("S", Hv(5), 3)             # H2
        add("D", 8*q+6, 2)             # L1
        add("A", T, 1)                 # T1
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 3)             # T3
        add("D", Tv(6), 2)             # H3
        add("A", Tv(3), 2)             # T5
        add("M", 3, P+3)               # T9
        add("S", Tv(9), 1)             # T8
        add("D", Tv(8), 2)             # H4
        add("A", Tv(6), 1)             # T7
        add("M", 2, Hv(2))             # T4

    elif c == 10:
        add("M", 4, 3*q+2)             # T2
        add("S", Hv(5), 3)             # H2
        add("D", 8*q+6, 2)             # L1
        add("A", T, 1)                 # T1
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 3)             # T3
        add("D", Tv(6), 2)             # H3
        add("A", Tv(3), 1)             # T4
        add("M", 3, P+3)               # T9
        add("S", Tv(9), 1)             # T8
        add("D", Tv(8), 2)             # H4
        add("A", Tv(4), 1)             # T5
        add("M", 4, 3*q+4)             # T10
        add("S", Tv(8), 1)             # T7

    elif c == 11:
        add("M", 4, 3*q+2)             # T2
        add("S", Tv(2), 1)             # T1
        add("D", 8*q+6, 2)             # L1
        add("A", Tv(2), 1)             # T3
        add("M", 6, 2*q+2)             # T6
        add("S", Tv(6), 2)             # T4
        add("D", Tv(4), 2)             # H2
        add("A", Tv(4), 1)             # T5
        add("M", 3, P+3)               # T9
        add("S", Tv(9), 2)             # T7
        add("D", Tv(6), 2)             # H3
        add("A", Tv(9), 2)             # T11
        add("M", 4, 3*q+4)             # T10
        add("S", Tv(9), 1)             # T8
        add("D", Tv(8), 2)             # H4

    elif c == 15:
        add("M", 3, P+5)               # T15
        add("S", Tv(15), 1)            # T14
        add("D", Tv(14), 2)            # H7
        add("A", Hv(1), 3)             # H4
        add("M", 6, 2*q+3)             # T12
        add("S", Tv(12), 2)            # T10
        add("D", Tv(12), 2)            # H6
        add("A", Hv(1), 1)             # H2
        add("M", 3, P+3)               # T9
        add("S", Tv(9), 3)             # T6
        add("D", Tv(10), 2)            # H5
        add("A", Tv(12), 1)            # T13
        add("M", 2, Hv(4))             # T8
        add("S", Tv(12), 1)            # T11
        add("D", Tv(6), 2)             # H3
        add("A", Tv(6), 1)             # T7
        add("M", 2, Hv(2))             # T4
        add("S", Tv(6), 1)             # T5
        add("D", 8*q+8, 2)             # L2
        add("A", T, 3)                 # T3
        add("M", 4, 3*q+2)             # T2
        add("S", Tv(2), 1)             # T1
        add("D", 8*q+6, 2)             # L1

    else:
        raise ValueError(f"Unsupported patch c={c}")

    return steps


# Convenience wrappers for the three recursive class-2 maps.
def extend_3p_plus_4(parent: List[Step], P: int) -> List[Step]:
    return apply_patch(parent, P, 4)


def extend_3p_plus_8(parent: List[Step], P: int) -> List[Step]:
    return apply_patch(parent, P, 8)


# ---------------------------------------------------------------------------
# Recursive class P = 2 (mod 4) constructor.
# ---------------------------------------------------------------------------
def build_class2(P: int) -> List[Step]:
    if P in BASES:
        return BASES[P]()
    if P < 10 or P % 4 != 2:
        raise ValueError(f"P must be >=10 and 2 mod 4; got {P}")

    q = (P - 2) // 4
    rmod = q % 3

    if rmod == 1:
        r = (q - 1) // 3
        P0 = 4*r + 2
        return extend_3p(build_class2(P0), P0)
    elif rmod == 2:
        r = (q - 2) // 3
        P0 = 4*r + 2
        return extend_3p_plus_4(build_class2(P0), P0)
    else:
        # q mod 3 == 0. q=3 or 6 are already finite bases (P=14,26).
        r = (q - 3) // 3
        P0 = 4*r + 2
        return extend_3p_plus_8(build_class2(P0), P0)


# ---------------------------------------------------------------------------
# Small cases 9 <= N <= 33 that the construction does not reach
# (N = 9 from Section 3, the rest from Appendix D). Each entry is (op, a, b).
# ---------------------------------------------------------------------------
SMALL_CASES: Dict[int, List[Tuple[str, int, int]]] = {
    9: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",6,2),
        ("A",2,3), ("M",3,3), ("S",9,2), ("D",2,2),
    ],
    11: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",6,2),
        ("A",4,3), ("M",3,3), ("S",8,3), ("D",2,2),
        ("A",2,9), ("M",2,5),
    ],
    12: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",2,2),
        ("A",2,8), ("M",2,6), ("S",4,1), ("D",10,2),
        ("A",2,5), ("M",3,3), ("S",12,1),
    ],
    13: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",6,2),
        ("A",8,3), ("M",2,6), ("S",12,2), ("D",10,2),
        ("A",2,11), ("M",3,3), ("S",11,4), ("D",2,2),
    ],
    15: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",2,2),
        ("A",8,6), ("M",2,6), ("S",14,1), ("D",14,2),
        ("A",2,1), ("M",3,3), ("S",14,4), ("D",10,2),
        ("A",2,9), ("M",3,5),
    ],
    16: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",14,2),
        ("A",2,4), ("M",2,4), ("S",7,2), ("D",2,2),
        ("A",7,6), ("M",2,6), ("S",16,7), ("D",6,2),
        ("A",2,9), ("M",5,3), ("S",16,6),
    ],
    17: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",14,2),
        ("A",4,7), ("M",2,4), ("S",14,11), ("D",2,2),
        ("A",16,1), ("M",3,3), ("S",16,1), ("D",15,3),
        ("A",4,8), ("M",2,5), ("S",16,3), ("D",12,2),
    ],
    19: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",2,2),
        ("A",2,1), ("M",3,3), ("S",16,9), ("D",16,2),
        ("A",16,1), ("M",4,3), ("S",14,3), ("D",12,2),
        ("A",2,17), ("M",2,9), ("S",16,1), ("D",15,3),
        ("A",2,11), ("M",2,5),
    ],
    20: [
        ("A",2,2), ("M",4,4), ("S",16,4), ("D",2,2),
        ("A",2,1), ("M",3,3), ("S",12,1), ("D",16,2),
        ("A",2,11), ("M",2,3), ("S",16,2), ("D",14,2),
        ("A",4,16), ("M",2,9), ("S",20,3), ("D",20,4),
        ("A",2,17), ("M",2,5), ("S",16,1),
    ],
    21: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",14,2),
        ("A",2,4), ("M",2,4), ("S",7,6), ("D",6,2),
        ("A",14,1), ("M",6,3), ("S",16,4), ("D",15,3),
        ("A",7,6), ("M",4,5), ("S",18,1), ("D",18,2),
        ("A",2,17), ("M",7,3), ("S",16,5), ("D",20,2),
    ],
    23: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",2,2),
        ("A",2,1), ("M",4,3), ("S",16,1), ("D",14,2),
        ("A",2,3), ("M",3,7), ("S",16,5), ("D",16,2),
        ("A",14,8), ("M",3,3), ("S",16,3), ("D",12,2),
        ("A",2,15), ("M",4,5), ("S",21,2), ("D",20,2),
        ("A",2,21), ("M",2,9),
    ],
    24: [
        ("A",2,2), ("M",4,4), ("S",16,4), ("D",12,2),
        ("A",4,6), ("M",2,4), ("S",16,2), ("D",2,2),
        ("A",4,1), ("M",2,10), ("S",16,1), ("D",12,4),
        ("A",4,5), ("M",2,9), ("S",20,3), ("D",14,2),
        ("A",2,20), ("M",3,7), ("S",20,1), ("D",22,2),
        ("A",2,21), ("M",2,12), ("S",16,3),
    ],
    25: [
        ("A",2,2), ("M",4,4), ("S",16,4), ("D",12,4),
        ("A",2,4), ("M",3,3), ("S",9,4), ("D",16,2),
        ("A",16,8), ("M",5,5), ("S",24,2), ("D",2,2),
        ("A",4,16), ("M",3,5), ("S",16,3), ("D",20,2),
        ("A",3,20), ("M",2,9), ("S",16,2), ("D",14,2),
        ("A",4,15), ("M",3,7), ("S",24,7), ("D",22,2),
    ],
    27: [
        ("A",2,2), ("M",2,4), ("S",8,2), ("D",2,2),
        ("A",2,8), ("M",2,6), ("S",12,1), ("D",10,2),
        ("A",8,11), ("M",2,11), ("S",19,1), ("D",6,2),
        ("A",4,12), ("M",5,3), ("S",19,2), ("D",18,2),
        ("A",2,19), ("M",2,10), ("S",19,5), ("D",21,3),
        ("A",8,19), ("M",2,12), ("S",27,1), ("D",26,2),
        ("A",2,21), ("M",5,5),
    ],
    28: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",14,2),
        ("A",4,4), ("M",2,14), ("S",14,4), ("D",2,2),
        ("A",14,1), ("M",2,10), ("S",28,10), ("D",18,2),
        ("A",2,10), ("M",2,12), ("S",28,9), ("D",12,4),
        ("A",2,24), ("M",9,3), ("S",24,2), ("D",26,2),
        ("A",2,3), ("M",5,5), ("S",20,3), ("D",18,3),
        ("A",4,19), ("M",7,3), ("S",16,5),
    ],
    29: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",16,2),
        ("A",2,8), ("M",2,14), ("S",28,4), ("D",10,2),
        ("A",10,5), ("M",5,5), ("S",24,5), ("D",24,8),
        ("A",2,16), ("M",2,3), ("S",25,8), ("D",24,2),
        ("A",8,5), ("M",2,13), ("S",28,6), ("D",22,2),
        ("A",4,19), ("M",3,3), ("S",28,8), ("D",2,2),
        ("A",4,25), ("M",3,9), ("S",24,3), ("D",14,2),
    ],
    31: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",16,2),
        ("A",14,8), ("M",2,14), ("S",16,4), ("D",12,4),
        ("A",2,3), ("M",3,3), ("S",16,3), ("D",14,2),
        ("A",2,16), ("M",3,7), ("S",28,3), ("D",22,2),
        ("A",4,13), ("M",2,12), ("S",28,5), ("D",12,2),
        ("A",2,24), ("M",5,6), ("S",22,3), ("D",30,3),
        ("A",14,17), ("M",3,9), ("S",22,7), ("D",2,2),
        ("A",2,27), ("M",2,10),
    ],
    33: [
        ("A",2,2), ("M",4,4), ("S",16,2), ("D",14,2),
        ("A",4,7), ("M",2,16), ("S",16,7), ("D",2,2),
        ("A",32,1), ("M",2,14), ("S",32,9), ("D",16,2),
        ("A",2,11), ("M",2,9), ("S",33,4), ("D",33,11),
        ("A",4,13), ("M",2,3), ("S",32,8), ("D",24,2),
        ("A",2,17), ("M",2,13), ("S",32,2), ("D",30,6),
        ("A",2,29), ("M",5,5), ("S",33,11), ("D",30,3),
        ("A",2,19), ("M",9,3), ("S",32,12), ("D",30,2),
    ],
}


MIN_N = 9


def _from_table(moves: List[Tuple[str, int, int]]) -> List[Step]:
    return [make_step(op, a, b) for op, a, b in moves]


def decomposition(N: int) -> Tuple[int, int]:
    """Return the top-level (P, c) with N = 3P + c (table in Section 8)."""
    c = OFFSET_TABLE[N % 12]
    return (N - c) // 3, c


def _construction_applies(N: int) -> bool:
    """True when N = 3P + c with P >= 10 (P >= 14 for c = 1), as in Section 8.1."""
    P, c = decomposition(N)
    return P >= 10 and P % 4 == 2 and (c != 1 or P >= 14)


def build(N: int) -> List[Step]:
    """A perfect sequence for any N >= 9 (Theorem 2)."""
    if N < MIN_N:
        raise ValueError(
            f"No perfect sequence exists for N = {N}: the bound N >= 9 is sharp "
            "(exhaustive search for 2 <= N <= 8, Section 9)."
        )
    if N in SMALL_CASES:
        return _from_table(SMALL_CASES[N])
    if N in BASES:
        return BASES[N]()
    if _construction_applies(N):
        P, c = decomposition(N)
        return apply_patch(build_class2(P), P, c)
    raise AssertionError(f"N = {N} is not covered; this should not happen")


def reduction_path(N: int) -> List[Tuple[int, str, int]]:
    """Steps from a base case up to N, as (parent, step, child).

    step is "x3" for P -> 3P and "+c" for P -> 3P + c, matching the
    example at the end of Section 8. Empty when N is a table entry.
    """
    if N in SMALL_CASES or N in BASES or N < MIN_N:
        return []
    path: List[Tuple[int, str, int]] = []
    P, c = decomposition(N)
    path.append((P, "x3" if c == 0 else f"+{c}", N))
    while P not in BASES:
        q = (P - 2) // 4
        k = q % 3 or 3
        P0 = 4 * ((q - k) // 3) + 2
        extra = 4 * (k - 1)
        path.append((P0, "x3" if extra == 0 else f"+{extra}", P))
        P = P0
    return list(reversed(path))


# ---------------------------------------------------------------------------
# Output.
# ---------------------------------------------------------------------------
SYMBOL = {"A": "+", "M": "x", "S": "-", "D": "/"}


def format_table(steps: List[Step]) -> str:
    width = len(str(len(steps)))
    lines = [f"{'move':>{max(width, 4)}}  op  calculation"]
    for i, s in enumerate(steps, 1):
        lines.append(f"{i:>{max(width, 4)}}  {s.op}   {s.left} {SYMBOL[s.op]} {s.right} = {s.result}")
    return "\n".join(lines)


def format_csv(steps: List[Step]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["move", "op", "left", "right", "result"])
    for i, s in enumerate(steps, 1):
        w.writerow([i, s.op, s.left, s.right, s.result])
    return buf.getvalue()


def format_json(steps: List[Step], N: int) -> str:
    return json.dumps({
        "N": N,
        "start": 2,
        "cycle": "AMSD",
        "moves": [{"move": i, "op": s.op, "left": s.left, "right": s.right, "result": s.result}
                  for i, s in enumerate(steps, 1)],
    }, indent=1)


def explain(N: int) -> str:
    if N in SMALL_CASES:
        return f"N = {N} is a small case, taken from the table (Section 3 / Appendix D)."
    if N in BASES:
        return f"N = {N} is a base case (Appendix A)."
    path = reduction_path(N)
    chain = str(path[0][0]) + "".join(f" --{step}--> {child}" for _, step, child in path)
    P, c = decomposition(N)
    return (f"N = {N}: N mod 12 = {N % 12}, so c = {c} and P = {P}.\n"
            f"Built from base case {path[0][0]}: {chain}\n"
            "(x3 means P -> 3P; +c means P -> 3P + c using the patch for c.)")


# ---------------------------------------------------------------------------
# Command line.
# ---------------------------------------------------------------------------
def _read_N(text: str) -> int:
    try:
        return int(text.replace(",", "").replace("_", "").strip())
    except ValueError:
        raise SystemExit(f"Not a whole number: {text!r}")


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Make every number from 1 to N in N-1 moves under the fixed cycle +, x, -, /.")
    ap.add_argument("N", nargs="?", help="the target N (asked for if omitted)")
    ap.add_argument("--format", choices=["table", "csv", "json"], default="table")
    ap.add_argument("--out", help="write the sequence to this file instead of the screen")
    ap.add_argument("--quiet", action="store_true", help="build and verify only, do not print the moves")
    ap.add_argument("--explain", action="store_true", help="show how N reduces to a base case")
    ap.add_argument("--check", nargs=2, type=int, metavar=("LO", "HI"),
                    help="build and verify every N with LO <= N <= HI")
    args = ap.parse_args(argv)

    if args.check:
        lo, hi = args.check
        lo = max(lo, MIN_N)
        for N in range(lo, hi + 1):
            ok, msg = verify(build(N), N)
            if not ok:
                print(f"N = {N}: FAILED, {msg}")
                return 1
        print(f"All N from {lo} to {hi} verified.")
        return 0

    N = _read_N(args.N if args.N is not None else input("N = "))
    if N < MIN_N:
        print(f"No perfect sequence exists for N = {N}; the construction needs N >= 9.")
        return 1

    steps = build(N)
    ok, msg = verify(steps, N)
    if not ok:
        print(f"Internal error, the sequence failed verification: {msg}")
        return 2

    if args.explain:
        print(explain(N))
        print()

    if not args.quiet:
        text = {"table": lambda: format_table(steps),
                "csv": lambda: format_csv(steps),
                "json": lambda: format_json(steps, N)}[args.format]()
        if args.out:
            with open(args.out, "w") as f:
                f.write(text if text.endswith("\n") else text + "\n")
            print(f"Wrote {len(steps)} moves to {args.out}.")
        else:
            print(text)

    print(f"Verified: {len(steps)} moves make every number from 1 to {N}.", file=sys.stderr if not args.quiet and not args.out else sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
