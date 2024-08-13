'''
The purpose of this file is to try all the various causal-learn algorithms
and find the best causal model for the given dataset
'''

from causallearn.search.ConstraintBased.PC import pc
from causallearn.utils.PDAG2DAG import pdag2dag
from util import *
import dowhy.gcm.falsify
from dowhy.gcm.falsify import falsify_graph
from dowhy.gcm.falsify import apply_suggestions
from dowhy import CausalModel


class EstimateEffect:
    def __init__(self, df, treatment, outcome, perm=100):
        self.data = df
        self.graph = None
        self.perm = perm
        self.trtment = treatment
        self.otce = outcome
        self.estimand = None
        self.model = None
        self.estimate = 0
        self.pval = None
        self.graph_ref = None
    
    def _create_cgm(self):
        df = self.data.to_numpy()
        labels = self.data.columns
        cg = pc(data=df, show_progress=False, node_names=labels)
        cg = pdag2dag(cg.G)
        predicted_graph = genG_to_nx(cg, labels)
        self.graph = predicted_graph
    
    def _refute_graph(self):
        result = falsify_graph(self.graph, self.data, n_permutations=self.perm,
                              independence_test=gcm,
                              conditional_independence_test=gcm)
        self.graph_ref = result
        mod_graph = apply_suggestions(self.graph, result)
        self.graph = mod_graph
    
    def _identify_effect(self):
        model_est=CausalModel(
            data = self.data,
            treatment=self.trtment,
            outcome=self.otce,
            graph=self.graph)
        
        self.model = model_est
        
        identified_estimand = model_est.identify_effect(proceed_when_unidentifiable=False)
        self.estimand = identified_estimand
    
    def _estimate(self):
        estimate = self.model_est.estimate_effect(self.estimand,
                                method_name="backdoor.linear_regression",
                                control_value=0,
                                treatment_value=1,
                                confidence_intervals=True,
                                test_significance=True)
        
        self.estimate = estimate
    
    def _refute_estimate(self):
        refute_placebo_treatment = self.model.refute_estimate(
            self.estimand,
            self.estimate,
            method_name="placebo_treatment_refuter",
            placebo_type="permute"
        )

        self.pval = refute_placebo_treatment

    def get_refutation_results(self):
        print(self.graph_ref)
        print(self.pval)
    
    def perform_effect_estimation(self):
        # First create the causal graph
        self._create_cgm()
        
        # refute the causal graph and apply suggestions
        self._refute_graph()

        # identify the estimand
        self._identify_effect()

        # estimate the estimand
        self._estimate()

        # refute the estimate
        self._refute_estimate()

        return self.estimate



