# Import libraries
import os, json
from azureml.core import Workspace
from azureml.core import Experiment
from azureml.core.model import Model
import azureml.core
from azureml.core import Run
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Get the latest run_id from file
with open("aml_config/run_id.json") as f:
    config = json.load(f)

# Save the run details in local variables
new_model_run_id = config["run_id"]
experiment_name = config["experiment_name"]

# Get the experiment with the provided name
exp = Experiment(workspace=ws, name=experiment_name)

# TODO: Paramaterize the metrics on which the models should be compared
# TODO: Add golden data set on which all the model performance can be evaluated

try:
    # Get most recently registered model (we assume that is the model in production)
    # Download this model and compare it with the recently trained model by running test with same data set
    model_list = Model.list(ws)
    production_model = next(
        filter(
            lambda x: x.created_time == max(model.created_time for model in model_list),
            model_list,
        )
    )
    production_model_run_id = production_model.tags.get("run_id")

    # Get list of experiment runs
    run_list = exp.get_runs()

    # Get the run history for both production model and newly trained model 
    production_model_run = Run(exp, run_id=production_model_run_id)
    new_model_run = Run(exp, run_id=new_model_run_id)

    # Get value of metric that will be used for comparison ('mse' in this case)
    production_model_mse = production_model_run.get_metrics().get("mse")
    new_model_mse = new_model_run.get_metrics().get("mse")
    print(
        "Current Production model mse: {}, New trained model mse: {}".format(
            production_model_mse, new_model_mse
        )
    )

    # Compare metric
    promote_new_model = False
    if new_model_mse < production_model_mse:
        # Set flag to True as new model performs better
        promote_new_model = True
        print("New trained model performs better, thus it will be registered")
except:
    # Set flag to True as new model is the first model to be registered
    promote_new_model = True
    print("This is the first model to be trained, thus nothing to evaluate for now")

run_id = {}
run_id["run_id"] = ""
# Writing the run id to /aml_config/run_id.json
if promote_new_model:
    run_id["run_id"] = new_model_run_id

run_id["experiment_name"] = experiment_name
with open("aml_config/run_id.json", "w") as outfile:
    json.dump(run_id, outfile)
