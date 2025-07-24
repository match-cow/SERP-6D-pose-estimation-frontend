import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests
import json
import numpy as np
import cv2
import zipfile

# Use the commented code below if running in a headless environment.
# Ensure to run the code BEFORE importing trimesh and pyrender.

# import os
# os.environ["PYOPENGL_PLATFORM"] = "egl"

import pyrender
import trimesh

errorMsg = ", and come back to this page to run foundation pose"
_flag = _flag2 = True

if (
    "img" not in st.session_state
    or "img_height" not in st.session_state
    or "img_width" not in st.session_state
    or "filename" not in st.session_state
):
    st.error("Upload a RGB Image" + errorMsg)
    _flag = _flag2 = False
if "depthMap" not in st.session_state:
    st.error("Upload a depth map" + errorMsg)
    _flag = _flag2 = False
if "roi" not in st.session_state:
    st.error("Upload a mask" + errorMsg)
    _flag = False
if "mesh" not in st.session_state:
    st.error("Upload a 3D Object" + errorMsg)
    _flag = False
if "cam_json" not in st.session_state:
    st.error("Upload Camera Intrinsics" + errorMsg)
    _flag = False

if _flag2 and (len(st.session_state.img) != len(st.session_state.depthMap)):
    st.error("Number of RBG images must be the same as number of depth maps")
    _flag = False

if _flag:
    K = st.session_state.cam_json[
        "intrinsics"
    ]  # e.g., [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
    depth_scale = st.session_state.cam_json[
        "depthscale"
    ]  # e.g., if depth is in mm, scale to meters

    buffered_roi = BytesIO()
    st.session_state.roi.save(buffered_roi, format="PNG")
    roi_base64 = base64.b64encode(buffered_roi.getvalue()).decode("utf-8")
    roi_array = np.frombuffer(base64.b64decode(roi_base64), np.uint8)
    roi_cv2 = cv2.imdecode(roi_array, cv2.IMREAD_GRAYSCALE)  # binary mask of object

    obj_base64 = base64.b64encode(st.session_state.mesh).decode("utf-8")
    mesh_bytes = st.session_state.mesh
    mesh_io = BytesIO(mesh_bytes)

    w, h = st.session_state.img_width, st.session_state.img_height

    img_cv2 = []
    overlays = {}
    images_json = []

    for i in range(len(st.session_state.img)):
        buffered_img = BytesIO()
        st.session_state.img[i].save(buffered_img, format="PNG")
        img_base64 = base64.b64encode(buffered_img.getvalue()).decode("utf-8")
        img_array = np.frombuffer(base64.b64decode(img_base64), np.uint8)
        img_cv2.append(
            cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        )  # each image is needed later on to make overlays; hence storing it in a list

        buffered_depth = BytesIO()
        st.session_state.depthMap[i].save(buffered_depth, format="PNG")
        depth_base64 = base64.b64encode(buffered_depth.getvalue()).decode("utf-8")

        images_json.append(
            {
                "filename": st.session_state.filename[i],
                "rgb": img_base64,
                "depth": depth_base64,
            }
        )  # creating a list of dictionaries to be passed in the request. Refer to request format
    request_dict = {
        "camera_matrix": K,
        "images": images_json,
        "mesh": obj_base64,
        "mask": roi_base64,
        "depthscale": depth_scale,
    }
    st.write("Request")
    st.json(request_dict, expanded=1)
    request = json.dumps(request_dict)

    url = "http://localhost:5000/foundationpose"

    try:
        response = requests.post(url, json=request)
    except:
        st.error("Failed to establish connection. Check URL and/or server status.")
    else:  # to avoid wrong error message if anything apart from request fails.
        if response.status_code == 200:  # 200 is success code
            response_json = response.json()
            st.write("Response")
            st.json(response_json, expanded=1)

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

            for i in range(len(img_cv2)):
                T = np.array(response_json["transformation_matrix"][i])
                # Extract rotation
                R = T[:3, :3]
                t = T[:3, 3].reshape(3, 1)

                transformed = (
                    np.array(
                        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]],
                        dtype=np.float32,
                    )
                    @ T
                )  # Transformation to account for axes negation

                world = np.eye(4)
                mesh_io.seek(0)
                trimesh_obj = trimesh.load(mesh_io, file_type="ply")
                mesh = pyrender.Mesh.from_trimesh(trimesh_obj)  # Required step

                # === Load 3D mesh ===
                trimesh_obj.apply_scale(0.001)
                mesh = pyrender.Mesh.from_trimesh(trimesh_obj, smooth=False)

                # === Scene Setup ===
                scene = pyrender.Scene(
                    bg_color=[0, 0, 0, 0], ambient_light=[0.3, 0.3, 0.3]
                )
                scene.add(camera, pose=world)
                scene.add(mesh, pose=transformed)
                camera = pyrender.IntrinsicsCamera(
                    fx, fy, cx, cy, znear=0.001, zfar=10.0
                )

                light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
                scene.add(light, pose=transformed)

                # === Render Offscreen ===
                r = pyrender.OffscreenRenderer(viewport_width=w, viewport_height=h)
                color, depth = r.render(scene)
                r.delete()

                # === Load background RGB image
                bg = img_cv2[i]
                bg = cv2.resize(bg, (w, h))
                bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

                # === Create mask from depth (where model is visible)
                mask = depth > 0

                # === Composite model onto background
                composite = bg.copy()
                composite[mask] = color[mask]

                # === Save result
                overlay = draw_axes_on_image(composite, K, R, t)

                st.image(overlay)
                filename = st.session_state.filename[i]
                try:
                    success, buffer = cv2.imencode(
                        ".png", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
                    )  # converting cv2 image to png
                    if success:
                        img_bytes = buffer.tobytes()  # storing png bytes
                        overlays[filename + ".png"] = img_bytes
                except:
                    st.error(
                        "An error occured while tring to convert the overlay for "
                        + filename
                        + " to an image"
                    )

            buffer = BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
                for name, file in overlays.items():
                    zip.writestr(name, file)
            buffer.seek(0)

            st.download_button(
                label="Download Poses",
                data=buffer,
                file_name="poses.zip",
                mime="application/zip",
                icon=":material/download:",
            )

        else:
            st.error("Error! JSON Responsde Code: " + str(response.status_code))
