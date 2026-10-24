import json
import pathlib
import tempfile
import unittest
from evaluate import calculate, load, load_manifest


def row(dataset, task_id, variant, passed=True, tokens=4000, repetition=1):
    return {
        "dataset": dataset, "task_id": task_id, "repetition": repetition,
        "variant": variant, "pass": passed, "input_tokens": tokens,
        "cached_input_tokens": 0, "output_tokens": 0, "wall_seconds": 3.0,
    }


def manifest(count=100, repetitions=3):
    return {
        "benchmark": "controlled unit fixtures", "expected_repetitions": repetitions,
        "tasks": [{"dataset": "fixture/" + str(i % 4), "task_id": "task-%03d" % i}
                  for i in range(count)]
    }


def build_trials(m, qualifies=70, swat_fails=False):
    rows = []
    for i, t in enumerate(m["tasks"]):
        for rep in range(1, m["expected_repetitions"] + 1):
            rows.append(row(t["dataset"], t["task_id"], "baseline", True, 4000, rep))
            swat_pass = not swat_fails or i < qualifies
            rows.append(row(t["dataset"], t["task_id"], "swat", swat_pass,
                            50 if i < qualifies else 4000, rep))
    return rows


class EvaluationTests(unittest.TestCase):
    def test_100_tasks_70_qualified(self):
        m = manifest()
        report = calculate(build_trials(m, 70), m)
        score = report["forty_x_target"]
        self.assertEqual(report["selected_distinct_tasks"], 100)
        self.assertEqual(report["observed_runs"], 600)
        self.assertEqual(score["required_task_count"], 70)
        self.assertEqual(score["qualified_40x"], 70)
        self.assertEqual(score["fraction"], 0.7)
        self.assertTrue(score["achieved"])

    def test_69_of_100_does_not_pass(self):
        m = manifest()
        self.assertFalse(calculate(build_trials(m, 69), m)["forty_x_target"]["achieved"])

    def test_450_of_642_required(self):
        m = manifest(642)
        report = calculate(build_trials(m, 450), m)
        self.assertEqual(report["forty_x_target"]["required_task_count"], 450)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 450)
        self.assertTrue(report["forty_x_target"]["achieved"])

    def test_single_dataset_89_tasks_can_qualify(self):
        m = manifest(89)
        for t in m["tasks"]:
            t["dataset"] = "terminal-bench-2.0"
        report = calculate(build_trials(m, 89), m)
        self.assertEqual(report["forty_x_target"]["required_task_count"], 63)
        self.assertTrue(report["forty_x_target"]["achieved"])

    def test_zero_results_still_100_denominator(self):
        report = calculate([], manifest())
        self.assertEqual(report["selected_distinct_tasks"], 100)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 0)
        self.assertEqual(report["forty_x_target"]["fraction"], 0)
        self.assertFalse(report["forty_x_target"]["achieved"])

    def test_missing_repeat_is_not_qualified(self):
        m = manifest()
        rows = build_trials(m, 70)
        first = m["tasks"][0]["task_id"]
        rows = [x for x in rows if not (x["task_id"] == first and x["variant"] == "swat"
                                        and x["repetition"] == 3)]
        report = calculate(rows, m)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 69)
        self.assertEqual(report["fully_observed_tasks"], 99)
        self.assertFalse(report["forty_x_target"]["achieved"])

    def test_repeated_trials_not_distinct_tasks(self):
        m = manifest(1)
        report = calculate(build_trials(m, 1), m)
        self.assertEqual(report["selected_distinct_tasks"], 1)
        self.assertEqual(report["observed_runs"], 6)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 1)
        self.assertFalse(report["forty_x_target"]["achieved"])

    def test_failed_baseline_counts_as_miss(self):
        m = manifest()
        rows = build_trials(m, 70)
        for x in rows:
            if x["task_id"] == "task-000" and x["variant"] == "baseline":
                x["pass"] = False
        report = calculate(rows, m)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 69)

    def test_accuracy_regression_prevents_overall_success(self):
        m = manifest()
        report = calculate(build_trials(m, 70, swat_fails=True), m)
        self.assertEqual(report["forty_x_target"]["qualified_40x"], 70)
        self.assertEqual(report["swat_pass_tasks"], 70)
        self.assertFalse(report["forty_x_target"]["achieved"])

    def test_unexpected_task_refused(self):
        with self.assertRaises(ValueError):
            calculate([row("other", "not-selected", "baseline")], manifest())

    def test_duplicate_observation_refused(self):
        m = manifest()
        one = row(m["tasks"][0]["dataset"], m["tasks"][0]["task_id"], "baseline")
        with self.assertRaises(ValueError):
            calculate([one, one], m)

    def test_unlocked_results_never_certified(self):
        m = manifest()
        report = calculate(build_trials(m, 100))
        self.assertFalse(report["locked_manifest"])
        self.assertFalse(report["forty_x_target"]["achieved"])

    def test_load_validates_bad_usage_and_types(self):
        with tempfile.TemporaryDirectory() as temp:
            p = pathlib.Path(temp) / "rows.jsonl"
            item = row("a", "b", "baseline")
            item["cached_input_tokens"] = 9000
            p.write_text(json.dumps(item) + "\n")
            with self.assertRaises(ValueError):
                load(p)
            item["cached_input_tokens"] = 0
            item["pass"] = "yes"
            p.write_text(json.dumps(item) + "\n")
            with self.assertRaises(ValueError):
                load(p)

    def test_locked_real_manifest_metadata(self):
        path = pathlib.Path(__file__).parent / "swebench_pro_v2_pilot100.json"
        if path.exists():
            m = load_manifest(path)
            self.assertEqual(len(m["tasks"]), 100)
            self.assertEqual(m["expected_repetitions"], 3)
            self.assertEqual(len({t["dataset"] for t in m["tasks"]}), 11)


if __name__ == "__main__":
    unittest.main()
