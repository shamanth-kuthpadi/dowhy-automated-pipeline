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