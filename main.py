# main.py - 程序入口（仅需运行此文件）
import tkinter as tk
from tkinter import messagebox
import sys

def check_dependencies():
    """检查必要的依赖库"""
    missing = []
    
    # 检查tkinter（通常内置）
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    # 检查yaml
    try:
        __import__("yaml")
    except ImportError:
        missing.append("pyyaml")
    
    # 检查openpyxl（可能会卡注册表，跳过）
    # openpyxl会在首次导入时读取Windows注册表，这里仅检查是否存在
    try:
        import importlib.util
        spec = importlib.util.find_spec("openpyxl")
        if spec is None:
            missing.append("openpyxl")
    except Exception:
        missing.append("openpyxl")
    
    if missing:
        msg = f"缺失依赖库：{', '.join(missing)}\n\n请执行：\npip install {' '.join(missing)}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("依赖缺失", msg)
        root.destroy()
        return False
    
    return True

def main():
    """主程序入口"""
    if not check_dependencies():
        sys.exit(1)
    
    # 导入GUI
    from gui import GPUFullInfoGUI
    
    # 启动应用
    root = tk.Tk()
    app = GPUFullInfoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
