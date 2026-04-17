# 导出 STL 文件
import bpy

# 加载 Blender 文件
bpy.ops.wm.open_mainfile(filepath="/root/repos/joycode-robot-mechanical/blender/MD-001_Shell_V6.1.blend")

# 选择外壳对象
for obj in bpy.data.objects:
    if obj.name == "Shell_Outer":
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        break

# 导出 STL
bpy.ops.export_mesh.stl(filepath="/root/repos/joycode-robot-mechanical/stl/MD-001_Shell_V6.1.stl", 
                        use_selection=True)

print("STL 导出完成：stl/MD-001_Shell_V6.1.stl")
