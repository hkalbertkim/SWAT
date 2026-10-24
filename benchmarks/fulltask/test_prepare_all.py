import unittest
from prepare_all import commands


class FullRunCoverageTests(unittest.TestCase):
    def test_four_full_suite_jobs_no_task_filters(self):
        fake = [
            {"suite": "SWE-bench Pro V2", "manifest": "swebench_pro_v2_full642.json",
             "task_root": "/suite/swe/tasks", "task_count": 642, "expected_runs": 3852},
            {"suite": "Terminal-Bench 2.0", "manifest": "terminal_bench2_full89.json",
             "task_root": "/suite/terminal/tasks", "task_count": 89, "expected_runs": 534}
        ]
        jobs = commands(fake)
        self.assertEqual(len(jobs), 4)
        self.assertEqual(sum(s["expected_runs"] for s in fake), 4386)
        self.assertEqual({j["variant"] for j in jobs}, {"baseline", "swat"})
        for job in jobs:
            cmd = job["cmd"]
            self.assertIn("--n-attempts", cmd)
            self.assertEqual(cmd[cmd.index("--n-attempts") + 1], "3")
            self.assertNotIn("--n-tasks", cmd)
            self.assertNotIn("--task", cmd)
            self.assertNotIn("--task-names", cmd)
            self.assertNotIn("--exclude-task-names", cmd)
        self.assertEqual(sum("prompt_template_path=" in " ".join(j["cmd"]) for j in jobs), 2)


if __name__ == "__main__":
    unittest.main()
