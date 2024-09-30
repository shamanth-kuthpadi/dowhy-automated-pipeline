import unittest
import pandas as pd
from util import *
from EstimateEffect import EstimateEffect

class TestEstimateEffectv2(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.data = load_from_txt('/Users/shamanthk/Documents/eval-dowhy-caunex/datasets/sachs.2005.continuous.txt')
        cls.estimator = EstimateEffect(cls.data)
    
    def test_pc_algorithm(self):
        try:
            graph = self.estimator.find_causal_graph(algo='pc')
            self.assertIsNotNone(graph)
            print("PC Algorithm executed successfully.")
        except Exception as e:
            self.fail(f"PC Algorithm failed with exception: {e}")
    
    def test_ges_algorithm(self):
        try:
            graph = self.estimator.find_causal_graph(algo='ges')
            self.assertIsNotNone(graph)
            print("GES Algorithm executed successfully.")
        except Exception as e:
            self.fail(f"GES Algorithm failed with exception: {e}")
    
    def test_icalingam_algorithm(self):
        try:
            graph = self.estimator.find_causal_graph(algo='icalingam')
            self.assertIsNotNone(graph)
            print("ICALiNGAM Algorithm executed successfully.")
        except Exception as e:
            self.fail(f"ICALiNGAM Algorithm failed with exception: {e}")
    
    def test_prior_knowledge_integration(self):
        required_edges = [('akt', 'pip3')]  # Example edges; replace with your specifics
        forbidden_edges = [('akt', 'jnk')]
        pk_obj = {'required': required_edges, 'forbidden': forbidden_edges}
        try:
            graph = self.estimator.find_causal_graph(
                algo='pc',
                pk=pk_obj
            )
            self.assertIsNotNone(graph)
            # Further assertions can be added to check if the required/forbidden edges are present/absent
            print("Prior knowledge integrated successfully.")
        except Exception as e:
            self.fail(f"Prior knowledge integration failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
