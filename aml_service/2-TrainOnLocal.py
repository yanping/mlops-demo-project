# Import libraries
from azureml.core.runconfig import RunConfiguration
from azureml.core import Workspace
from azureml.core import Experiment
from azureml.core import ScriptRunConfig
import json
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Read file with configuration variables
with open("aml_config/config.json") as f:
    config = json.load(f)

# Create or attach experiment
experiment_name = config["experiment_name"]
exp = Experiment(workspace=ws, name=experiment_name)
# Print experiment details
print(exp.name, exp.workspace.name, sep="\n")

# Edit a run configuration property on-fly
run_config_user_managed = RunConfiguration()
run_config_user_managed.environment.python.user_managed_dependencies = True

print("Submitting an experiment.")
# Save configuration information for submitting a training run
src = ScriptRunConfig(
    source_directory="./code",
    script="training/train.py",
    run_config=run_config_user_managed,
)
# Submit a run (into experiment)
run = exp.submit(src)

# Show output of the run on stdout
run.wait_for_completion(show_output=True, wait_post_processing=True)

# Raise exception if run fails
if run.get_status() == "Failed":
    raise Exception(
        "Training on local failed with following run status: {} and logs: \n {}".format(
            run.get_status(), run.get_details_with_logs()
        )
    )

# Write the run details to /aml_config/run_id.json
run_id = {}
run_id["run_id"] = run.id
run_id["experiment_name"] = run.experiment.name
with open("aml_config/run_id.json", "w") as outfile:
    json.dump(run_id, outfile)
