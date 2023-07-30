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


def plot_annotated_image(
    input_image_path, bounding_box, dpi=250, page_height=15, page_width=5
):
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt

    image = cv2.imread(input_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boundingBox = bounding_box
    new_bounding_box_values = [val * dpi for val in boundingBox]
    pts = np.array(new_bounding_box_values, np.int32).reshape((-1, 1, 2))
    image = cv2.polylines(image, [pts], True, (255, 0, 0), 10)
    plt.figure(figsize=(page_width, page_height))
    plt.imshow(image)
    plt.axis("off")
    plt.show()


def save_annotated_image(
    input_image_path,
    bounding_box,
    output_path,
    dpi=250,
    page_height=5,
    page_width=5,
):
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt

    print("input_image_path: ", input_image_path)
    print("Saving annotated image to: ", output_path)

    image = cv2.imread(input_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boundingBox = bounding_box
    new_bounding_box_values = [val * dpi for val in boundingBox]
    pts = np.array(new_bounding_box_values, np.int32).reshape((-1, 1, 2))
    image = cv2.polylines(image, [pts], True, (255, 0, 0), 5)
    plt.figure(figsize=(page_width, page_height))
    plt.imshow(image)
    plt.axis("off")
    plt.savefig(output_path)
