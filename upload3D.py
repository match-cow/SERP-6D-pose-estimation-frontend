import streamlit as st
import tempfile
import open3d as o3d
@st.cache_data
def displayImage(img):
    st.image(img)

with st.container(key = 'upload', border = True):
    uploaded_file = st.file_uploader("Upload a 3D file", type=["ply"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ply') as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_file_path = tmp_file.name

        mesh = o3d.io.read_triangle_mesh(temp_file_path)
        mesh.compute_vertex_normals()

        st.session_state.mesh = mesh

        st.write(f"Loaded mesh: `{st.session_state.filename}`")
        st.write(f"- Vertices: {len(mesh.vertices)}")
        st.write(f"- Triangles: {len(mesh.triangles)}")

        # Optional: render mesh as image (Open3D supports offscreen rendering)
        st.info("3D preview is not shown here — use the next page to render or analyze the mesh.")

    if st.button("Continue"):
        if uploaded_file:
            st.switch_page(st.session_state.cam_pg)
        else:
            st.error('Please select a 3D file to proceed')
        pass