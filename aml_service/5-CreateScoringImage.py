# Import libraries
import os, json, sys
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Get the latest model details
try:
    with open("aml_config/model.json") as f:
        model_config = json.load(f)
except:
    print("No new model to register thus no need to create new scoring image")
    # Ending process, nothing else to do
    sys.exit(0)

# Get model details from model.json file
model_name = model_config["model_name"]
model_version = model_config["model_version"]

# Read file with configuration variables
with open("aml_config/config.json") as f:
    config = json.load(f)

# Get image details from config file
image_name = config["image_name"]
image_description = config["image_description"]
image_tags = config["model_tags"]

# Get models registered in workspace
model_list = Model.list(workspace=ws)
# Get model with provided configuration
model, = (m for m in model_list if m.version == model_version and m.name == model_name)
print(
    "Model picked: {} \nModel Description: {} \nModel Version: {}".format(
        model.name, model.description, model.version
    )
)
os.chdir("./code/scoring")



# Create a container image configuration with the provided configuration
image_config = ContainerImage.image_configuration(
    execution_script="score.py",
    runtime="python-slim",
    conda_file="conda_dependencies.yml",
    description=image_description,
    tags=image_tags,
)

# Create an image with the image configuration provided
image = Image.create(
    name=image_name, models=[model], image_config=image_config, workspace=ws
)
image.wait_for_creation(show_output=True)
os.chdir("../..")

# Check if creation was successful
if image.creation_state != "Succeeded":
    raise Exception("Image creation status: {image.creation_state}")

# Print image details
print(
    "{}(v.{} [{}]) stored at {} with build log {}".format(
        image.name,
        image.version,
        image.creation_state,
        image.image_location,
        image.image_build_log_uri,
    )
)

# Writing the image details to /aml_config/image.json
image_json = {}
image_json["image_name"] = image.name
image_json["image_version"] = image.version
image_json["image_location"] = image.image_location
with open("aml_config/image.json", "w") as outfile:
    json.dump(image_json, outfile)
