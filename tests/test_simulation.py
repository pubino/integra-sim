import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

from web.simulation import integrate

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    [-3, 3, 10, 1, 2, 0],
    [-2.4, 3.1, 17, -0.8, 1.7, 3],
    [2, 0.5, 50, 2.1, 3, -2],
    [-1.5, -1.5, 1, -0.3, -1.4, -1],
    [1, 2, 1000, 0.5, -2, 2],
    [-2, 2, 5, 0, 1, 0],
]


class IntegrationTest(unittest.TestCase):
    def test_matches_java_samples_and_both_approximations(self) -> None:
        with tempfile.TemporaryDirectory() as classes:
            subprocess.run(
                [
                    "javac",
                    "--release",
                    "25",
                    "-d",
                    classes,
                    *sorted((ROOT / "myutil").glob("*.java")),
                    ROOT / "integra/Integra.java",
                    ROOT / "tests/IntegrationReference.java",
                ],
                check=True,
                timeout=30,
            )
            output = subprocess.check_output(
                [
                    "java",
                    "-Djava.awt.headless=true",
                    "-cp",
                    classes,
                    "integra.IntegrationReference",
                ],
                timeout=30,
                text=True,
            )
        results = [integrate(json.dumps(case)) for case in CASES]
        rules_count = panel_count = curve_count = 0
        for line in output.splitlines():
            kind, index, *data = line.split(",")
            midpoint, trapezoid, curve, edges, heights = results[int(index)]
            if kind == "RULES":
                self.assert_values((midpoint, trapezoid), data)
                rules_count += 1
            if kind == "INTERVAL":
                panel = int(data[0])
                self.assert_values((*edges[panel], heights[panel]), data[1:])
                panel_count += 1
            if kind == "CURVE":
                self.assert_values(curve[int(data[0])], data[1:])
                curve_count += 1
        self.assertEqual((rules_count, panel_count, curve_count), (6, 1083, 6006))

    def assert_values(self, actual: tuple[float, ...], expected: list[str]) -> None:
        for value, reference in zip(actual, expected, strict=True):
            self.assertTrue(
                math.isclose(value, float(reference), rel_tol=3e-13, abs_tol=3e-13),
                f"got {value} from Python, expected {reference} from Java",
            )

    def test_validation(self) -> None:
        for invalid in (
            "[-1,1,10,1,0,0]",
            "[-1,1,10,1,2,-1]",
            "[-1,1,0,1,2,0]",
            "[-1,1,1.5,1,2,0]",
            "[-1,1,10,1,2,0.5]",
            "[1e308,1e309,10,1,2,0]",
            "[10,20,10,1,-0.001,10]",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                integrate(invalid)
