Build-Your-Own Machine Learning(BYO ML) package, currently in public preview, is provided by Azure Sentinel team to help organizations build or bring your own ML to tackle security problems specifically for your business. This folder contains the BYO ML package including the first ML algorithm  Azure Sentinel team shares.

The package includes:

Library (.whl files)
- azure_sentinel_ml_utilities - Library contains Azure Storage & Log Analytics helper functions.

Notebooks:

Following three Notebooks work with the collaborative filtering algorithm for Anomalous Resource Access (File Share Access as example) 

- AnonymousRATraining.ipynb - This Notebook trains and stores the model in Blob Storage.
- AnonymousRAScoring.ipynb - This Notebook schedules the scoring and writes the highest scored results into Log Analytics so the score can be used for hunting, detection, investigation in Azure Sentinel.
- AnonymousRASampleData.ipynb - This notebook demonstrates the use of Anomalous Resource Access model in Sentinel. It generates training and testing data, trains the Anomalous Resource Access model and uses it to score the test data. The top predicted scores are submitted to Sentinel workspace.
		
It is run from Azure Databricks
- Standard_DS4_v2 (28 GB)
- Version 5.5 (includes Apache Spark 2.4.0, Scala 2.11)

Other libraries:
- azure.storage.blob==2.1.0 (from PyPi)
- scikit-surprise==1.0.6 (from PyPi)
- numpy==1.15.0 (from PyPi)
- pyarrow==0.12.0 (from PyPi)
- plotly  (from PyPi,for Sankey diagram)

Notes:
- Credentials for Azure Storage and Log Analytics are kept in KeyVault
- The training data is preprocessed to sum total access in a day - this is used as the initial score for training
- The Data reading library assumes a certain folder format.  If your folders don't match it, you will have to read int input files differently.

Training Data vs Testing Data

Training data fields:
- TimeStamp				- Day in which the access happened
- User					- User accessing the resource
- Resource				- resource name
- Categorical features			- (not used, could be 0)
- Count					- Total number of access on that day		

Testing data fields:
- TimeStamp				- Time of access
- User					- User accessing the resource
- Resource				- resource name
- Categorical features			- (not used, could be 0)
- Count					- (not needed)
	
