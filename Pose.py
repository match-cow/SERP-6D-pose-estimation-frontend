import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests
import json

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




# buffered_img = BytesIO()
# st.session_state.img.save(buffered_img, format = 'PNG')
# img_base64 = base64.b64encode(buffered_img.getvalue()).decode('utf-8')
