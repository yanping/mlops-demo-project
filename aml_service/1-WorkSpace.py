# Import libraries
from azureml.core import Workspace
import os, json, sys
import azureml.core
from azureml.core.authentication import AzureCliAuthentication

# Print current SDK version
print("SDK Version:", azureml.core.VERSION)

# Read file with configuration variables
# This is a recommended practice
with open("aml_config/config.json") as f:
    config = json.load(f)

# Declare resource configuration local variables
workspace_name = config["workspace_name"]
resource_group = config["resource_group"]
subscription_id = config["subscription_id"]
location = config["location"]

# Create or get an Azure CLI authentication object
# Allows you to open an Azure authentication window if not authenticated yet
cli_auth = AzureCliAuthentication()

try:
    # Get existing workspace with the provided configuration
    # Save the workspace configuration in the 'ws' variable
    ws = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=cli_auth
    )

except:
    # If the workspace does not exist, create a new one
    # This call might take a minute or two
    print("Creating new workspace")
    ws = Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        # create_resource_group=True,   # Optional
        location=location,
        auth=cli_auth

    )

# Print Workspace details
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep="\n")
