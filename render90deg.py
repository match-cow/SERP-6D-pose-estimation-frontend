import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import open3d as o3d
import pyrender
import trimesh
from PIL import Image

rgb_image = cv2.imread("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/000049.png")  # shape: (H, W, 3)
depth_map = cv2.imread("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/000049_depth.png", cv2.IMREAD_UNCHANGED) # shape: (H, W), in depth units
#mesh = o3d.io.read_triangle_mesh("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/Ql4i.ply")
trimesh_obj = trimesh.load("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/Ql4i.ply")
mesh = pyrender.Mesh.from_trimesh(trimesh_obj)  # Required step
depth_scale = 1.0000000474974513  # e.g., if depth is in mm, scale to meters
h, w, _ = rgb_image.shape

# Camera intrinsics
K = np.array([
        [906.17822265625, 0.0, 646.2926635742188],
        [0.0, 905.9284057617188, 370.1160583496094],
        [0.0, 0.0, 1.0]
    ])

fx, fy = K[0, 0], K[1, 1]
cx, cy = K[0, 2], K[1, 2]

intrinsic = o3d.camera.PinholeCameraIntrinsic()
intrinsic.set_intrinsics(w, h, fx, fy, cx, cy)

print(w,h)

camera = pyrender.IntrinsicsCamera(fx=fx, fy=fy, cx=cx, cy=cy)

# Pose matrix (4x4) from FoundationPose or similar
T1 = np.array([
    [6.441221833229064941e-01, 7.646285891532897949e-01, -2.120633423328399658e-02, 1.071708276867866516e-03],  
    [6.352801322937011719e-01, -5.501901507377624512e-01, -5.419494509696960449e-01, -1.981154456734657288e-02],  
    [-4.260576665401458740e-01, 3.356097936630249023e-01, -8.401432633399963379e-01, 5.749665498733520508e-01],
    [0.0, 0.0, 0.0, 1.0]
])  

T2 = np.array([[2.486930836558349026e-02, 6.422343588964443128e-01, -7.661047318736831091e-01, 2.511898041037676638e-02],
    [5.410685421533254491e-01, 6.357471106215925039e-01, 5.505183146889540691e-01, -5.352716326496290145e-02],
    [8.406107137497964565e-01, -4.282062206720773645e-01, -3.316820883403773790e-01, 5.842868249282111570e-01],
    [0.0, 0.0, 0.0, 1.0]
])

# FUNCTIONS
def get_3d_points_from_mask(depth_map, mask, depth_scale):
    ys, xs = np.where(mask > 0)
    zs = depth_map[ys, xs] * depth_scale

    xs_cam = (xs - cx) * zs / fx 
    ys_cam = (ys - cy) * zs / fy

    points_3d = np.stack((xs_cam, ys_cam, zs), axis=-1)
    return points_3d

def project_point(point, K):
    x, y, z = point
    u = (K[0, 0] * x / z) + K[0, 2]
    v = (K[1, 1] * y / z) + K[1, 2]
    return int(round(u)), int(round(v))

def draw_axes_on_image(image, K, R, t, axis_len=0.1):
    img = image.copy()
    origin = t.flatten()

    axes = [origin + R[:, i] * axis_len for i in range(3)]  # X, Y, Z
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # BGR
    origin_2d = project_point(origin, K)

    for pt, color in zip(axes, colors):
        pt_2d = project_point(pt, K)
        cv2.line(img, origin_2d, pt_2d, color, 2)
    
    return img

def draw_axes_3d(ax, R, t, scale=0.1):
    origin = t.flatten()
    x_axis = R[:, 0] * scale
    y_axis = R[:, 1] * scale
    z_axis = R[:, 2] * scale

    ax.quiver(*origin, *x_axis, color='r', label='X')
    ax.quiver(*origin, *y_axis, color='g', label='Y')
    ax.quiver(*origin, *z_axis, color='b', label='Z')

# Extract pose
R1 = T1[:3, :3]
t1 = T1[:3, 3].reshape(3, 1)

R2 = T2[:3, :3]
t2 = T2[:3, 3].reshape(3,1)

# 2D Overlay
transformed = T1.copy()
transformed[:3, 3] *= -1
transformed = np.linalg.inv(transformed)

negated = T2.copy()
#negated[:3, 2] *= -1 
negated[:3, 3] *= -1 
# negated[2, 3] *= -1
# negated[1, 3] *= -1
# negated[0, 3] *= -1
negated = np.linalg.inv(negated)

rotx = trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0])
roty = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
rotz = trimesh.transformations.rotation_matrix(np.pi/180 * -5, [0,0,1])
#world = roty @ rotz
world = np.eye(4)
#world = roty

# === Load 3D mesh ===
trimesh_obj.apply_scale(0.001)
mesh = pyrender.Mesh.from_trimesh(trimesh_obj, smooth=False)

transformed = np.array([
    [1,  0,  0, 0],
    [0, -1,  0, 0],
    [0,  0, -1, 0],
    [0,  0,  0, 1]
], dtype=np.float32) @ T1


# === Scene Setup ===
scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.3, 0.3, 0.3])
scene.add(camera, pose = world)
scene.add(mesh, pose = transformed)
camera = pyrender.IntrinsicsCamera(fx,fy,cx,cy, znear=0.001, zfar=10.0)

light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
scene.add(light, pose=transformed)

# === Render Offscreen ===
r = pyrender.OffscreenRenderer(viewport_width=w, viewport_height=h)
color, depth = r.render(scene)
r.delete()

# === Load background RGB image
bg = rgb_image
bg = cv2.resize(bg, (w, h))
bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

# === Create mask from depth (where model is visible)
mask = (depth > 0)

# === Composite model onto background
composite = bg.copy()
composite[mask] = color[mask]

# === Save result
overlay = draw_axes_on_image(composite, K, R1, t1)
overlay2 = draw_axes_on_image(overlay, K, R2, t2)

# 3D Visualization Scatter
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(121, projection='3d')

# Plot object points from depth
points_3d = get_3d_points_from_mask(depth_map, mask, depth_scale)
ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2], s=0.5, c='gray', alpha=0.3)

# Plot pose axes
#draw_axes_3d(ax, R, t)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("3D Pose Visualization")
ax.view_init(elev=30, azim=45)

# 2D overlay
ax2 = fig.add_subplot(122)
ax2.imshow(overlay2)
ax2.set_title("2D Pose Overlay")
ax2.axis("off")

cv2.imwrite("output.png" , cv2.cvtColor(overlay2, cv2.COLOR_RGB2BGR))
print("Saved")

plt.tight_layout()
plt.show()