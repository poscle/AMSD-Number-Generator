from __future__ import annotations

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
# General constructor for N >= 34.
# ---------------------------------------------------------------------------
def build(N: int) -> List[Step]:
    if N < 34:
        raise ValueError("This reproducible large-check script implements N>=34.")
    c = OFFSET_TABLE[N % 12]
    P = (N - c) // 3
    if P % 4 != 2:
        raise AssertionError((N, c, P))
    parent = build_class2(P)
    return apply_patch(parent, P, c)


def decomposition(N: int) -> Tuple[int, int]:
    """Return the top-level (P,c) such that N=3P+c."""
    c = OFFSET_TABLE[N % 12]
    return (N-c)//3, c


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
