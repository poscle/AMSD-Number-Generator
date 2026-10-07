## Code & Verification
- **Algorithms & Proof Design:** The mathematical formulas, modulo tracking logic, and constructive sequence steps were conceived, derived, and proved entirely by the authors.
- **Code Implementation:** Python scripts for verifying sequences across values of $N$ ($N \le 100,000$) were generated and refactored with assistance from Claude (Anthropic). All script outputs and verification logic were independently tested and audited by the authors.

# AMSD Number Generator

Start with the number 2. At each move, combine two numbers you already have, but the operations must follow the fixed order `+, ×, −, ÷` (A, M, S, D), and a division must be exact. How few moves does it take to make every number from 1 to N?

At least N − 1, since each move makes one number. This program writes down a sequence of exactly N − 1 moves for any N ≥ 9, following the construction in

>  S. Lesmana and T. Tjugiarto, *Making Every Number from 1 to N Under a Fixed Cycle of +, ×, −, ÷*.

For 2 ≤ N ≤ 8 no such sequence exists.

## Usage

Python 3.8 or later, no dependencies.

```
python amsd.py 100                      # print a perfect sequence for N = 100
python amsd.py                          # ask for N
python amsd.py 500 --explain            # show how N reduces to a base case
python amsd.py 100000 --quiet           # build and verify only
python amsd.py 500 --format csv --out seq.csv
python amsd.py 500 --format json
python amsd.py --check 9 5000           # verify every N in a range
python targeted_large_checks.py         # the large-N checks reported in the paper
```

Every sequence is checked move by move before it is printed: the operation follows the cycle, both operands were already made, divisions are exact, and every result is new and at most N.

## How it works

The code follows Section 11 of the paper.

1. For 9 ≤ N ≤ 33 not reached by the construction, the sequence is taken from a table (Section 3 and Appendix D).
2. Otherwise, write N = 3P + c, with c chosen from N mod 12 so that P ≡ 2 (mod 4).
3. Reduce P to one of the base cases 10, 14, 18, 22, 26 by repeatedly writing P = 3P′, 3P′ + 4 or 3P′ + 8.
4. Start from the base sequence (Appendix A), apply the tripling step P → 3P (Section 6) or a patch P → 3P + c (Appendix B) at each level, and finish with the patch for c.

For example, `python amsd.py 100000 --explain` prints

```
14 --x3--> 42 --+8--> 134 --+8--> 410 --+4--> 1234 --x3--> 3702 --+4--> 11110 --x3--> 33330 --+10--> 100000
```
