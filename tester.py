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
    
    def test_prior_knowledge(self):
        required_edges = [('akt', 'pip3')] 
        forbidden_edges = [('akt', 'jnk')]
        pk_obj = {'required': required_edges, 'forbidden': forbidden_edges}
        try:
            graph = self.estimator.find_causal_graph(
                algo='pc',
                pk=pk_obj
            )
            self.assertIsNotNone(graph)

            print("Prior knowledge integrated successfully.")
        except Exception as e:
            self.fail(f"Prior knowledge integration failed with exception: {e}")
    
    def test_prior_knowledge_integration(self):
        required_edges = [('akt', 'pip3')]  
        forbidden_edges = [('akt', 'jnk')]
        pk_obj = {'required': required_edges, 'forbidden': forbidden_edges}
        
        try:
            graph = self.estimator.find_causal_graph(
                algo='pc',
                pk=pk_obj
            )
    
            self.assertIsNotNone(graph)
            generated_edges = set(graph.edges())

            for edge in required_edges:
                self.assertIn(edge, generated_edges, f"Required edge {edge} is missing from the graph.")

            for edge in forbidden_edges:
                self.assertNotIn(edge, generated_edges, f"Forbidden edge {edge} is present in the graph.")

            print("Prior knowledge integrated successfully.")
        
        except Exception as e:

            self.fail(f"Prior knowledge integration failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
