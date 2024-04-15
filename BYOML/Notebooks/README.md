Following three Notebooks work with the collaborative filtering algorithm for Anomalous Resource Access (File Share Access as example)

AnonymousRASampleData.ipynb - This notebook demonstrates the use of Anomalous Resource Access model in Sentinel. It generates training and testing data, trains the Anomalous Resource Access model and uses it to score the test data. The top predicted scores are submitted to Sentinel workspace.

AnonymousRATraining.ipynb - This Notebook trains and stores the model in Blob Storage.

AnonymousRAScoring.ipynb - This Notebook schedules the scoring and writes the highest scored results into Log Analytics so the score can be used for hunting, detection, investigation in Azure Sentinel.

