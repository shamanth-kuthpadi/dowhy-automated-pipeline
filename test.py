from EstimateEffectv2 import *

df = load_from_txt('/Users/shamanthk/Documents/eval-dowhy-caunex/datasets/sachs.2005.continuous.txt')
labels = df.columns
df.head()

effest = EstimateEffectv2(data=df)

# # checking to make sure that the class is imported
# print(effest)

# # now testing the find_causal_graph functionality
# # without prior knowledge
# # pc
# cg = effest.find_causal_graph(algo='pc')
# disp_graph_nx(cg)

# # now testing the find_causal_graph functionality
# # without prior knowledge
# # ges

# cg = effest.find_causal_graph(algo='ges')
# disp_graph_nx(cg)

# # now testing the find_causal_graph functionality
# # without prior knowledge
# # icalingam

# cg = effest.find_causal_graph(algo='icalingam')
# disp_graph_nx(cg)

cg = effest.find_causal_graph(algo='icalingam')
disp_graph_nx(cg)
prior_kn = {'required': [('pip3', 'erk')], 'forbidden': [('jnk', 'akt')]}
cg = effest.find_causal_graph(algo='icalingam', pk=prior_kn)
disp_graph_nx(cg)