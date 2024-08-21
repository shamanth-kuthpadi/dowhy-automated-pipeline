'''
The purpose of this file is to try all the various causal-learn algorithms
and find the best causal model for the given dataset
'''

from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.ScoreBased.GES import ges
from causallearn.search.FCMBased import lingam
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
        self.algos = ['pc', 'ges', 'icalingam']
        self.idx = 0

    def _create_cgm(self):
        algorithm = self.algos[self.idx]
        try:
            match algorithm:
                case 'pc':
                    df = self.data.to_numpy()
                    labels = self.data.columns
                    cg = pc(data=df, show_progress=False, node_names=labels)
                    cg = pdag2dag(cg.G)
                    predicted_graph = genG_to_nx(cg, labels)
                    self.graph = predicted_graph
                    return
                case 'ges':
                    df = self.data.to_numpy()
                    labels = self.data.columns
                    cg = ges(data=df, show_progress=False, node_names=labels)
                    cg = pdag2dag(cg['G'])
                    predicted_graph = genG_to_nx(cg, labels)
                    self.graph = predicted_graph
                    return
                case 'icalingam':
                    model = lingam.ICALiNGAM()
                    model.fit(df)
                    pyd_lingam = pyd_lingam.pipe(format='dot').decode('utf-8')
                    pyd_lingam = (pyd_lingam,) = graph_from_dot_data(pyd_lingam)
                    dot_data_lingam = pyd_lingam.to_string()
                    predicted_graph = genG_to_nx(dot_data_lingam, labels)
                    self.graph = predicted_graph

        except Exception as e:
            print(f"Error in creating causal graph: {e}")
            raise

    def _refute_graph(self):
        try:
            result = falsify_graph(self.graph, self.data, n_permutations=self.perm,
                                  independence_test=gcm,
                                  conditional_independence_test=gcm)
            self.graph_ref = result
            mod_graph = apply_suggestions(self.graph, result)
            self.graph = mod_graph
        except Exception as e:
            print(f"Error in refuting graph: {e}")
            raise

    def _identify_effect(self):
        try:
            model_est = CausalModel(
                data=self.data,
                treatment=self.trtment,
                outcome=self.otce,
                graph=self.graph
            )
            self.model = model_est
            identified_estimand = model_est.identify_effect(proceed_when_unidentifiable=False)
            self.estimand = identified_estimand
        except Exception as e:
            print(f"Error in identifying effect: {e}")
            raise

    def _estimate(self, method_name="backdoor.linear_regression"):
        try:
            estimate = self.model.estimate_effect(self.estimand,
                                                  method_name=method_name,
                                                  control_value=0,
                                                  treatment_value=1,
                                                  confidence_intervals=True,
                                                  test_significance=True)
            self.estimate = estimate
        except Exception as e:
            print(f"Error in estimating effect: {e}")
            raise

    def _refute_estimate(self, method_name="placebo_treatment_refuter"):
        try:
            refute_placebo_treatment = self.model.refute_estimate(
                self.estimand,
                self.estimate,
                method_name=method_name,
                placebo_type="permute"
            )
            self.pval = refute_placebo_treatment
        except Exception as e:
            print(f"Error in refuting estimate: {e}")
            raise

    def get_refutation_results(self):
        print("Refuted Graph:")
        print(self.graph_ref)
        print("Refutation p-value:")
        print(self.pval)

    def perform_effect_estimation(self, estimation_method="backdoor.linear_regression", refutation_method="placebo_treatment_refuter"):
        significant = True
        while significant is True and self.idx < len(self.algos):
            try:
                # Create the causal graph
                self._create_cgm()
                
                # Refute the causal graph and apply suggestions
                self._refute_graph()

                # Identify the estimand
                self._identify_effect()

                # Estimate the effect
                self._estimate(method_name=estimation_method)

                # Refute the estimate
                self._refute_estimate(method_name=refutation_method)

                print(self.estimate)

                if self.pval.refutation_result['is_statistically_significant'] is False:
                    significant = False
                    return self.estimate
                else:
                    if self.idx == len(self.algos)-1:
                        print("Best estimate found, but it should be considered with caution.")
                        return self.estimate
                    self.idx += 1
            except Exception as e:
                print(f"Error during effect estimation with {self.algos[self.idx]}: {e}")
                raise




