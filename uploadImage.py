import streamlit as st
from PIL import Image

@st.cache_data
def displayImage(img):
    st.image(img)

with st.container(key = 'upload', border = True):
    uploaded_file = st.file_uploader("Upload an image to get started", type=["png"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGBA")
        st.session_state.img = image
        st.image(st.session_state.img)
        st.session_state.img_width, st.session_state.img_height = image.size
        st.session_state.filename = uploaded_file.name

    if st.button("Continue"):
        if uploaded_file:
            st.switch_page(st.session_state.depthUpload_pg)
        else:
            st.error('Please select an image to proceed')
        pass