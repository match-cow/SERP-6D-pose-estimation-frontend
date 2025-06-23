import streamlit as st
import json

r1col1, r1col2 = st.columns(2, gap = "medium", border = True)
r2col1, r2col2 = st.columns(2, gap = "medium", border = True)

depthscale_val = 0
intrinsics_val = [[0,0,0],[0,0,0],[0,0,0]]

def update_json():
    intrinsics_val = nums.copy()
    #depthscale_val = depthscale_val_tb



with r1col1:
    st.header('Use JSON')
    st.json({
        'intrinsics' : [['val1', 'val2', 'val3'], ['val4', 'val5', 'val6'], ['val7', 'val8', 'val9']],
        'depthscale' : 'float'
    }, expanded = 1)

    cam_data = st.file_uploader("Upload a JSON in the above format", type = ['json'])

    if cam_data:
        json_str = cam_data.read().decode("utf-8")

        try:
            data = json.loads(json_str)  # Parse JSON
        
            # st.success("JSON loaded successfully!")
        
            # Display key-value pairs in text inputs
            # If nested JSON, you might want to flatten it or handle differently
            if isinstance(data, dict):
                intrinsics_val = data['intrinsics'].copy()
                depthscale_val = data['depthscale']
                # flag = True
                # for key, value in data.items():
                #     if flag:
                #         intrinsics_val = value.copy()
                #         print('intrinsics: ', intrinsics_val)
                #         print('og:', value)
                #         flag = False
                #     else:
                #         depthscale_val = value
            else:
                st.error("JSON root is not a dictionary.")
        except json.JSONDecodeError:
            st.error("Uploaded file is not valid JSON.")

with r1col2:
    st.header('Use Text Files')

    intrinsics_upload = st.file_uploader("Upload a text file with the intrinsic data", type = ['txt'])
    depthscale_upload = st.file_uploader("Upload a text file with the depth scale", type = ['txt'])

    if intrinsics_upload:
        intrinsics_str = intrinsics_upload.read().decode("utf-8").split()
        intrinsics_val = [[], [], []]
        for i in range(0,9):
            if i < 3:
                intrinsics_val[0].append(float(intrinsics_str[i]))
            elif i < 6:
                intrinsics_val[1].append(float(intrinsics_str[i]))
            elif i < 9:
                intrinsics_val[2].append(float(intrinsics_str[i]))

    
    if depthscale_upload:
        depthscale_val = depthscale_upload.read().decode("utf-8")

with r2col2:
    st.header('Edit Values')
    scol1, scol2, scol3 = st.columns(3)
    # no_of_columns = len(intrinsics_val)
    # scols = st.columns(no_of_columns)
    nums = intrinsics_val.copy()

    # for i in range(0, no_of_columns):
    #     nums.append([])

    # for i in scols:
    #     for j in 
    #     nums.append(st.number_input(value='p'+str(scols.index(i)), key='p'+str(scols.index(i))', on_change=None,  placeholder='Enter value for p1', label_visibility="collapsed"))

    with scol1:
        for i in range(0,3):
            nums[i][0] = st.number_input(label = 'p'+str(i*3 + 1), value=float(intrinsics_val[i][0]), key='p'+str(i*3 + 1), on_change=update_json,  placeholder='Enter value for p'+str(i*3 + 1), format="%0.5f")

    with scol2:
        for i in range(0,3):
            nums[i][1] = st.number_input(label = 'p'+str(i*3 + 2), value=float(intrinsics_val[i][1]), key='p'+str(i*3 + 2), on_change=update_json,  placeholder='Enter value for p'+str(i*3 + 2), format="%0.5f")

    with scol3:
        for i in range(0,3):
            nums[i][2] = st.number_input(label = 'p'+str(i*3 + 3), value=float(intrinsics_val[i][2]), key='p'+str(i*3 + 3), on_change=update_json,  placeholder='Enter value for p'+str(i*3 + 3), format="%0.5f")

    depthscale_val = st.number_input(label = 'Depth Scale', value=float(depthscale_val), key='depth', on_change=update_json,  placeholder='Enter value for depthscale', format = "%0.5f")


with r2col1:
    st.session_state.cam_json = {"intrinsics": intrinsics_val.copy(), "depthscale": depthscale_val}
    st.header('Final JSON')
    st.json(st.session_state.cam_json)
    st.session_state.intrinsics = intrinsics_val.copy()

if st.button("Run Foundation Pose"):
    st.switch_page(st.session_state.pose_pg)