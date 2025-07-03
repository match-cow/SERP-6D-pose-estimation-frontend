import streamlit as st
from PIL import Image


@st.cache_data
def displayImage(img):
    st.image(img)


st.header("Upload Depth Map")
with st.container(key="upload", border=True):
    uploaded_file = st.file_uploader("Upload a Depth Map", type=["png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.depthMap = image
        st.image(
            st.session_state.depthMap.convert("RGB")
        )  # Converting to RGB because Streamlit cannot display greyscale images
    if st.button("Continue"):
        if uploaded_file:
            st.switch_page(st.session_state.roi_pg)
        else:
            st.error("Please select a depth map to proceed")
