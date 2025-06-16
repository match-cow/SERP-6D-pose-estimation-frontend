import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests
import json
import numpy as np
import plotly.graph_objects as go
import csv

buffered_img = BytesIO()
st.session_state.img.save(buffered_img, format = 'PNG')
img_base64 = base64.b64encode(buffered_img.getvalue()).decode('utf-8')
# st.write(img_base64)

buffered_depth = BytesIO()
# st.session_state.depthMap.convert('L').save(buffered_depth, format = 'PNG')
st.session_state.depthMap.save(buffered_depth, format = 'PNG')
depth_base64 = base64.b64encode(buffered_depth.getvalue()).decode('utf-8')

buffered_roi = BytesIO()
st.session_state.roi.save(buffered_roi, format = 'PNG')
roi_base64 = base64.b64encode(buffered_roi.getvalue()).decode('utf-8')

# st.write(depth_base64)

st.write(len(img_base64))
st.write(len(depth_base64))
st.write(len(roi_base64))

request_dict = {
    "request_summary": {
        "camera_matrix": st.session_state.cam_json["intrinsics"],
        "images_count": 1
    },
    "full_request_data": {
        "camera_matrix": st.session_state.cam_json["intrinsics"],
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
        "depthscale": st.session_state.cam_json["depthscale"]
    }
}

request = json.dumps(request_dict)

url = "http://api.open-notify.org/this-api-doesnt-exist"

response = requests.post(url, json = request)
st.write(response.status_code)
if response.status_code == 200:
    st.write(response.json())

# MOVE THIS INTO  STATUS_CODE == 200 EVENTUALLY
with open("C:\\SERP\\000049_ob_incam.txt", "r") as pose_file:
    data = csv.reader(pose_file, delimiter=' ')
    st.write(data)
# Your 4x4 transformation matrix (from pose estimation)
T = np.array([
    [ 0.64412218,  0.76462859, -0.02120633,  0.00107171],
    [ 0.63528013, -0.55019015, -0.54194945, -0.01981154],
    [-0.42605767,  0.33560979, -0.84014326,  0.57496655],
    [ 0.0,         0.0,         0.0,         1.0       ]
])

# Define a unit cube centered at origin
def get_unit_cube():
    return np.array([
        [-0.5, -0.5, -0.5],
        [ 0.5, -0.5, -0.5],
        [ 0.5,  0.5, -0.5],
        [-0.5,  0.5, -0.5],
        [-0.5, -0.5,  0.5],
        [ 0.5, -0.5,  0.5],
        [ 0.5,  0.5,  0.5],
        [-0.5,  0.5,  0.5]
    ])

# Transform cube using 4x4 pose matrix
def transform_cube(cube_pts, T):
    cube_hom = np.hstack((cube_pts, np.ones((len(cube_pts), 1))))  # (8, 4)
    transformed = (T @ cube_hom.T).T
    return transformed[:, :3]

# Cube faces (by vertex index)
faces = [
    [0, 1, 2, 3], [4, 5, 6, 7],
    [0, 1, 5, 4], [2, 3, 7, 6],
    [1, 2, 6, 5], [0, 3, 7, 4]
]

# Get cube and apply transformation
cube = get_unit_cube()
cube_transformed = transform_cube(cube, T)

# Create Plotly figure
fig = go.Figure()

# Draw cube faces
for face in faces:
    x = [cube_transformed[i][0] for i in face + [face[0]]]
    y = [cube_transformed[i][1] for i in face + [face[0]]]
    z = [cube_transformed[i][2] for i in face + [face[0]]]
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode='lines',
        line=dict(color='orange', width=4),
        showlegend=False
    ))

# Draw pose axes
origin = T[:3, 3]
R = T[:3, :3]
scale = 0.1
colors = ['red', 'green', 'blue']
for i in range(3):  # x, y, z axes
    axis_end = origin + R[:, i] * scale
    fig.add_trace(go.Scatter3d(
        x=[origin[0], axis_end[0]],
        y=[origin[1], axis_end[1]],
        z=[origin[2], axis_end[2]],
        mode='lines',
        line=dict(color=colors[i], width=6),
        name=f'{colors[i]}-axis'
    ))

# Layout
fig.update_layout(
    scene=dict(aspectmode='data'),
    title='Cube at Pose (Defined by 4×4 Matrix)',
    margin=dict(l=0, r=0, t=40, b=0),
)

# Show in Streamlit
st.plotly_chart(fig)




# buffered_img = BytesIO()
# st.session_state.img.save(buffered_img, format = 'PNG')
# img_base64 = base64.b64encode(buffered_img.getvalue()).decode('utf-8')
