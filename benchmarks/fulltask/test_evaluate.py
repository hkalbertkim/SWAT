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
    def test_unpaired(self):
        self.assertEqual(calculate([self.row("baseline")])["unpaired"],1)
if __name__=="__main__":unittest.main()
