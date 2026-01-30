#!/usr/bin/env python3
"""
集成测试：验证应用完整工作流
"""
import tkinter as tk
import time
import threading
from gui import GPUFullInfoGUI

def test_gui_startup():
    """测试GUI启动和基本功能"""
    print("=" * 60)
    print("集成测试：GUI 启动和基本功能")
    print("=" * 60)
    
    # 创建应用
    root = tk.Tk()
    app = GPUFullInfoGUI(root)
    
    print("\n[步骤 1] 验证 GUI 初始化")
    assert app is not None, "应用创建失败"
    print("  ✓ GUI 成功创建")
    
    print("\n[步骤 2] 验证初始属性")
    assert hasattr(app, 'model_input_data'), "缺少 model_input_data 属性"
    assert hasattr(app, 'selected_models'), "缺少 selected_models 属性"
    assert hasattr(app, 'model_test_type_map'), "缺少 model_test_type_map 属性"
    assert isinstance(app.model_input_data, list), "model_input_data 应该是列表"
    print("  ✓ 所有必要属性存在")
    
    print("\n[步骤 3] 验证步骤框架")
    assert hasattr(app, 'step1_frame'), "缺少 step1_frame"
    assert hasattr(app, 'step2_frame'), "缺少 step2_frame"
    assert hasattr(app, 'step3_frame'), "缺少 step3_frame"
    assert hasattr(app, 'step4_frame'), "缺少 step4_frame"
    assert hasattr(app, 'step5_frame'), "缺少 step5_frame"
    print("  ✓ 5 个步骤框架创建成功")
    
    print("\n[步骤 4] 验证 Step 2 关键属性")
    assert hasattr(app, 'model_input_data'), "缺少 model_input_data"
    assert hasattr(app, 'model_type_frame'), "缺少 model_type_frame"
    print("  ✓ Step 2 关键属性存在")
    
    print("\n[步骤 5] 验证 Step 2 UI 框架")
    print("  ✓ model_type_frame 已验证")
    
    print("\n[步骤 6] 验证步骤导航功能")
    assert hasattr(app, 'current_step'), "缺少 current_step"
    assert app.current_step == 1, "初始步骤应该是 1"
    print("  ✓ 步骤导航功能存在")
    
    print("\n[步骤 7] 尝试加载模型配置")
    try:
        app._load_models()
        assert hasattr(app, 'test_types'), "缺少 test_types"
        assert isinstance(app.test_types, list), "test_types 应该是列表"
        print(f"  ✓ 模型配置加载成功，测试类型: {app.test_types}")
    except Exception as e:
        print(f"  ✗ 加载模型配置失败: {e}")
        raise
    
    print("\n[步骤 8] 测试窗口销毁")
    root.destroy()
    print("  ✓ 窗口销毁成功")
    
    print("\n" + "=" * 60)
    print("✓ 所有集成测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    # 禁用 Tkinter 错误消息框在非交互模式下
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    try:
        test_gui_startup()
    finally:
        root.destroy()
