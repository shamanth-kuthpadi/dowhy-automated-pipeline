from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.ScoreBased.GES import ges
from causallearn.search.FCMBased import lingam
from causallearn.utils.PDAG2DAG import pdag2dag
from causallearn.search.FCMBased.lingam.utils import make_dot
from util import *
import dowhy.gcm.falsify
from dowhy.gcm.falsify import falsify_graph
from dowhy.gcm.falsify import apply_suggestions
from dowhy import CausalModel

class EstimateEffectv2:
    def __init__(self, data):
        self.data = data
        self.graph = None
        self.graph_ref = None
        self.model = None
        self.estimand = None
        self.estimate = None
        self.est_ref = None
    
    # For now, the only prior knowledge that the prototype will allow is required/forbidden edges
    # pk must be of the type => {'required': [list of edges to require], 'forbidden': [list of edges to forbid]}
    def find_causal_graph(self, algo='pc', pk=None):
        df = self.data.to_numpy()
        labels = list(self.data.columns)
        try:
            match algo:
                case 'pc':
                    cg = pc(data=df, show_progress=False, node_names=labels)
                    cg = pdag2dag(cg.G)
                    predicted_graph = genG_to_nx(cg, labels)
                    self.graph = predicted_graph
                case 'ges':
                    cg = ges(X=df, node_names=labels)
                    cg = pdag2dag(cg['G'])
                    predicted_graph = genG_to_nx(cg, labels)
                    self.graph = predicted_graph
                case 'icalingam':
                    model = lingam.ICALiNGAM()
                    model.fit(df)
                    pyd_lingam = make_dot(model.adjacency_matrix_, labels=labels)
                    pyd_lingam = pyd_lingam.pipe(format='dot').decode('utf-8')
                    pyd_lingam = (pyd_lingam,) = graph_from_dot_data(pyd_lingam)
                    dot_data_lingam = pyd_lingam.to_string()
                    pydot_graph_lingam = graph_from_dot_data(dot_data_lingam)[0]
                    predicted_graph = nx.drawing.nx_pydot.from_pydot(pydot_graph_lingam)
                    predicted_graph = nx.DiGraph(predicted_graph)
                    self.graph = predicted_graph
            
            if pk is not None:
                # ensuring that pk is indeed of the right type
                if not isinstance(pk, dict):
                    print(f"Please ensure that the prior knowledge is of the right form")
                    raise
                # are there any edges to require
                if 'required' in pk.keys():
                    eb = pk['required']
                    self.graph.add_edges_from(eb)
                # are there any edges to remove
                if 'forbidden' in pk.keys():
                    eb = pk['forbidden']
                    self.graph.remove_edges_from(eb)
        
        except Exception as e:
            print(f"Error in creating causal graph: {e}")
            raise

        return self.graph

    def refute_cgm(self, n_perm=100, indep_test=gcm, cond_indep_test=gcm, apply_sugst=True, show_plt=False):
        try:
            result = falsify_graph(self.graph, self.data, n_permutations=n_perm,
                                  independence_test=indep_test,
                                  conditional_independence_test=cond_indep_test, plot_histogram=show_plt)
            self.graph_ref = result
            if apply_sugst is True:
                self.graph = apply_suggestions(self.graph, result)
            
        except Exception as e:
            print(f"Error in refuting graph: {e}")
            raise

        return self.graph
    
    def create_model(self, treatment, outcome):
        model_est = CausalModel(
                data=self.data,
                treatment=treatment,
                outcome=outcome,
                graph=self.graph
            )
        self.model = model_est
        return self.model

    def identify_effect(self):
        try:
            identified_estimand = self.model.identify_effect(proceed_when_unidentifiable=False)
            self.estimand = identified_estimand
        except Exception as e:
            print(f"Error in identifying effect: {e}")
            raise
        return self.estimand
    
    def estimate_effect(self, method_cat='backdoor.linear_regression', ctrl_val=0, trtm_val=1):
        estimate = None
        try:
            match method_cat:
                case 'backdoor.linear_regression':
                    estimate = self.model.estimate_effect(self.estimand,
                                                  method_name=method_cat,
                                                  control_value=ctrl_val,
                                                  treatment_value=trtm_val,
                                                  confidence_intervals=True,
                                                  test_significance=True)
                # there are other estimation methods that I can add later on, however parameter space will increase immensely
            self.estimate = estimate
        except Exception as e:
            print(f"Error in estimating the effect: {e}")
            raise

        return self.estimate
    
    def refute_estimate(self,  method_name="placebo_treatment_refuter", placebo_type=None, subset_fraction=None):
        ref = None
        try:
            match method_name:
                case "placebo_treatment_refuter":
                    ref = self.model.refute_estimate(
                        self.estimand,
                        self.estimate,
                        method_name=method_name,
                        placebo_type=placebo_type
                    )
                
                case "random_common_cause":
                    ref = self.model.refute_estimate(
                        self.estimand,
                        self.estimate,
                        method_name=method_name
                    )
                case "data_subset_refuter":
                    ref = self.model.refute_estimate(
                        self.estimand,
                        self.estimate,
                        method_name=method_name,
                        subset_fraction=subset_fraction
                    )
            self.est_ref = ref
        
        except Exception as e:
            print(f"Error in refuting estimate: {e}")
            raise
            
        return self.est_ref