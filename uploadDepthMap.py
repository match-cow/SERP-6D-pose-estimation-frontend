import streamlit as st
from PIL import Image


@st.cache_data
def displayImage(img):
    st.image(img)


st.header("Upload Depth Map")

with st.container(key="upload", border=True):
    uploaded_files = st.file_uploader(
        "Upload a Depth Map", type=["png"], accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.depthMap = []
        display = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.session_state.depthMap.append(image)
            display.append(
                image.convert("RGB")
            )  # Converting to RGB because Streamlit cannot display greyscale images
        st.image(display)

    if st.button("Continue"):
        if uploaded_files:
            if len(st.session_state.depthMap) == len(st.session_state.img):
                st.switch_page(st.session_state.roi_pg)
            else:
                st.error(
                    "Number of RBG images must be the same as number of depth maps"
                )
        else:
            st.error("Please select a depth map to proceed")
