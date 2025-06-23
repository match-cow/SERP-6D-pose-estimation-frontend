import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

buffered_img = BytesIO()
st.session_state.img.save(buffered_img, format = 'PNG')
img_base64 = base64.b64encode(buffered_img.getvalue()).decode('utf-8')
img_array = np.frombuffer(base64.b64decode(img_base64), np.uint8)
img_cv2 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # shape: (H, W, 3)

buffered_depth = BytesIO()
st.session_state.depthMap.save(buffered_depth, format = 'PNG')
depth_base64 = base64.b64encode(buffered_depth.getvalue()).decode('utf-8')
depth_array = np.frombuffer(base64.b64decode(depth_base64), np.uint8)
depth_cv2 = cv2.imdecode(depth_array, cv2.IMREAD_UNCHANGED)  # shape: (H, W), in depth units

buffered_roi = BytesIO()
st.session_state.roi.save(buffered_roi, format = 'PNG')
roi_base64 = base64.b64encode(buffered_roi.getvalue()).decode('utf-8')
roi_array = np.frombuffer(base64.b64decode(roi_base64), np.uint8)
roi_cv2 = cv2.imdecode(roi_array, cv2.IMREAD_GRAYSCALE)  # binary mask of object

# Camera intrinsics
K = st.session_state.cam_json["intrinsics"]  # e.g., [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
depth_scale = st.session_state.cam_json["depthscale"]  # e.g., if depth is in mm, scale to meters


st.write(len(img_base64))
st.write(len(depth_base64))
st.write(len(roi_base64))

request_dict = {
    "request_summary": {
        "camera_matrix": K,
        "images_count": 1
    },
    "full_request_data": {
        "camera_matrix": K,
        "images": {
            "rgb": [
                img_base64
            ],
            "depth_map": [
                depth_base64
            ],
            "region_of_interest": [
                roi_base64
            ]
        },
        "depthscale": depth_scale
    }
}

request = json.dumps(request_dict)

url = "localhost:5000/pose/estimate"

response = requests.post(url, json = request)
#st.write(response.status_code)
if response.status_code == 200:
    st.write(response.json())

    # Add this to if condition later once API is ready
    # Pose matrix (4x4) from FoundationPose or similar
    K = np.array(K)
    T = np.array([
        [6.441221833229064941e-01, 7.646285891532897949e-01, -2.120633423328399658e-02, 1.071708276867866516e-03],  
        [6.352801322937011719e-01, -5.501901507377624512e-01, -5.419494509696960449e-01, -1.981154456734657288e-02],  
        [-4.260576665401458740e-01, 3.356097936630249023e-01, -8.401432633399963379e-01, 5.749665498733520508e-01],
        [0.0, 0.0, 0.0, 1.0]
    ])  # Example: replace with your output

    # -----------------------------
    # FUNCTIONS
    # -----------------------------

    def get_3d_points_from_mask(depth_map, mask, K, depth_scale):
        fx, fy = K[0, 0], K[1, 1]
        cx, cy = K[0, 2], K[1, 2]

        ys, xs = np.where(mask > 0)
        zs = depth_map[ys, xs] * depth_scale

        xs_cam = (xs - cx) * zs / fx 
        ys_cam = (ys - cy) * zs / fy

        points_3d = np.stack((xs_cam, ys_cam, zs), axis=-1)
        return points_3d

    def project_point(point, K):
        x, y, z = point
        u = (K[0, 0] * x / z) + K[0, 2]
        v = (K[1, 1] * y / z) + K[1, 2]
        return int(round(u)), int(round(v))

    def draw_axes_on_image(image, K, R, t, axis_len=0.1):
        img = image.copy()
        origin = t.flatten()

        axes = [origin + R[:, i] * axis_len for i in range(3)]  # X, Y, Z
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # BGR
        origin_2d = project_point(origin, K)

        for pt, color in zip(axes, colors):
            pt_2d = project_point(pt, K)
            cv2.line(img, origin_2d, pt_2d, color, 2)
        
        return img

    def draw_axes_3d(ax, R, t, scale=0.1):
        origin = t.flatten()
        x_axis = R[:, 0] * scale
        y_axis = R[:, 1] * scale
        z_axis = R[:, 2] * scale

        ax.quiver(*origin, *x_axis, color='r', label='X')
        ax.quiver(*origin, *y_axis, color='g', label='Y')
        ax.quiver(*origin, *z_axis, color='b', label='Z')

    # -----------------------------
    # MAIN VISUALIZATION
    # -----------------------------

    # Extract pose
    #R = np.linalg.inv(T[:3, :3])
    R = T[:3, :3]
    t = T[:3, 3].reshape(3, 1)

    print(R)
    # 2D Overlay
    overlay = draw_axes_on_image(img_cv2, K, R, t)

    # 3D Visualization
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(121, projection='3d')

    # Plot object points from depth
    points_3d = get_3d_points_from_mask(depth_cv2, roi_cv2, K, depth_scale)
    ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2], s=0.5, c='gray', alpha=0.3)

    # Plot pose axes
    draw_axes_3d(ax, R, t)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("3D Pose Visualization")
    ax.view_init(elev=30, azim=45)

    # 2D overlay
    ax2 = fig.add_subplot(122)
    ax2.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    ax2.set_title("2D Pose Overlay")
    ax2.axis("off")

    plt.tight_layout()
    #st.write(plt.show())
    #plt.show()
    st.pyplot(fig)
else:
    st.error("Error! JSON Responsde Code: "+str(response.status_code))