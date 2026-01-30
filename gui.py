# gui.py - 核心GUI控制器（重构版）
import tkinter as tk
from tkinter import messagebox
import uuid
from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, PERF_FIELDS_MAP
from utils import ScrollableFrame, UIRenderer
from steps_ui import StepsUIRenderer
from data_manager import DataManager
from excel_export import ExcelExporter
from summary_generator import SummaryGenerator


class GPUFullInfoGUI:
    """GPU性能测试工具的主GUI控制器"""

    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # ========== 步骤管理 ==========
        self.current_step = 1

        # ========== 全局数据变量 ==========
        self.project_name = tk.StringVar()
        self.test_cycle = tk.StringVar()
        self.vendor_str = tk.StringVar()
        
        # Step 1 新增字段
        self.customer_name = tk.StringVar()
        self.customer_industry = tk.StringVar()
        self.bid_status = tk.StringVar()
        self.bid_share = tk.StringVar()
        self.bid_fail_reason = tk.StringVar()
        self.test_owner = tk.StringVar()

        self.selected_models = []
        self.model_test_type_map = {}
        self.model_vars = {}
        self.model_typet_vars = {}
        self.model_input_data = []  # 新增：存储用户输入的模型数据

        self.env_data = []
        self.pk_data = []
        self.perf_data = []
        self.problem_data = []
        self.project_summary = ""

        # ========== UI框架引用 ==========
        self.main_scroll = ScrollableFrame(root)
        self.main_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.main_frame = self.main_scroll.scrollable_frame

        # ========== 步骤框架引用 ==========
        self.step1_frame = None
        self.step2_frame = None
        self.step3_frame = None
        self.step4_frame = None
        self.step5_frame = None

        # ========== 步骤内部框架引用 ==========
        self.model_frame = None
        self.test_type_frame = None
        self.model_type_frame = None  # 新增：步骤2的模型和测试类型框架
        self.pk_frame = None
        self.perf_frame = None
        self.problem_frame = None
        self.summary_text = None

        # ========== 按钮引用 ==========
        self.prev_btn = None
        self.next_btn = None
        self.gen_btn = None
        self.reset_btn = None

        # ========== 初始化UI ==========
        self.ui_renderer = StepsUIRenderer(self.main_frame, self)
        self.ui_renderer.create_all_steps()

    def prev_step(self):
        """上一步"""
        if self.current_step > 1:
            self.current_step -= 1
            self._refresh_step_display()

    def next_step(self):
        """下一步"""
        if self.current_step == 1:
            if not self._validate_step1():
                return
            self.current_step = 2
            self._load_models()
            UIRenderer.render_models_and_test_types(
                self.model_type_frame, self
            )

        elif self.current_step == 2:
            if not self._validate_step2():
                return
            self.current_step = 3
            self._init_env_data()
            UIRenderer.render_env_frame(
                self.step3_frame,
                self.env_data,
                self.selected_models,
                self.model_test_type_map,
                self.vendor_str.get(),
                self.main_scroll,
            )

        elif self.current_step == 3:
            if not self._validate_step3():
                return
            self.current_step = 4
            self._init_perf_data()
            UIRenderer.render_pk_frame(self.pk_frame, self.pk_data, self)
            UIRenderer.render_perf_frame(self.perf_frame, self.perf_data, self)

        elif self.current_step == 4:
            self.current_step = 5
            UIRenderer.render_problem_frame(
                self.problem_frame, self.problem_data, self
            )

        self._refresh_step_display()

    def _refresh_step_display(self):
        """刷新步骤显示"""
        self.ui_renderer.refresh_step_display(self.current_step)

    # ============ 验证逻辑 ============
    def _validate_step1(self):
        """验证步骤1"""
        if not self.project_name.get().strip():
            messagebox.showerror("错误", "项目名称不能为空！")
            return False
        if not self.vendor_str.get().strip():
            messagebox.showerror("错误", "厂家信息不能为空！")
            return False
        return True

    def _validate_step2(self):
        """验证步骤2"""
        if not self.model_input_data:
            messagebox.showerror("错误", "必须至少有一个模型！")
            return False
        
        # 检查是否填写了模型名称和测试类型
        has_valid_model = False
        for model_data in self.model_input_data:
            # 从StringVar获取模型名称
            model_name = model_data["model_name"].get().strip() if isinstance(model_data["model_name"], tk.StringVar) else model_data["model_name"].strip()
            if not model_name:
                continue
            
            has_test_type = any(
                var.get() for var in model_data["test_types"].values()
            )
            if not has_test_type:
                messagebox.showerror("错误", f"模型 '{model_name}' 必须选择至少一个测试类型！")
                return False
            
            has_valid_model = True
        
        if not has_valid_model:
            messagebox.showerror("错误", "必须至少填写一个模型名称和选择测试类型！")
            return False
        
        # 提取选中的模型
        self.selected_models = []
        self.model_test_type_map = {}
        
        for model_data in self.model_input_data:
            # 从StringVar获取模型名称
            model_name = model_data["model_name"].get().strip() if isinstance(model_data["model_name"], tk.StringVar) else model_data["model_name"].strip()
            if model_name:
                self.selected_models.append(model_name)
                self.model_test_type_map[model_name] = [
                    tt for tt, var in model_data["test_types"].items() if var.get()
                ]
        
        return True

    def _validate_step3(self):
        """验证步骤3"""
        if not self.env_data:
            messagebox.showerror("错误", "测试环境数据不能为空！")
            return False
        for idx, data in enumerate(self.env_data):
            if not data["gpu_count"].strip():
                messagebox.showerror("错误", f"第{idx+1}行GPU数量不能为空！")
                return False
            if not data["dataset"].strip():
                messagebox.showerror("错误", f"第{idx+1}行数据集不能为空！")
                return False
        return True

    # ============ 数据初始化逻辑 ============
    def _load_models(self):
        """加载模型配置"""
        yaml_path = "model_config.yaml"
        _, self.test_types = DataManager.load_models(yaml_path, self)
        # 初始化模型输入数据列表（如果还没有）
        if not self.model_input_data:
            self.model_input_data = []

    def _init_env_data(self):
        """初始化环境数据"""
        vendor_list = DataManager.parse_vendor_str(self.vendor_str.get())
        self.env_data = DataManager.init_env_data(
            self.selected_models, self.model_test_type_map, vendor_list
        )

    def _init_perf_data(self):
        """初始化性能和PK数据"""
        self.perf_data, self.pk_data = DataManager.init_perf_data(
            self.env_data, self.selected_models, self.model_test_type_map
        )
        self.problem_data = DataManager.init_problem_data()

    # ============ 计算和导出逻辑 ============
    def _calculate_throughput(self):
        """计算推理吞吐"""
        try:
            DataManager.calculate_throughput(self.perf_data)
            UIRenderer.render_perf_frame(self.perf_frame, self.perf_data, self)
            messagebox.showinfo("成功", "吞吐数据计算完成！")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

    def _generate_project_summary(self):
        """生成项目总结"""
        try:
            self.project_summary = SummaryGenerator.generate(self)

            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, self.project_summary)
            self.summary_text.config(state=tk.DISABLED)

            messagebox.showinfo("成功", "项目总结已自动生成，包含性能对比与结论！")
        except Exception as e:
            messagebox.showerror("错误", f"生成项目总结失败：{str(e)}")

    def generate_excel(self):
        """生成Excel报告"""
        ExcelExporter.generate_report(self)

    def reset_all(self):
        """重置所有数据"""
        if messagebox.askyesno("确认", "确定要重置所有数据吗？"):
            self.current_step = 1
            self.project_name.set("")
            self.test_cycle.set("")
            self.vendor_str.set("")
            self.customer_name.set("")
            self.customer_industry.set("")
            self.bid_status.set("")
            self.bid_share.set("")
            self.bid_fail_reason.set("")
            self.test_owner.set("")
            self.selected_models.clear()
            self.model_test_type_map.clear()
            self.env_data.clear()
            self.perf_data.clear()
            self.pk_data.clear()
            self.problem_data.clear()
            self.project_summary = ""

            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.config(state=tk.DISABLED)

            self._refresh_step_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = GPUFullInfoGUI(root)
    root.mainloop()
