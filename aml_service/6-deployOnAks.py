# Import libraries
import os, json, datetime, sys
from operator import attrgetter
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.core.webservice import Webservice, AksWebservice
from azureml.core.authentication import AzureCliAuthentication

# Get an Azure CLI authentication object
cli_auth = AzureCliAuthentication()

# Get workspace from authentication
ws = Workspace.from_config(auth=cli_auth)

# Get the Image to deploy details
try:
    # Read file aml_config/image.json
    with open("aml_config/image.json") as f:
        image_config = json.load(f)
except:
    print("No new model, thus no deployment on AKS")
    # Ending process, nothing else to do
    sys.exit(0)

# Get image details from file
image_name = image_config["image_name"]
image_version = image_config["image_version"]

# List existing images in workspace
images = Image.list(workspace=ws)
image, = (m for m in images if m.version == image_version and m.name == image_name)
print(
    "From image.json, Image used to deploy webservice on AKS: {}\nImage Version: {}\nImage Location = {}".format(
        image.name, image.version, image.image_location
    )
)

# Check if AKS already Available
try:
    # Read file aml_config/aks_webservice.json
    with open("aml_config/aks_webservice.json") as f:
        aks_config = json.load(f)
    aks_service_name = aks_config["aks_service_name"]

    # Get existing web service
    service = Webservice(name=aks_service_name, workspace=ws)
    print(
        "Updating AKS service {} with image: {}".format(
            aks_service_name, image.image_location
        )
    )
    # Update existing web service with new image
    service.update(image=image)
except:

    # Set the resource group that contains the AKS cluster and the cluster name
    # Read file with configuration variables
    with open("aml_config/config.json") as f:
        config = json.load(f)
    resource_group = config["resource_group"]
    aks_name = config["aks_name"]
    aks_service_name = config["aks_service_name"]
    aks_namespace = config["aks_namespace"]
    
    print(
        "No AKS found in aks_webservice.json. Getting AKS: {} and AKS Webservice: {}".format(
            aks_name, aks_service_name
        )
    )

    # Detect previous configuration
    try:
        # Existing attached cluster
        aks_target = AksCompute(ws, aks_name)
        print(
            "Already attached AKS {}".format(
                aks_name)
        )
    except:
        # Attach existing AKS cluster
        print(
            "Attaching AKS {}".format(
                aks_name)
        )
        # Link to existing AKS
        attach_config = AksCompute.attach_configuration(resource_group = resource_group,
                                                cluster_name = aks_name,
                                                cluster_purpose = AksCompute.ClusterPurpose.DEV_TEST)
        aks_target = ComputeTarget.attach(ws, aks_name, attach_config)

        aks_target.wait_for_completion(show_output=True)

    # Set the web service configuration
    aks_config = AksWebservice.deploy_configuration(enable_app_insights=True, 
                                                    compute_target_name=aks_name,
                                                    namespace = aks_namespace,
                                                    scoring_timeout_ms = 300000,
                                                    cpu_cores = 1,
                                                    memory_gb = 1)
 
    # Deploy a new web service with the provided configuration
    service = Webservice.deploy_from_image(
        workspace=ws,
        name=aks_service_name,
        image=image,
        deployment_config=aks_config,
        deployment_target=aks_target
    )
 
    service.wait_for_deployment(show_output=True)
    print(service.state)
    
    print(
        "Deployed AKS Webservice: {} \nWebservice Uri: {}".format(
            service.name, service.scoring_uri
        )
    )


# Writing the AKS details to /aml_config/aks_webservice.json
aks_webservice = {}
aks_webservice["aks_name"] = aks_name
aks_webservice["aks_service_name"] = service.name
aks_webservice["aks_namespace"] = aks_namespace
aks_webservice["aks_url"] = service.scoring_uri
aks_webservice["aks_keys"] = service.get_keys()
with open("aml_config/aks_webservice.json", "w") as outfile:
    json.dump(aks_webservice, outfile)
