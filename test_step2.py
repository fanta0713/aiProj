#!/usr/bin/env python3
"""
测试 Step 2 UI 和验证逻辑
"""
import tkinter as tk
import uuid
from gui import GPUFullInfoGUI

def test_step2_workflow():
    """测试 Step 2 的完整工作流"""
    # 创建应用实例
    root = tk.Tk()
    app = GPUFullInfoGUI(root)
    
    print("=" * 50)
    print("测试 Step 2 工作流")
    print("=" * 50)
    
    # 测试 1: 验证初始状态
    print("\n[测试 1] 验证初始状态")
    print(f"  model_input_data: {app.model_input_data}")
    assert isinstance(app.model_input_data, list), "model_input_data 应该是列表"
    print("  ✓ model_input_data 初始化为空列表")
    
    # 测试 2: 模拟添加模型
    print("\n[测试 2] 模拟添加模型行")
    # 模拟第一个模型行
    model_entry_1 = tk.StringVar(value="GPT-4")
    test_types_1 = {}
    for tt in ["Inference", "Training"]:
        test_types_1[tt] = tk.IntVar(value=1)
    
    model_data_1 = {
        "model_name": model_entry_1,
        "test_types": test_types_1,
        "id": str(uuid.uuid4())
    }
    app.model_input_data.append(model_data_1)
    print(f"  ✓ 添加了模型: GPT-4，测试类型: Inference=1, Training=1")
    
    # 模拟第二个模型行
    model_entry_2 = tk.StringVar(value="Claude")
    test_types_2 = {}
    for tt in ["Inference", "Training"]:
        test_types_2[tt] = tk.IntVar(value=1 if tt == "Inference" else 0)
    
    model_data_2 = {
        "model_name": model_entry_2,
        "test_types": test_types_2,
        "id": str(uuid.uuid4())
    }
    app.model_input_data.append(model_data_2)
    print(f"  ✓ 添加了模型: Claude，测试类型: Inference=1, Training=0")
    
    # 测试 3: 验证 Step 2 验证逻辑
    print("\n[测试 3] 验证 Step 2 验证逻辑")
    result = app._validate_step2()
    print(f"  验证结果: {result}")
    assert result, "验证应该通过"
    print(f"  ✓ 验证通过")
    
    # 测试 4: 检查提取的模型和测试类型
    print("\n[测试 4] 检查提取的数据")
    print(f"  selected_models: {app.selected_models}")
    print(f"  model_test_type_map: {app.model_test_type_map}")
    
    assert "GPT-4" in app.selected_models, "应该包含 GPT-4"
    assert "Claude" in app.selected_models, "应该包含 Claude"
    assert set(app.model_test_type_map["GPT-4"]) == {"Inference", "Training"}
    assert set(app.model_test_type_map["Claude"]) == {"Inference"}
    print("  ✓ 模型和测试类型正确提取")
    
    # 测试 5: 测试验证失败的情况 - 没有模型
    print("\n[测试 5] 测试验证失败情况（无模型）")
    app.model_input_data.clear()
    result = app._validate_step2()
    print(f"  验证结果: {result}")
    assert not result, "验证应该失败"
    print("  ✓ 验证正确失败")
    
    # 测试 6: 测试验证失败的情况 - 模型名为空
    print("\n[测试 6] 测试验证失败情况（模型名为空）")
    empty_entry = tk.StringVar(value="")
    test_types_empty = {}
    for tt in ["Inference", "Training"]:
        test_types_empty[tt] = tk.IntVar(value=0)
    
    app.model_input_data.append({
        "model_name": empty_entry,
        "test_types": test_types_empty,
        "id": str(uuid.uuid4())
    })
    result = app._validate_step2()
    print(f"  验证结果: {result}")
    assert not result, "验证应该失败"
    print("  ✓ 验证正确失败")
    
    # 测试 7: 测试验证失败的情况 - 模型有名称但没有选择测试类型
    print("\n[测试 7] 测试验证失败情况（模型有名称但没有选择测试类型）")
    app.model_input_data.clear()
    no_test_type_entry = tk.StringVar(value="TestModel")
    test_types_none = {}
    for tt in ["Inference", "Training"]:
        test_types_none[tt] = tk.IntVar(value=0)
    
    app.model_input_data.append({
        "model_name": no_test_type_entry,
        "test_types": test_types_none,
        "id": str(uuid.uuid4())
    })
    result = app._validate_step2()
    print(f"  验证结果: {result}")
    assert not result, "验证应该失败"
    print("  ✓ 验证正确失败")
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过！")
    print("=" * 50)
    
    root.destroy()

if __name__ == "__main__":
    test_step2_workflow()
