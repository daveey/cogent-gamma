"""PCO LLM Experiment: actor learns to solve programming puzzles.

Requires ANTHROPIC_API_KEY env var for LLM tests.
Results written to .tests/pco_experiment/
"""

import asyncio
import json
import os
import textwrap
from pathlib import Path
from typing import Any

import pytest

from coglet import Coglet, CogletConfig, CogletRuntime, enact, listen
from coglet.handle import Command
from coglet.pco.constraint import ConstraintCoglet
from coglet.pco.learner import LearnerCoglet
from coglet.pco.loss import LossCoglet
from coglet.pco.optimizer import ProximalCogletOptimizer

RESULTS_DIR = Path(".tests/pco_experiment")

PUZZLES = [
    # ── Easy ───────────────────────────────────────────
    {
        "name": "fizzbuzz",
        "description": "Given int n, return 'FizzBuzz' if divisible by 15, 'Fizz' if by 3, 'Buzz' if by 5, else str(n).",
        "signature": "def fizzbuzz(n: int) -> str:",
        "tests": [(1, "1"), (3, "Fizz"), (5, "Buzz"), (15, "FizzBuzz"), (30, "FizzBuzz"), (7, "7")],
    },
    {
        "name": "is_palindrome",
        "description": "Return True if the string is a palindrome (case-insensitive, ignoring non-alphanumeric chars).",
        "signature": "def is_palindrome(s: str) -> bool:",
        "tests": [("racecar", True), ("hello", False), ("A man a plan a canal Panama", True), ("", True), ("ab", False)],
    },
    {
        "name": "reverse_words",
        "description": "Reverse the order of words in a string. 'hello world' → 'world hello'. Strip extra spaces.",
        "signature": "def reverse_words(s: str) -> str:",
        "tests": [("hello world", "world hello"), ("  the sky is blue  ", "blue is sky the"), ("a", "a"), ("", "")],
    },
    {
        "name": "max_of_list",
        "description": "Return the maximum element in a list of integers. Raise ValueError if list is empty.",
        "signature": "def max_of_list(nums: list[int]) -> int:",
        "tests": [([1, 3, 2], 3), ([-1, -5, -2], -1), ([42], 42), ([0, 0, 0], 0)],
    },
    {
        "name": "factorial",
        "description": "Return n! (n factorial). n is a non-negative integer. 0! = 1.",
        "signature": "def factorial(n: int) -> int:",
        "tests": [(0, 1), (1, 1), (5, 120), (10, 3628800)],
    },
    # ── Medium ─────────────────────────────────────────
    {
        "name": "balanced_parens",
        "description": "Return True if the string has balanced parentheses. Only consider '(' and ')'.",
        "signature": "def balanced_parens(s: str) -> bool:",
        "tests": [("(())", True), ("(()", False), (")(", False), ("", True), ("()()", True), ("((()))", True), ("(()))(", False)],
    },
    {
        "name": "roman_to_int",
        "description": "Convert a roman numeral string to integer. Handle subtractive notation (IV=4, IX=9, XL=40, XC=90, CD=400, CM=900).",
        "signature": "def roman_to_int(s: str) -> int:",
        "tests": [("III", 3), ("IV", 4), ("IX", 9), ("XLII", 42), ("MCMXCIV", 1994), ("XIV", 14)],
    },
    {
        "name": "run_length_encode",
        "description": "Run-length encode a string. 'aaabbc' → '3a2b1c'. Single chars get '1' prefix.",
        "signature": "def run_length_encode(s: str) -> str:",
        "tests": [("aaabbc", "3a2b1c"), ("a", "1a"), ("", ""), ("aaa", "3a"), ("abcd", "1a1b1c1d")],
    },
    {
        "name": "flatten_list",
        "description": "Flatten an arbitrarily nested list. [[1,[2]],3] → [1,2,3].",
        "signature": "def flatten_list(lst: list) -> list:",
        "tests": [([[1, [2]], 3], [1, 2, 3]), ([1, 2, 3], [1, 2, 3]), ([[[[1]]]], [1]), ([], [])],
    },
    {
        "name": "nth_prime",
        "description": "Return the nth prime number (1-indexed). nth_prime(1)=2, nth_prime(2)=3, nth_prime(5)=11.",
        "signature": "def nth_prime(n: int) -> int:",
        "tests": [(1, 2), (2, 3), (3, 5), (5, 11), (10, 29), (20, 71)],
    },
    # ── Hard ───────────────────────────────────────────
    {
        "name": "eval_rpn",
        "description": "Evaluate a reverse Polish notation expression. Tokens are ints or '+','-','*','/'. Division truncates toward zero.",
        "signature": "def eval_rpn(tokens: list[str]) -> int:",
        "tests": [
            (["2", "3", "+"], 5),
            (["4", "13", "5", "/", "+"], 6),
            (["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"], 22),
        ],
    },
    {
        "name": "longest_common_subseq",
        "description": "Return the length of the longest common subsequence of two strings.",
        "signature": "def longest_common_subseq(s1: str, s2: str) -> int:",
        "tests": [("abcde", "ace", 3), ("abc", "abc", 3), ("abc", "def", 0), ("", "abc", 0), ("abcba", "abcbcba", 5)],
    },
    {
        "name": "spiral_matrix",
        "description": "Given an NxN matrix (list of lists), return elements in spiral order (clockwise from top-left).",
        "signature": "def spiral_matrix(matrix: list[list[int]]) -> list[int]:",
        "tests": [
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1, 2, 3, 6, 9, 8, 7, 4, 5]),
            ([[1]], [1]),
            ([[1, 2], [3, 4]], [1, 2, 4, 3]),
        ],
    },
    {
        "name": "merge_intervals",
        "description": "Merge overlapping intervals. Input: list of [start, end] pairs sorted by start. Return merged list.",
        "signature": "def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:",
        "tests": [
            ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
            ([[1, 4], [4, 5]], [[1, 5]]),
            ([[1, 2]], [[1, 2]]),
            ([], []),
        ],
    },
    {
        "name": "valid_sudoku",
        "description": "Validate a 9x9 Sudoku board. Board is list of 9 strings, each 9 chars. '.' means empty. Return True if valid (no duplicates in rows, cols, 3x3 boxes). Board doesn't need to be solvable.",
        "signature": "def valid_sudoku(board: list[str]) -> bool:",
        "tests": [
            ([
                "53..7....",
                "6..195...",
                ".98....6.",
                "8...6...3",
                "4..8.3..1",
                "7...2...6",
                ".6....28.",
                "...419..5",
                "....8..79",
            ], True),
            ([
                "83..7....",
                "6..195...",
                ".98....6.",
                "8...6...3",
                "4..8.3..1",
                "7...2...6",
                ".6....28.",
                "...419..5",
                "....8..79",
            ], False),
        ],
    },
]


def run_solution(puzzle: dict, code: str) -> dict:
    """Execute a solution against test cases. Returns result dict."""
    namespace: dict[str, Any] = {}
    try:
        exec(code, namespace)
    except Exception as e:
        return {
            "name": puzzle["name"],
            "passed": False,
            "total_tests": len(puzzle["tests"]),
            "passed_tests": 0,
            "error": f"compile error: {e}",
        }

    fn_name = puzzle["signature"].split("(")[0].replace("def ", "").strip()
    fn = namespace.get(fn_name)
    if fn is None:
        return {
            "name": puzzle["name"],
            "passed": False,
            "total_tests": len(puzzle["tests"]),
            "passed_tests": 0,
            "error": f"function {fn_name} not found in code",
        }

    passed_tests = 0
    first_error = None
    for test_input, expected in puzzle["tests"]:
        try:
            if isinstance(test_input, tuple):
                result = fn(*test_input)
            else:
                result = fn(test_input)
            if result == expected:
                passed_tests += 1
            elif first_error is None:
                first_error = f"input={test_input!r}: got {result!r}, expected {expected!r}"
        except Exception as e:
            if first_error is None:
                first_error = f"input={test_input!r}: raised {type(e).__name__}: {e}"

    return {
        "name": puzzle["name"],
        "passed": passed_tests == len(puzzle["tests"]),
        "total_tests": len(puzzle["tests"]),
        "passed_tests": passed_tests,
        "error": first_error,
    }


# ── Sanity tests (no API key needed) ──────────────────


def test_harness_runs_correct_solution():
    puzzle = PUZZLES[0]  # fizzbuzz
    code = textwrap.dedent("""\
        def fizzbuzz(n):
            if n % 15 == 0: return "FizzBuzz"
            if n % 3 == 0: return "Fizz"
            if n % 5 == 0: return "Buzz"
            return str(n)
    """)
    result = run_solution(puzzle, code)
    assert result["passed"] is True
    assert result["passed_tests"] == len(puzzle["tests"])


def test_harness_catches_bad_solution():
    puzzle = PUZZLES[0]
    result = run_solution(puzzle, "def fizzbuzz(n): return str(n)")
    assert result["passed"] is False
    assert result["error"] is not None
