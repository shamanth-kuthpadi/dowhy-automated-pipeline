# Streamlining DoWhy for Effect Estimation

DoWhy suggests that we perform effect estimation tasks using the following pipeline:

1. Establish a causal graph that encapsulates assumptions about given data
2. Identify possible causal questions (estimands) that we can find an estimate for
3. Estimate the identified estimand
4. Refute the estimate to check for validity and sensitivity

While I will not go into the motivation or reasoning behind this pipeline, I will modify the pipeline to something like this:

1. Establish a causal graph that encapsulates assumptions about given data
2. Refute the causal graph using statistical methods to check if the conditional independence statements dictated by our model align with the data.
3. Identify possible causal questions (estimands) that we can find an estimate for
4. Estimate the identified estimand
5. Refute the estimate to check for validity and sensitivity


## Source Code

The source code has a bunch of different files and so it is worthwhile to address any foreseen confusions. 

`EstimateEffect.py`contains the architecture to model the aforementioned pipeline for effect estimation.

`run_sachs.ipynb` is a notebook mainly used for informal testing whereas `tester.py` has unit tests that formally test the definitions in `EstimateEffect.py`. Please do note that, currently, not all definitions have been fully tested.

`data` is a directory containing the incredibly popular Sachs dataset.

`util.py` is simply a storage for utility functions that are used in various parts of this project.


## **EstimateEffect Class Documentation**

The `EstimateEffect` class is designed to estimate causal effects from a dataset by leveraging various causal discovery algorithms such as PC, GES, and LiNGAM. The class includes methods to discover causal graphs, falsify graphs, and estimate causal effects.

Before using the class, ensure you have the following dependencies installed:

- `causallearn`
- `dowhy`
- `pandas` (assuming the data is passed in as a pandas DataFrame)

You can install these dependencies using pip (ensure that you are using a python virtual environment with a python version == 3.10.14):

```bash
pip install causallearn dowhy pandas
```

### Attributes:
* `data`: The dataset (typically a pandas DataFrame) on which causal discovery and effect estimation will be performed.
* `graph`: The discovered causal graph.
* `graph_ref`: A reference to the causal graph, possibly with modifications.
* `model`: The dowhy.CausalModel object for estimating causal effects.
* `estimand`: The causal estimand, which represents the causal query.
* `estimate`: The estimated causal effect.
* `est_ref`: A reference to the estimated effect, potentially after adjustments.

### Initialization:

```python
estimator = EstimateEffect(data)
```

* `data`: A pandas DataFrame that contains the dataset you want to analyze.

### Methods:

`find_causal_graph(algo='pc', pk=None)`

This method discovers the causal graph from the dataset using a specified algorithm.

* Parameters:

    * `algo`: The algorithm to use for causal discovery. Options include 'pc', 'ges', and 'lingam'. The default is 'pc'.
    * `pk`: Prior knowledge, which can include required or forbidden edges in the graph. This is optional and should be passed as a dictionary:

```python
pk = {
    'required': [('A', 'B'), ('C', 'D')],
    'forbidden': [('E', 'F')]
}
```

* Returns: The discovered causal graph, which is stored in the graph attribute.

* Usage Example:

```python
causal_graph = estimator.find_causal_graph(algo='ges', pk={'required': [('X', 'Y')]})
```

---

`refute_cgm(self, n_perm=100, indep_test=gcm, cond_indep_test=gcm, apply_sugst=True, show_plt=False)`

This method refutes the previously discovered causal graphical model and applies suggestions that are returned by the algorithm (if it is set to true).

* Parameters:


