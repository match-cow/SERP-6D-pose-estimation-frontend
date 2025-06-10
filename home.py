import streamlit as st

st.set_page_config(layout="wide")

st.title("Intuitive 6D Pose Estimation")

if 'imgUpload_pg' not in st.session_state:
   st.session_state.imgUpload_pg = st.Page("Upload Image.py", icon = ':material/arrow_upload_progress:')

if 'depthUpload_pg' not in st.session_state:
   st.session_state.depthUpload_pg = st.Page("Upload Depth Map.py", icon = ':material/arrow_upload_ready:')

if 'roi_pg' not in st.session_state:
   st.session_state.roi_pg = st.Page("Region of Interest.py", icon = ':material/lasso_select:')

if 'cam_pg' not in st.session_state:
   st.session_state.cam_pg = st.Page("Camera Intrinsics.py", icon = ':material/photo_camera:')

if 'pose_pg' not in st.session_state:
   st.session_state.pose_pg = st.Page("Pose.py", icon = ':material/terminal:')

pg = st.navigation([st.session_state.imgUpload_pg, 
                    st.session_state.depthUpload_pg, 
                    st.session_state.roi_pg, 
                    st.session_state.cam_pg,
                    st.session_state.pose_pg])
pg.run()
# test comment