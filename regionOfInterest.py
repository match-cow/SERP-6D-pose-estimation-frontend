import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

st.header("Upload a region of interest or draw one")

with st.container(key="upload", border=True):
    uploaded_file = st.file_uploader("Upload a Region of Interest", type=["png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.roi = image
        st.image(st.session_state.roi)

    if st.button("Continue with uploaded ROI"):
        if uploaded_file:
            st.switch_page(st.session_state.obj_pg)
        else:
            st.error("Please select an image to proceed")

with st.container(key="draw", border=True):
    st.write("Draw Region of interest using tools on the sidebar")
    st.write("Scroll down to see the mask")
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform")
    )  # default drawimg mode

    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)  # default stroke width
    if drawing_mode == "point":
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)

    bg_image = st.session_state.img
    final_bw = Image.new(
        "RGBA", (st.session_state.img_width, st.session_state.img_height), (0, 0, 0)
    ).convert(
        "RGBA"
    )  # creating dummy bw image to avoid buffering error

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color="#FFFFFF",  # Fixing stroke color to white, and not allowing user to change color
        background_color="#000000",  # Fixing background color to black and not allowing user to change color
        background_image=bg_image,
        update_streamlit=True,  # Fixing "update_streamlit" to True. Provides realtime update of the drawing
        width=st.session_state.img_width,
        height=st.session_state.img_height,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        key="canvas",
    )

    if canvas_result.image_data is not None:
        drawn_image = Image.fromarray(
            (canvas_result.image_data).astype("uint8")
        ).convert("RGBA")

        bw_bg = Image.new(
            "RGBA", (st.session_state.img_width, st.session_state.img_height), (0, 0, 0)
        ).convert("RGBA")
        final_bw = Image.alpha_composite(
            bw_bg, drawn_image
        )  # Overlapping the mask on a black background
        st.image(final_bw)

        if final_bw:
            st.session_state.roi = final_bw.convert(
                "L"
            )  # Converting to greyscale, required by API

        if st.button("Continue with custom ROI"):
            st.switch_page(st.session_state.obj_pg)

    buffer = BytesIO()
    final_bw.save(
        buffer, format="PNG"
    )  # Provisional file creation, if user wishes to download
    buffer.seek(0)

    st.download_button(
        label="Download Mask",
        data=buffer,
        file_name="mask.png",
        mime="image/png",
        icon=":material/download:",
    )
