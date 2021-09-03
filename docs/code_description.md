## Repo Details

### Environment Setup

- requirements.txt : It consists of a list of python packages which are needed by the train.py to run successfully on host agent (locally).

- install_requirements.sh : This script prepares the python environment (i.e. install the Azure ML SDK and the packages specified in requirements.txt)

### Config Files
All the scripts inside the ./aml_config folder are configuration files. These are the files where you need to provide details about the subscription, resource group, workspace, conda dependencies, remote vm, AKS etc.

- config.json : This is a mandatory config file. Provide the subscription id, resource group name, workspace name and location where you want to create Azure ML services workspace. If you have already created the workspace, provide the existing workspace details in here. You can also include other required variables (i.e. webservice name)

- conda_dependencies.yml : This is a mandatory file. This files contains the list of dependencies which are needed by the training/scoring script to run. This file is used to prepare environment for the local run(user managed/system managed) and docker run (local/remote).

- aks_webservice.json : This is an optional configuration file. If you already have an AKS attached to your workspace, then provide the details in this file. If not, you do not have to check in this file to git.

### Build Pipeline Scripts

The scripts under ./aml_service folder are used in build pipeline. These are the scripts which need to be run only once. There is no harm of running these scripts every time in build pipeline.

- 1-WorkSpace.py : This is a onetime run script. It reads the workspace details from ./aml_config/config.json file and creates (if workspace not available) or gets (existing workspace). 

- 2-TrainOnLocal.py : This script triggers the run of ./training/train.py script on the local compute (Host agent). All the training scripts generate an output file aml_config/run_id.json which records the run_id and run history name of the training run. run_id.json is used by 4-RegisterModel.py to get the trained model.

- 3-EvaluateModel.py : It gets the metrics of latest model trained and compares it with the model in production. If the production model still performs better, all below scripts are skipped. 

- 4-RegisterModel.py : It gets the run id from training steps output json and registers the model associated with that run along with tags. This scripts outputs a model.json file which contains model name and version. This script is included as build task.

- 5-CreateScoringImage.py : This takes the model details from last step, creates a scoring webservice docker image and publishes the image to ACR. This script is included as build task. It writes the image name and version to image.json file.

### Deployment/Release Scripts
Files under the directory ./aml_service are used in release pipeline. They are basically to deploy the docker image on AKS and publish webservice on them.

- 6-deployOnAks.py : This script reads the image.json which is published as an artifact from build pipeline, creates AKS cluster and deploys the scoring web service on it. If the aks_webservice.json file was checked in with existing AKS details, it will update the existing webservice with the new Image. It writes the scoring service details to aks_webservice.json

- 7-AksWebServiceTest.py : Reads the AKS info from aks_webservice.json and tests it with the sample data provided.

### Training/Scoring Scripts

- /code/training/train.py : This is the model training code. It uploads the model file to AML Service run id once the training is successful. This script is submitted as run job by all the build pipeline scripts.

- /code/scoring/score.py : This is the score file used to create the webservice docker image. There is a conda_dependencies.yml in this directory which is exactly same as the one in aml_config. These two files are needed by the 5-CreateScoringImage.py scripts to be in the same root directory while creating the image.

**Note: In CICD Pipeline, please make sure that the working directory is the root directory of the repo.**  

