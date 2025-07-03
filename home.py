import streamlit as st

st.set_page_config(layout="wide")

st.title("Intuitive 6D Pose Estimation")

if "imgUpload_pg" not in st.session_state:
    st.session_state.imgUpload_pg = st.Page(
        "uploadImage.py", icon=":material/add_photo_alternate:"
    )

if "depthUpload_pg" not in st.session_state:
    st.session_state.depthUpload_pg = st.Page(
        "uploadDepthMap.py", icon=":material/gradient:"
    )

if "roi_pg" not in st.session_state:
    st.session_state.roi_pg = st.Page(
        "regionOfInterest.py", icon=":material/lasso_select:"
    )

if "obj_pg" not in st.session_state:
    st.session_state.obj_pg = st.Page("upload3D.py", icon=":material/deployed_code:")

if "cam_pg" not in st.session_state:
    st.session_state.cam_pg = st.Page(
        "cameraIntrinsics.py", icon=":material/photo_camera:"
    )

if "pose_pg" not in st.session_state:
    st.session_state.pose_pg = st.Page("pose.py", icon=":material/terminal:")

# List should be in order of navigation
pg = st.navigation(
    [
        st.session_state.imgUpload_pg,
        st.session_state.depthUpload_pg,
        st.session_state.roi_pg,
        st.session_state.obj_pg,
        st.session_state.cam_pg,
        st.session_state.pose_pg,
    ]
)
pg.run()
