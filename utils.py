def get_azure_env_var():
    """
    Get the Azure environment variables from the .env file
    """
    import subprocess

    # Run the "azd env get-values" command
    result = subprocess.run(
        ["azd", "env", "get-values"], capture_output=True, text=True
    )

    # Get the environment variables from the command output
    env_vars = {}
    for line in result.stdout.splitlines():
        key, value = line.split("=", 1)
        env_vars[key] = value

    return env_vars
