import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests
import json
import numpy as np
import cv2

# import os
# os.environ["PYOPENGL_PLATFORM"] = "egl"
import pyrender
import trimesh

buffered_img = BytesIO()
st.session_state.img.save(buffered_img, format = 'PNG')
img_base64 = base64.b64encode(buffered_img.getvalue()).decode('utf-8')
img_array = np.frombuffer(base64.b64decode(img_base64), np.uint8)
img_cv2 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # shape: (H, W, 3)
w, h = st.session_state.img_width, st.session_state.img_height

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

obj_base64 = base64.b64encode(st.session_state.mesh).decode('utf-8')
mesh_bytes = st.session_state.mesh
mesh_io = BytesIO(mesh_bytes)

# Camera intrinsics
K = st.session_state.cam_json["intrinsics"]  # e.g., [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
depth_scale = st.session_state.cam_json["depthscale"]  # e.g., if depth is in mm, scale to meters


st.write(len(img_base64))
st.write(len(depth_base64))
st.write(len(roi_base64))
st.write(len(obj_base64))

request_dict = {
    "camera_matrix": K,
    "images": [
        {
        "filename": st.session_state.filename,
        "rgb": img_base64,
        "depth": depth_base64
        }
    ],
    "mesh": obj_base64,
    "mask": roi_base64,
    "depthscale": depth_scale
}

request = json.dumps(request_dict)

url = "http://localhost:5000/pose/estimate"

#response = requests.post(url, json = request)
#st.write(response.status_code)
#if response.status_code:
if True:
    #response_json = response.json()
    #st.write(response_json)

    # Camera intrinsics
    K = np.array(K)

    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    camera = pyrender.IntrinsicsCamera(fx=fx, fy=fy, cx=cx, cy=cy)

    # FUNCTIONS
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

    trimesh_obj = trimesh.load(mesh_io, file_type = 'ply')
    mesh = pyrender.Mesh.from_trimesh(trimesh_obj)  # Required step

    #T = np.array(response_json["transformation_matrix"])
    T = np.array([
    [6.441221833229064941e-01, 7.646285891532897949e-01, -2.120633423328399658e-02, 1.071708276867866516e-03],  
    [6.352801322937011719e-01, -5.501901507377624512e-01, -5.419494509696960449e-01, -1.981154456734657288e-02],  
    [-4.260576665401458740e-01, 3.356097936630249023e-01, -8.401432633399963379e-01, 5.749665498733520508e-01],
    [0.0, 0.0, 0.0, 1.0]
        ])  
    # Extract pose
    R = T[:3, :3]
    t = T[:3, 3].reshape(3, 1)

    # 2D Overlay
    transformed = np.array([
        [1,  0,  0, 0],
        [0, -1,  0, 0],
        [0,  0, -1, 0],
        [0,  0,  0, 1]
    ], dtype=np.float32) @ T

    world = np.eye(4)

    # === Load 3D mesh ===
    trimesh_obj.apply_scale(0.001)
    mesh = pyrender.Mesh.from_trimesh(trimesh_obj, smooth=False)

    # === Scene Setup ===
    scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.3, 0.3, 0.3])
    scene.add(camera, pose=world)
    scene.add(mesh, pose=transformed)
    camera = pyrender.IntrinsicsCamera(fx,fy,cx,cy, znear=0.001, zfar=10.0)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
    scene.add(light, pose=transformed)

    # === Render Offscreen ===
    r = pyrender.OffscreenRenderer(viewport_width=w, viewport_height=h)
    color, depth = r.render(scene)
    r.delete()

    # === Load background RGB image
    bg = img_cv2
    bg = cv2.resize(bg, (w, h))
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

    # === Create mask from depth (where model is visible)
    mask = (depth > 0)

    # === Composite model onto background
    composite = bg.copy()
    composite[mask] = color[mask]

    # === Save result
    overlay = draw_axes_on_image(composite, K, R, t)

    #st.image(cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    st.image(overlay, cv2.COLOR_RGB2BGR)

else:
    st.error("Error! JSON Responsde Code: "+str(response.status_code))