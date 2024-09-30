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

## How to Use `EstimateEffect.py`

Really, the guideline to use the automated model follows the pipeline architecture. As a preliminary, load your data as a Pandas DataFrame.

Look at the example notebook `run_sachs.ipynb` to understand and learn how to use the model. In this notebook you should also be able to see the various parameters and return values of definitions/methods.
