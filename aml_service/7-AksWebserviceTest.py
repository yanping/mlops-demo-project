# Import libraries
import numpy
import os, json, datetime, sys
from operator import attrgetter
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Get the AKS Details
try:
    # Read file aml_config/aks_webservice.json
    with open("aml_config/aks_webservice.json") as f:
        config = json.load(f)
except:
    print("No new model, thus no deployment on AKS")
    # Ending process, nothing else to do
    sys.exit(0)

# Get the service name from aks_webservice.json
service_name = config["aks_service_name"]
# Get the hosted web service from workspace
service = Webservice(workspace=ws, name=service_name)

# Input for Model with all features
# Read data from data_test.json
with open("data/data_test.json") as f:
    data_test = json.load(f)

# Configurate the data for testing in web service
input_j = data_test["data"][0]
print(input_j)
test_sample = json.dumps({"data": input_j})
test_sample = bytes(test_sample, encoding="utf8")
try:
    # Call service
    prediction = service.run(input_data=test_sample)
    print(prediction)
except Exception as e:
    result = str(e)
    print(result)
    raise Exception("AKS service is not working as expected")

# Delete service after test
# Optional
# service.delete()
