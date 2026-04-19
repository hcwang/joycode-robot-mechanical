# 渲染内部支架爆炸图 - Workbench 模式
import bpy
import os

# 文件路径
BLEND_FILE = "/root/repos/joycode-robot-mechanical/blender/MD-002_Internal_Bracket.blend"
RENDERS_DIR = "/root/repos/joycode-robot-mechanical/renders/"

# 确保渲染目录存在
os.makedirs(RENDERS_DIR, exist_ok=True)

# 加载 Blender 文件
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

# 设置渲染参数
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'

# 使用 Workbench 引擎 - 最适合无头渲染
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.type = 'SOLID'
scene.display.shading.color_type = 'RANDOM'
scene.display.shading.light = 'FLAT'

print("渲染内部支架视图...")

# 获取所有相关对象
objects = {}
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        objects[obj.name] = obj
        print(f"  找到对象：{obj.name}")

# 查找或创建相机
camera = None
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        camera = obj
        break

if camera is None:
    print("创建新相机...")
    camera_data = bpy.data.cameras.new('RenderCamera')
    camera = bpy.data.objects.new('RenderCamera', camera_data)
    bpy.context.collection.objects.link(camera)

scene.camera = camera

# 定义视图配置
views = {
    'exploded': {
        'location': (100, -100, 80),
        'rotation': (1.15, 0, 0.85),
        'filename': 'MD-002_Internal_Bracket_Exploded.png',
        'explode_offset': 30
    },
    'assembly': {
        'location': (80, -80, 60),
        'rotation': (1.1, 0, 0.78),
        'filename': 'MD-002_Internal_Bracket_Assembly.png',
        'explode_offset': 0
    },
    'battery_holder': {
        'location': (0, -150, 40),
        'rotation': (1.4, 0, 0),
        'filename': 'MD-002_Battery_Holder_View.png',
        'explode_offset': 0
    },
    'camera_mount': {
        'location': (150, 0, 40),
        'rotation': (1.4, 0, 1.57),
        'filename': 'MD-002_Camera_Mount_View.png',
        'explode_offset': 0
    }
}

# 渲染每个视图
for view_name, config in views.items():
    print(f"\n渲染 {view_name} 视图...")
    
    # 重置所有对象位置
    if 'BatteryHolder' in objects:
        objects['BatteryHolder'].location = [0, 0, 0]
    if 'CameraMount_Base' in objects:
        objects['CameraMount_Base'].location = [0, 0, 0]
    if 'CameraMount_Platform' in objects:
        objects['CameraMount_Platform'].location = [0, 0, 15]
    
    # 如果是爆炸图，分离组件
    if config['explode_offset'] > 0:
        offset = config['explode_offset']
        if 'CameraMount_Platform' in objects:
            objects['CameraMount_Platform'].location = [0, 0, 15 + offset]
        if 'BatteryHolder' in objects:
            objects['BatteryHolder'].location = [-offset, -offset, 0]
    
    # 设置相机位置
    camera.location = config['location']
    camera.rotation_euler = config['rotation']
    
    # 设置输出路径
    output_path = os.path.join(RENDERS_DIR, config['filename'])
    scene.render.filepath = output_path
    
    try:
        # 渲染
        bpy.ops.render.render(write_still=True)
        print(f"  ✓ 完成：{output_path}")
    except Exception as e:
        print(f"  ✗ 错误：{e}")

# 列出渲染的文件
print("\n渲染文件列表:")
for f in os.listdir(RENDERS_DIR):
    if f.startswith("MD-002_"):
        filepath = os.path.join(RENDERS_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  {f}: {size} bytes")

print("\n渲染完成！")
