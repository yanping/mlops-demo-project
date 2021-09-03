# Import libraries
import os, json, sys
from azureml.core import Workspace
from azureml.core import Run
from azureml.core import Experiment
from azureml.core.model import Model
from azureml.core.runconfig import RunConfiguration
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Get the latest evaluation result
try:
    with open("aml_config/run_id.json") as f:
        run_config = json.load(f)
    if not run_config["run_id"]:
        raise Exception("No new model to register as production model perform better")
except:
    print("No new model to register as production model perform better")
    # Ending process, nothing else to do
    sys.exit(0)

# Save the run details in local variables
run_id = run_config["run_id"]
experiment_name = run_config["experiment_name"]

# Get the experiment with the provided name
exp = Experiment(workspace=ws, name=experiment_name)

# Get the run history
run = Run(experiment=exp, run_id=run_id)

# List the files that are stored in association with the run
names = run.get_file_names
names()
print("Run ID for last run: {}".format(run_id))

# Create local directory
model_local_dir = "model"
os.makedirs(model_local_dir, exist_ok=True)

# Read file with configuration variables
with open("aml_config/config.json") as f:
    config = json.load(f)

# Get model details from config file
model_name = config["model_name"]
model_description = config["model_description"]
model_tags = config["model_tags"]
# Add run ID to tags
model_tags["run_id"] = run_id

# Download Model to Project root directory
run.download_file(
    name="./outputs/" + model_name, output_file_path="./model/" + model_name
)
print("Downloaded model {} to Project root directory".format(model_name))
os.chdir("./model")

# Register model with register method from Model library
model = Model.register(
    model_path=model_name,  # this points to a local file
    model_name=model_name,  # this is the name the model is registered as
    tags=model_tags,
    description=model_description,
    workspace=ws,
)
os.chdir("..")

# Print model details
print(
    "Model registered: {} \nModel Description: {} \nModel Version: {}".format(
        model.name, model.description, model.version
    )
)

# Remove the evaluate.json as we no longer need it
# Optional
# os.remove("aml_config/evaluate.json")

# Write the registered model details to /aml_config/model.json
model_json = {}
model_json["model_name"] = model.name
model_json["model_version"] = model.version
model_json["run_id"] = run_id
with open("aml_config/model.json", "w") as outfile:
    json.dump(model_json, outfile)
