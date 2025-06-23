import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# -----------------------------
# CONFIGURATION (replace with your data)
# -----------------------------

# Load or define your data here
rgb_image = cv2.imread("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/000049_rgb.png")  # shape: (H, W, 3)
depth_map = cv2.imread("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/000049_depth.png", cv2.IMREAD_UNCHANGED) # shape: (H, W), in depth units
mask = cv2.imread("C:/Users/Bohori/Trial Data/test data/Ql4i/000049/000049_roi.png", cv2.IMREAD_GRAYSCALE)  # binary mask of object
depth_scale = 1.0000000474974513  # e.g., if depth is in mm, scale to meters

# Camera intrinsics
K = np.array([
        [906.17822265625, 0.0, 646.2926635742188],
        [0.0, 905.9284057617188, 370.1160583496094],
        [0.0, 0.0, 1.0]
    ])

# Pose matrix (4x4) from FoundationPose or similar
T = np.array([
    [6.441221833229064941e-01, 7.646285891532897949e-01, -2.120633423328399658e-02, 1.071708276867866516e-03],  
    [6.352801322937011719e-01, -5.501901507377624512e-01, -5.419494509696960449e-01, -1.981154456734657288e-02],  
    [-4.260576665401458740e-01, 3.356097936630249023e-01, -8.401432633399963379e-01, 5.749665498733520508e-01],
    [0.0, 0.0, 0.0, 1.0]
])  # Example: replace with your output

# -----------------------------
# FUNCTIONS
# -----------------------------

def get_3d_points_from_mask(depth_map, mask, K, depth_scale):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

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

# -----------------------------
# MAIN VISUALIZATION
# -----------------------------

# Extract pose
#R = np.linalg.inv(T[:3, :3])
R = T[:3, :3]
t = T[:3, 3].reshape(3, 1)

print(R)
# 2D Overlay
overlay = draw_axes_on_image(rgb_image, K, R, t)

# 3D Visualization
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(121, projection='3d')

# Plot object points from depth
points_3d = get_3d_points_from_mask(depth_map, mask, K, depth_scale)
ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2], s=0.5, c='gray', alpha=0.3)

# Plot pose axes
draw_axes_3d(ax, R, t)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("3D Pose Visualization")
ax.view_init(elev=30, azim=45)

# 2D overlay
ax2 = fig.add_subplot(122)
ax2.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
ax2.set_title("2D Pose Overlay")
ax2.axis("off")

plt.tight_layout()
plt.show()