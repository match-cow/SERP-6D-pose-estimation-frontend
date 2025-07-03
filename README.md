# Intuituve 6D Pose Estimation Frontend 🚀

This application provides a user-friendly frontend for 6D pose estimation models, starting with FoundationPose. It offers a simplified interface to interact with a pose estimation API, visualize the results, and download the output. The frontend is built using Streamlit.

## ✨ Features

* **Intuitive Workflow:** Guides users through the pose estimation process step-by-step.
* **Flexible Input Methods:** Supports various ways to upload images, 3D models, and camera intrinsics.
* **Custom Masking:** Allows users to upload an existing mask or draw a Region of Interest (ROI) directly on the image.
* **Real-time Visualization:** Displays the 6D pose of the object rendered directly on the input image.
* **Downloadable Results:** Enables users to download the generated pose-estimated image.
* **Built with Streamlit:** Leverages Streamlit for a fast and interactive user experience.

## ⚙️ Setup

To get started with the application, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/SERP-6D-pose-estimation-frontend.git](https://github.com/yourusername/SERP-6D-pose-estimation-frontend.git)
    cd SERP-6D-pose-estimation-frontend
    ```
2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

**Note on Streamlit Version:**
Upgrading Streamlit to versions above `1.40.0` will currently break the canvas component, which affects the custom mask drawing feature. If using a newer Streamlit version is necessary, please modify `regionOfInterest.py` by removing all code after line 22.

## 🚀 Application Flow

The application guides the user through the following steps to perform 6D pose estimation:

1.  **Upload RGB Image:** The user uploads a **PNG** format RGB image.
2.  **Upload Depth Map:** The user uploads a **PNG** format greyscale depth map.
3.  **Region of Interest (ROI):** The user can choose to either:
    * Upload an existing mask image.
    * Draw a custom mask directly over the uploaded RGB image using the provided drawing tools.
4.  **Upload 3D Model:** The user uploads the 3D model of the object in **PLY** format.
5.  **Camera Intrinsics:** The user has three convenient options for inputting camera intrinsic parameters:
    * Upload a JSON file (see format below).
    * Upload two separate text files: one containing the camera matrix and another with the depth scale.
    * Manually type the intrinsic values into the provided fields.
    Regardless of the input method, the user can review and modify the intrinsics and view an updated JSON representation before proceeding.
6.  **Pose Estimation:** The application sends a request to the backend API with all the provided data and images to run FoundationPose.
7.  **Display Results:** If the request is successful, an image displaying the 6D pose of the object (rendered on the input image) will be shown. The user can then download this generated image.

## 📄 JSON Formats

### 1. Camera Intrinsics JSON

This JSON structure is used for uploading camera intrinsic parameters.

```json
{
    "intrinsics": [
        ["val1", "val2", "val3"],
        ["val4", "val5", "val6"],
        ["val7", "val8", "val9"]
    ],
    "depthscale": "float"
}
```
- ```intrinsics```: A 3x3 matrix representing the camera's intrinsic parameters. Each inner array represents a row of the matrix. For example, a typical camera intrinsic matrix K is structured as:

- ```depthscale```: A float value representing the depth scale. This is a multiplier to convert raw depth sensor values into real-world units (e.g., meters or millimeters).

### 2. Request Payload JSON

This JSON structure is sent to the pose estimation API.
```JSON

{
    "camera_matrix": [
        ["val1", "val2", "val3"],
        ["val4", "val5", "val6"],
        ["val7", "val8", "val9"]
    ],
    "images": [
        {
            "filename": "string",
            "rgb": "base64 encoded rgb image",
            "depth": "base64 encoded depth map"
        }
    ],
    "mesh": "base64 encoded mesh",
    "mask": "base64 encoded mask",
    "depthscale": "float"
}
```
- ```camera_matrix```: A 3x3 matrix (same format as described above for intrinsics) representing the camera's intrinsic parameters for the image being processed.

- ```images```: An array containing image data.

    - ```filename```: The original filename of the image.

    - ```rgb```: Base64 encoded string of the RGB image.

    - ```depth```: Base64 encoded string of the depth map.

- ```mesh```: Base64 encoded string of the 3D object model (PLY format).

- ```mask```: Base64 encoded string of the Region of Interest mask.

- ```depthscale```: A float value representing the depth scale.

##  📄 License

This project is licensed under the MIT License.

### Developed by: [Alaqmar Bohori]