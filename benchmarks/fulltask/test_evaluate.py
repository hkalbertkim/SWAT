import unittest
from evaluate import calculate
class Tests(unittest.TestCase):
    def row(self,variant,ok=True,t=100):
        return {"dataset":"a","task_id":"1","variant":variant,"pass":ok,"input_tokens":t,"cached_input_tokens":0,"output_tokens":0,"wall_seconds":1}
    def test_pair(self):
        result=calculate([self.row("baseline",True,200),self.row("swat",True,10)])
        self.assertEqual(result["total_tokens"]["ratio"],20)
        self.assertFalse(result["twenty_x_full_task_tokens_proven"])
    def test_failure(self):
        result=calculate([self.row("baseline",True,200),self.row("swat",False,10)])
        self.assertEqual(result["pass_counts"]["swat"],0)
        self.assertFalse(result["twenty_x_full_task_tokens_proven"])
    def test_forty_x_one_case_not_sufficient(self):
        r=calculate([self.row("baseline",True,4000),self.row("swat",True,50)])
        self.assertEqual(r["forty_x_target"]["fraction"],1.0)
        self.assertFalse(r["forty_x_target"]["achieved"])
    def test_forty_x_failures_count_against_target(self):
        rows=[]
        for i in range(10):
            a=self.row("baseline",True,4000);b=self.row("swat",i<6,50)
            a["task_id"]=str(i);b["task_id"]=str(i)
            rows.extend((a,b))
        r=calculate(rows)
        self.assertEqual(r["forty_x_target"]["fraction"],0.6)
        self.assertFalse(r["forty_x_target"]["achieved"])
    def test_baseline_failures_still_count(self):
        rows=[]
        for i in range(100):
            a=self.row("baseline",i>=30,4000);b=self.row("swat",True,50)
            a["task_id"]=str(i);b["task_id"]=str(i)
            rows.extend((a,b))
        r=calculate(rows)
        self.assertEqual(r["forty_x_target"]["all_selected_denominator"],100)
        self.assertEqual(r["forty_x_target"]["qualified_40x"],70)
        self.assertEqual(r["forty_x_target"]["fraction"],0.7)
    def test_unpaired(self):
        self.assertEqual(calculate([self.row("baseline")])["unpaired"],1)
if __name__=="__main__":unittest.main()
