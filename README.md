[![.github/workflows/azure-dev.yml](https://github.com/rachhek/pdf-search-assistant/actions/workflows/azure-dev.yml/badge.svg)](https://github.com/rachhek/pdf-search-assistant/actions/workflows/azure-dev.yml)

# About
The aim of this project is to build a tool that can:
1. Search for answers from an uploaded PDF(s)
2. Filter the search on specific page components (e.g. headers, sub header, tables, paragraphs, etc.)
3. Filter the search on specific pages
4. Show the search results as PDF annotations
5. Summarize the answers for the questions in a concise manner

# How?
The project will use Microsoft form recognizer to extract the text from the PDFs and then use a search engine to search for the answers. The search engine will be built using Azure Cognitive Search.The summarization will done using a Large Language Model from Azure OpenAI service.

# Project Setup
The project is built using Azure Developer CLI (azd). The following is the README from the azd starter project.

# Azure Developer CLI (azd) Bicep Starter

A starter blueprint for getting your application up on Azure using [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview) (azd). Add your application code, write Infrastructure as Code assets in [Bicep](https://aka.ms/bicep) to get your application up and running quickly.

The following assets have been provided:

- Infrastructure-as-code (IaC) Bicep files under the `infra` folder that demonstrate how to provision resources and setup resource tagging for azd.
- A [dev container](https://containers.dev) configuration file under the `.devcontainer` directory that installs infrastructure tooling by default. This can be readily used to create cloud-hosted developer environments such as [GitHub Codespaces](https://aka.ms/codespaces).
- Continuous deployment workflows for CI providers such as GitHub Actions under the `.github` directory, and Azure Pipelines under the `.azdo` directory that work for most use-cases.

# Project Directory
1. app : Streamlit application host.
2. infra : Bicep files for provisioning Azure resources.
3. scripts : Powershell and shell scripts storage.
4. data: Store files for the application

## Next Steps

### Step 1: Add application code

1. Initialize the service source code projects anywhere under the current directory. Ensure that all source code projects can be built successfully.
    - > Note: For `function` services, it is recommended to initialize the project using the provided [quickstart tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-get-started).
2. Once all service source code projects are building correctly, update `azure.yaml` to reference the source code projects.
3. Run `azd package` to validate that all service source code projects can be built and packaged locally.

### Step 2: Provision Azure resources

Update or add Bicep files to provision the relevant Azure resources. This can be done incrementally, as the list of [Azure resources](https://learn.microsoft.com/en-us/azure/?product=popular) are explored and added.

- A reference library that contains all of the Bicep modules used by the azd templates can be found [here](https://github.com/Azure-Samples/todo-nodejs-mongo/tree/main/infra/core).
- All Azure resources available in Bicep format can be found [here](https://learn.microsoft.com/en-us/azure/templates/).

Run `azd provision` whenever you want to ensure that changes made are applied correctly and work as expected.

### Step 3: Tie in application and infrastructure

Certain changes to Bicep files or deployment manifests are required to tie in application and infrastructure together. For example:

1. Set up [application settings](#application-settings) for the code running in Azure to connect to other Azure resources.
1. If you are accessing sensitive resources in Azure, set up [managed identities](#managed-identities) to allow the code running in Azure to securely access the resources.
1. If you have secrets, it is recommended to store secrets in [Azure Key Vault](#azure-key-vault) that then can be retrieved by your application, with the use of managed identities.
1. Configure [host configuration](#host-configuration) on your hosting platform to match your application's needs. This may include networking options, security options, or more advanced configuration that helps you take full advantage of Azure capabilities.

For more details, see [additional details](#additional-details) below.

When changes are made, use azd to validate and apply your changes in Azure, to ensure that they are working as expected:

- Run `azd up` to validate both infrastructure and application code changes.
- Run `azd deploy` to validate application code changes only.

### Step 4: Up to Azure

Finally, run `azd up` to run the end-to-end infrastructure provisioning (`azd provision`) and deployment (`azd deploy`) flow. Visit the service endpoints listed to see your application up-and-running!

## Additional Details

The following section examines different concepts that help tie in application and infrastructure.

### Application settings

It is recommended to have application settings managed in Azure, separating configuration from code. Typically, the service host allows for application settings to be defined.

- For `appservice` and `function`, application settings should be defined on the Bicep resource for the targeted host. Reference template example [here](https://github.com/Azure-Samples/todo-nodejs-mongo/tree/main/infra).
- For `aks`, application settings are applied using deployment manifests under the `<service>/manifests` folder. Reference template example [here](https://github.com/Azure-Samples/todo-nodejs-mongo-aks/tree/main/src/api/manifests).

### Managed identities

[Managed identities](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) allows you to secure communication between services. This is done without having the need for you to manage any credentials.

### Azure Key Vault

[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview) allows you to store secrets securely. Your application can access these secrets securely through the use of managed identities.

### Host configuration

For `appservice`, the following host configuration options are often modified:

- Language runtime version
- Exposed port from the running container (if running a web service)
- Allowed origins for CORS (Cross-Origin Resource Sharing) protection (if running a web service backend with a frontend)
- The run command that starts up your service

### Prerequisites

#### To Run Locally
- [Azure Developer CLI](https://aka.ms/azure-dev/install)
- [Python 3+](https://www.python.org/downloads/)
    - **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
    - **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.    
- [Node.js](https://nodejs.org/en/download/)
- [Git](https://git-scm.com/downloads)
- [Powershell 7+ (pwsh)](https://github.com/powershell/powershell) - For Windows users only.
   - **Important**: Ensure you can run `pwsh.exe` from a PowerShell command. If this fails, you likely need to upgrade PowerShell.
- [Powershell for Mac/Linux (pwsh)](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-macos?view=powershell-7.3)


1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
1. Run `azd init -t azure-search-openai-demo`
1. Run `azd env refresh -e {environment name}` - Note that they will need the azd environment name, subscription Id, and location to run this command - you can find those values in your `./azure/{env name}/.env` file.  This will populate their azd environment's .env file with all the settings needed to run the app locally.
1. Run `pwsh ./scripts/roles.ps1` - This will assign all of the necessary roles to the user so they can run the app locally.  If they do not have the necessary permission to create roles in the subscription, then you may need to run this script for them. Just be sure to set the `AZURE_PRINCIPAL_ID` environment variable in the azd .env file or in the active shell to their Azure Id, which they can get with `az account show`.
2. az ad signed-in user show


>NOTE: Your Azure Account must have `Microsoft.Authorization/roleAssignments/write` permissions, such as [User Access Administrator](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) or [Owner](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner).  
