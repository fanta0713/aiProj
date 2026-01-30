# steps_ui.py - 各步骤的UI渲染模块
import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from utils import ScrollableFrame


class StepsUIRenderer:
    """负责5个步骤的UI初始化和渲染"""

    def __init__(self, main_frame, app_ref):
        """
        Args:
            main_frame: 主滚动框架的inner frame
            app_ref: 主应用引用（用于访问应用数据）
        """
        self.main_frame = main_frame
        self.app = app_ref
        self.frames = {}  # 存储各步骤frame引用

    def create_all_steps(self):
        """创建所有5个步骤的UI"""
        # Ensure the main frame grid expands: allow 4 columns and multiple rows to stretch
        for c in range(4):
            try:
                self.main_frame.columnconfigure(c, weight=1)
            except Exception:
                pass
        for r in range(6):
            try:
                self.main_frame.rowconfigure(r, weight=1)
            except Exception:
                pass

        self._create_step1()
        self._create_step2()
        self._create_step3()
        self._create_step4()
        self._create_step5()
        self._create_buttons()

    def _create_step1(self):
        """步骤1：基础信息填写"""
        frm = ttk.LabelFrame(self.main_frame, text="步骤1：基础信息填写（必填）", padding=15)
        frm.grid(row=0, column=0, sticky="ew", padx=15, pady=10, columnspan=4)
        self.frames["step1"] = frm

        # 第1行
        ttk.Label(frm, text="项目名称：", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.project_name, width=35).grid(
            row=0, column=1, sticky="ew", padx=10, pady=8
        )

        ttk.Label(frm, text="测试周期：", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.test_cycle, width=35).grid(
            row=0, column=3, sticky="ew", padx=10, pady=8
        )

        # 第2行
        ttk.Label(frm, text="厂家（格式：厂家1（GPU）、厂家2（GPU））：", font=("Arial", 10)).grid(
            row=1, column=0, sticky="e", padx=10, pady=8
        )
        ttk.Entry(frm, textvariable=self.app.vendor_str, width=100).grid(
            row=1, column=1, sticky="ew", padx=10, pady=8, columnspan=3
        )

        # 第3行
        ttk.Label(frm, text="客户名称：", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.customer_name, width=35).grid(
            row=2, column=1, sticky="ew", padx=10, pady=8
        )

        ttk.Label(frm, text="客户行业：", font=("Arial", 10)).grid(row=2, column=2, sticky="e", padx=10, pady=8)
        industry_combo = ttk.Combobox(
            frm,
            textvariable=self.app.customer_industry,
            values=["互联网", "运营商", "金融", "能源", "企业", "政府", "交通", "教育", "医疗", "商业", "国际"],
            width=30,
            state="readonly"
        )
        industry_combo.grid(row=2, column=3, sticky="ew", padx=10, pady=8)

        # 第4行
        ttk.Label(frm, text="中标情况：", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=10, pady=8)
        bid_combo = ttk.Combobox(
            frm,
            textvariable=self.app.bid_status,
            values=["已中标", "未中标"],
            width=30,
            state="readonly"
        )
        bid_combo.grid(row=3, column=1, sticky="ew", padx=10, pady=8)

        ttk.Label(frm, text="中标份额（如有）：", font=("Arial", 10)).grid(row=3, column=2, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.bid_share, width=35).grid(
            row=3, column=3, sticky="ew", padx=10, pady=8
        )

        # 第5行
        ttk.Label(frm, text="未中标原因（如有）：", font=("Arial", 10)).grid(row=4, column=0, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.bid_fail_reason, width=100).grid(
            row=4, column=1, sticky="ew", padx=10, pady=8, columnspan=3
        )

        # 第6行
        ttk.Label(frm, text="测试负责人：", font=("Arial", 10)).grid(row=5, column=0, sticky="e", padx=10, pady=8)
        ttk.Entry(frm, textvariable=self.app.test_owner, width=35).grid(
            row=5, column=1, sticky="ew", padx=10, pady=8
        )

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)

    def _create_step2(self):
        """步骤2：模型+测试类型配置"""
        frm = ttk.LabelFrame(
            self.main_frame, text="步骤2：模型+测试类型配置（必填）", padding=15
        )
        frm.grid(row=1, column=0, sticky="nsew", padx=15, pady=10, columnspan=4)
        self.frames["step2"] = frm
        frm.grid_remove()

        # 模型输入和测试类型选择容器
        model_type_frm = ttk.LabelFrame(frm, text="模型和测试类型", padding=10)
        model_type_frm.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.app.model_type_frame = model_type_frm

        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(0, weight=1)
        frm.rowconfigure(0, weight=1)

    def _create_step3(self):
        """步骤3：测试环境填写"""
        frm = ttk.LabelFrame(self.main_frame, text="步骤3：测试环境填写（必填）", padding=15)
        frm.grid(row=2, column=0, sticky="nsew", padx=15, pady=10, columnspan=4)
        self.frames["step3"] = frm
        self.app.step3_frame = frm
        frm.grid_remove()
        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(0, weight=1)

    def _create_step4(self):
        """步骤4：PK指标+性能数据填写"""
        frm_container = ttk.Frame(self.main_frame)
        frm_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=5, columnspan=4)

        # 4-1 PK指标
        pk_frm = ttk.LabelFrame(frm_container, text="步骤4-1：PK指标填写")
        pk_frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.pk_frame = pk_frm

        # 4-2 性能数据
        perf_frm = ttk.LabelFrame(
            frm_container, text="步骤4-2：性能数据填写（同步步骤3数据集）"
        )
        perf_frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.perf_frame = perf_frm

        self.frames["step4"] = frm_container
        self.frames["step4"].grid_remove()

    def _create_step5(self):
        """步骤5：项目问题录入 + 项目总结生成"""
        frm_container = ttk.Frame(self.main_frame)
        frm_container.grid(row=4, column=0, sticky="nsew", padx=10, pady=5, columnspan=4)

        # 5-1 项目问题录入
        problem_frm = ttk.LabelFrame(frm_container, text="步骤5-1：项目中遇到的问题录入")
        problem_frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.problem_frame = problem_frm

        # 5-2 项目总结生成
        summary_frm = ttk.LabelFrame(frm_container, text="步骤5-2：项目总结自动生成")
        summary_frm.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 生成总结按钮
        ttk.Button(
            summary_frm,
            text="📝 生成项目总结",
            command=self.app._generate_project_summary,
        ).pack(pady=8)

        # 总结展示区域（滚动文本框）
        summary_scroll = ScrollableFrame(summary_frm)
        summary_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.summary_text = tk.Text(
            summary_scroll.scrollable_frame, wrap=tk.WORD, font=("", 10)
        )
        self.app.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.summary_text.config(state=tk.DISABLED)

        self.frames["step5"] = frm_container
        self.frames["step5"].grid_remove()

    def _create_buttons(self):
        """底部导航按钮"""
        btn_frm = ttk.Frame(self.main_frame)
        btn_frm.grid(row=5, column=0, sticky="ew", padx=10, pady=20, columnspan=4)

        self.app.prev_btn = ttk.Button(
            btn_frm, text="上一步", command=self.app.prev_step, state=tk.DISABLED
        )
        self.app.prev_btn.pack(side=tk.LEFT, padx=5)

        self.app.next_btn = ttk.Button(btn_frm, text="下一步", command=self.app.next_step)
        self.app.next_btn.pack(side=tk.LEFT, padx=5)

        self.app.gen_btn = ttk.Button(
            btn_frm,
            text="生成Excel报告",
            command=self.app.generate_excel,
            state=tk.DISABLED,
        )
        self.app.gen_btn.pack(side=tk.LEFT, padx=5)

        self.app.reset_btn = ttk.Button(btn_frm, text="重置所有", command=self.app.reset_all)
        self.app.reset_btn.pack(side=tk.LEFT, padx=5)

    def refresh_step_display(self, current_step):
        """刷新步骤显示"""
        # 隐藏所有步骤
        for frame in self.frames.values():
            frame.grid_remove()

        # 只显示当前步骤
        step_key = f"step{current_step}"
        if step_key in self.frames:
            self.frames[step_key].grid()

        # 更新按钮状态
        self.app.prev_btn.config(state=tk.NORMAL if current_step > 1 else tk.DISABLED)
        self.app.next_btn.config(state=tk.NORMAL if current_step < 5 else tk.DISABLED)
        self.app.gen_btn.config(state=tk.NORMAL if current_step >= 5 else tk.DISABLED)

        # 刷新滚动
        self.app.main_scroll.canvas.update_idletasks()
        self.app.main_scroll.canvas.configure(
            scrollregion=self.app.main_scroll.canvas.bbox("all")
        )
