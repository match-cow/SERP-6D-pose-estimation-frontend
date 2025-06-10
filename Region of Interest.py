# import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

# import numpy as np

# st.set_page_config(layout="wide")
# st.image(st.session_state.img, caption="Uploaded Image")

# Specify canvas parameters in application
st.header('Upload a region of interest or draw one')

with st.container(key = 'upload', border = True):
    uploaded_file = st.file_uploader("Upload a Region of Interest", type=["png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.roi = image
        st.image(st.session_state.roi)

    if st.button("Continue with uploaded ROI"):
        if uploaded_file:
            st.switch_page(st.session_state.cam_pg)
        else:
            st.error('Please select an image to proceed')
        pass

with st.container(key = 'draw', border = True):
    st.write('Draw Region of interest.')
    st.write('Scroll down to see the overlay on actual image and mask.')
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform")
    )

    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == 'point':
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
    # stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    # bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
        
    # Create a canvas component
    canvas_result = st_canvas(
        fill_color = "rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width = stroke_width,
        stroke_color = '#FFFFFF',
        # background_color = bg_color,
        background_color = None,
        update_streamlit = True,
        width = st.session_state.img_width,
        height = st.session_state.img_height,
        drawing_mode = drawing_mode,
        point_display_radius = point_display_radius if drawing_mode == 'point' else 0,
        key="canvas"
    )

    # # Do something interesting with the image data and paths
    # if canvas_result.image_data is not None:
    #     st.image(canvas_result.image_data)
    # if canvas_result.json_data is not None:
    #     objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
    #     for col in objects.select_dtypes(include=['object']).columns:
    #         objects[col] = objects[col].astype("str")
    #     st.dataframe(objects)
    # END OF OLD CODE

    # NEW CODE
    # Load background image
    # bg_image = Image.open("Z:\\dummy\\SERP-6D-pose-estimation-frontend\\test images\\Sample-images-from-the-Robot-Scenario-data-collection.png").convert("RGBA")
    # img_width, img_height = bg_image.size

    # Display the background image
    # st.image(bg_image, caption="Background Image", use_column_width=False)

    # Create a transparent canvas
    # canvas_result = st_canvas(
    #     fill_color = "rgba(255, 165, 0, 0.3)",
    #     stroke_width = 3,
    #     stroke_color="#FF0000",
    #     background_color=None,
    #     update_streamlit=True,
    #     height=st.session_state.img_height,
    #     width=st.session_state.img_width,
    #     drawing_mode="freedraw",  # You can switch to 'rect', 'circle', etc.
    #     key="canvas_no_bg"
    # )

    # Merge the drawing with the background
    if canvas_result.image_data is not None:
        drawn_image = Image.fromarray((canvas_result.image_data).astype("uint8")).convert("RGBA")

        # Composite drawing over original image
        final = Image.alpha_composite(st.session_state.img, drawn_image)
        st.image(final)

    if canvas_result.image_data is not None:
            #bw_image = Image.fromarray((canvas_result.image_data).astype("uint8")).convert('RGBA')
            bw_bg = Image.new("RGBA", (st.session_state.img_width, st.session_state.img_height), (0, 0, 0)).convert('RGBA')

            # Composite drawing over original image
            final_bw = Image.alpha_composite(bw_bg, drawn_image)
            st.image(final_bw)

            if final_bw:
                st.session_state.roi = final_bw.convert('L')

            if st.button("Continue with custom ROI"):
                st.switch_page(st.session_state.cam_pg)

    buffer = BytesIO()
    final_bw.save(buffer, format="PNG")
    buffer.seek(0)  # Rewind to start so Streamlit can read it

    st.download_button(
    label="Download Mask",
    data=buffer,
    file_name="mask.png",
    mime="image/png",
    icon=":material/download:",
    )