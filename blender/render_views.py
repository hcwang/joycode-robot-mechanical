# 生成多视角渲染图 - 无头模式
import bpy
import os

# 文件路径
BLEND_FILE = "/root/repos/joycode-robot-mechanical/blender/MD-001_Shell_V6.1.blend"
RENDERS_DIR = "/root/repos/joycode-robot-mechanical/renders/"

# 确保渲染目录存在
os.makedirs(RENDERS_DIR, exist_ok=True)

# 加载 Blender 文件
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

# 设置渲染分辨率
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# 使用 Workbench 引擎（适合无头渲染）
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.type = 'SOLID'
scene.display.shading.color_type = 'MATERIAL'

# 查找场景中的对象
objects_to_render = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        objects_to_render.append(obj)

print(f"找到 {len(objects_to_render)} 个网格对象")

# 设置相机
camera = None
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        camera = obj
        break

if camera is None:
    # 创建新相机
    camera_data = bpy.data.cameras.new('RenderCamera')
    camera = bpy.data.objects.new('RenderCamera', camera_data)
    bpy.context.collection.objects.link(camera)

scene.camera = camera

# 计算场景边界以正确定位相机
min_corner = None
max_corner = None
for obj in objects_to_render:
    if min_corner is None:
        min_corner = obj.bound_box[0][:]
        max_corner = obj.bound_box[7][:]
    else:
        for i in range(8):
            for j in range(3):
                min_corner[j] = min(min_corner[j], obj.bound_box[i][j])
                max_corner[j] = max(max_corner[j], obj.bound_box[i][j])

if min_corner and max_corner:
    center = [(min_corner[i] + max_corner[i]) / 2 for i in range(3)]
    size = max(max_corner[i] - min_corner[i] for i in range(3))
    print(f"场景中心：{center}, 尺寸：{size}")
else:
    center = [0, 0, 0]
    size = 10

# 渲染视图配置
views = {
    'front': {
        'location': (center[0], center[1] - size * 2, center[2] + size * 0.3),
        'rotation': (1.4, 0, 0),
        'filename': 'MD-001_Shell_V6.1_Front_View.png'
    },
    'side': {
        'location': (center[0] + size * 2, center[1], center[2] + size * 0.3),
        'rotation': (1.4, 0, 1.57),
        'filename': 'MD-001_Shell_V6.1_Side_View.png'
    },
    'top': {
        'location': (center[0], center[1], center[2] + size * 2.5),
        'rotation': (0, 0, 0),
        'filename': 'MD-001_Shell_V6.1_Top_View.png'
    },
    'exploded': {
        'location': (center[0] + size * 1.5, center[1] - size * 1.5, center[2] + size * 1.5),
        'rotation': (1.1, 0, 0.78),
        'filename': 'MD-001_Shell_V6.1_Exploded_View.png'
    }
}

# 渲染每个视图
for view_name, config in views.items():
    print(f"渲染 {view_name} 视图...")
    
    # 设置相机位置
    camera.location = config['location']
    camera.rotation_euler = config['rotation']
    
    # 设置输出路径
    output_path = os.path.join(RENDERS_DIR, config['filename'])
    scene.render.filepath = output_path
    
    try:
        # 渲染
        bpy.ops.render.render(write_still=True)
        print(f"  完成：{output_path}")
    except Exception as e:
        print(f"  错误：{e}")

print("\n所有视图渲染完成！")
print(f"渲染文件保存在：{RENDERS_DIR}")

# 列出渲染的文件
for f in os.listdir(RENDERS_DIR):
    if f.endswith('.png'):
        filepath = os.path.join(RENDERS_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  {f}: {size} bytes")
