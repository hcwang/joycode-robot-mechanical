# MD-005 外壳 V6.2 - 三种配色方案渲染
# 匠心 (陈建) - 2026-04-21
# 配色方案：科技蓝、深空灰、珊瑚红

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

# 查找外壳对象
shell_object = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'Shell' in obj.name:
        shell_object = obj
        break

if shell_object is None:
    # 查找第一个网格对象
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            shell_object = obj
            break

print(f"找到外壳对象：{shell_object.name if shell_object else 'None'}")

# 设置相机
camera = None
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        camera = obj
        break

if camera is None:
    camera_data = bpy.data.cameras.new('RenderCamera')
    camera = bpy.data.objects.new('RenderCamera', camera_data)
    bpy.context.collection.objects.link(camera)

scene.camera = camera

# 计算场景边界
objects_to_render = [obj for obj in bpy.data.objects if obj.type == 'MESH']
min_corner = None
max_corner = None

for obj in objects_to_render:
    if min_corner is None:
        min_corner = list(obj.bound_box[0])
        max_corner = list(obj.bound_box[7])
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

# 设置相机位置（产品视角）
camera.location = (center[0] + size * 1.5, center[1] - size * 1.5, center[2] + size * 1.2)
camera.rotation_euler = (1.2, 0, 0.8)

# 三种配色方案
color_schemes = {
    'tech_blue': {
        'name': '科技蓝',
        'color': (0.0, 0.4, 0.8, 1.0),  # #0066CC
        'filename': 'MD-005_Shell_V6.2_Tech_Blue.png'
    },
    'space_gray': {
        'name': '深空灰',
        'color': (0.35, 0.35, 0.38, 1.0),  # #5A5A61
        'filename': 'MD-005_Shell_V6.2_Space_Gray.png'
    },
    'coral_red': {
        'name': '珊瑚红',
        'color': (1.0, 0.45, 0.35, 1.0),  # #FF7359
        'filename': 'MD-005_Shell_V6.2_Coral_Red.png'
    }
}

# 渲染每种配色
for scheme_key, scheme in color_schemes.items():
    print(f"\n渲染 {scheme['name']} 配色...")
    
    # 创建或更新材质
    mat_name = f"Shell_{scheme_key}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
    
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    
    bsdf.inputs["Base Color"].default_value = scheme['color']
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.1
    
    # 应用材质到外壳对象
    if shell_object:
        if shell_object.data.materials:
            shell_object.data.materials[0] = mat
        else:
            shell_object.data.materials.append(mat)
    
    # 设置输出路径
    output_path = os.path.join(RENDERS_DIR, scheme['filename'])
    scene.render.filepath = output_path
    
    try:
        # 渲染
        bpy.ops.render.render(write_still=True)
        print(f"  完成：{output_path}")
    except Exception as e:
        print(f"  错误：{e}")

print("\n所有配色渲染完成！")
print(f"渲染文件保存在：{RENDERS_DIR}")

# 列出渲染的文件
for f in os.listdir(RENDERS_DIR):
    if f.endswith('.png') and 'V6.2' in f:
        filepath = os.path.join(RENDERS_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  {f}: {size} bytes")
