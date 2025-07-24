import streamlit as st
from PIL import Image


# check caching options on streamlit docs
@st.cache_data
def displayImage(img):
    st.image(img)


st.header("Upload RGB Image")

with st.container(key="upload", border=True):
    uploaded_files = st.file_uploader("Upload an image to get started", type=["png"], accept_multiple_files = True)

    if uploaded_files:
        st.session_state.img = []
        st.session_state.filename = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file).convert("RGBA")
            st.session_state.img.append(image)
            st.session_state.filename.append(uploaded_file.name.split(".")[0])
        st.session_state.img_width, st.session_state.img_height = st.session_state.img[0].size
        st.image(st.session_state.img)
        

    if st.button("Continue"):
        if uploaded_files:
            st.switch_page(st.session_state.depthUpload_pg)
        else:
            st.error("Please select an image to proceed")


# with st.container(key="upload", border=True):
#     uploaded_files = st.file_uploader("Upload an image to get started", type=["png"], )

#     if uploaded_file:
#         image = Image.open(uploaded_file).convert("RGBA")
#         st.session_state.img = image
#         st.image(st.session_state.img)
#         st.session_state.img_width, st.session_state.img_height = image.size
#         st.session_state.filename = uploaded_file.name.split(".")[0]

#     if st.button("Continue"):
#         if uploaded_file:
#             st.switch_page(st.session_state.depthUpload_pg)
#         else:
#             st.error("Please select an image to proceed")
