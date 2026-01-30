# data_manager.py - 数据管理模块
import uuid
import yaml
import os
from tkinter import messagebox
from config import PERF_FIELDS_MAP


class DataManager:
    """管理所有数据的初始化、验证和更新"""

    @staticmethod
    def load_models(yaml_path, app_ref):
        """加载模型配置"""
        if not os.path.exists(yaml_path):
            DataManager.create_default_yaml(yaml_path)

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            model_names = config.get("model_names", [])
            test_types = config.get("test_types", [])
            return model_names, test_types
        except yaml.YAMLError as e:
            messagebox.showerror("YAML格式错误", f"语法错误：{str(e)}\n请用2个空格缩进")
            return [], []
        except Exception as e:
            messagebox.showerror("读取失败", f"配置文件错误：{str(e)}")
            return [], []

    @staticmethod
    def create_default_yaml(path):
        """创建默认YAML配置"""
        config = {
            "model_names": ["DeepSeek-R1", "yolov11", "qwen14B"],
            "test_types": [
                "文本推理",
                "图文推理",
                "图像识别",
                "预训练",
                "lora微调",
                "全参微调",
                "语音推理",
                "文档排序",
                "特征提取",
                "精度测试",
            ],
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            messagebox.showerror("创建失败", f"无法创建配置文件：{str(e)}")

    @staticmethod
    def parse_vendor_str(vendor_str):
        """解析厂家字符串"""
        vendors = []
        if not vendor_str.strip():
            return vendors
        for item in vendor_str.split("、"):
            item = item.strip()
            if "（" in item and "）" in item:
                name = item.split("（")[0].strip()
                gpu = item.split("（")[1].replace("）", "").strip()
                if name and gpu:
                    vendors.append((name, gpu))
        return vendors

    @staticmethod
    def init_env_data(selected_models, model_test_type_map, vendor_list):
        """初始化环境数据"""
        env_data = []
        for model in selected_models:
            for tt in model_test_type_map[model]:
                for vendor, gpu in vendor_list:
                    env_data.append({
                        "model": model,
                        "test_type": tt,
                        "vendor": vendor,
                        "gpu": gpu,
                        "gpu_count": "",
                        "dataset": "",
                        "tool": "",
                        "is_dynamic": False,
                        "id": str(uuid.uuid4()),
                    })
        return env_data

    @staticmethod
    def init_perf_data(env_data, selected_models, model_test_type_map):
        """初始化性能和PK数据"""
        perf_data = []
        for env in env_data:
            input_fields, calc_fields = PERF_FIELDS_MAP.get(env["test_type"], ([], []))
            perf_data.append({
                "id": str(uuid.uuid4()),
                "model": env["model"],
                "test_type": env["test_type"],
                "vendor": env["vendor"],
                "gpu": env.get("gpu", ""),
                "dataset": env["dataset"],
                "gpu_count": env["gpu_count"],
                "input_fields": input_fields,
                "calc_fields": calc_fields,
                "input_values": {field: "" for field in input_fields},
                "calc_values": {field: "" for field in calc_fields},
            })

        # 初始化PK数据
        pk_data = []
        pk_unique = set()
        for model in selected_models:
            for tt in model_test_type_map[model]:
                key = f"{model}_{tt}"
                if key not in pk_unique:
                    pk_unique.add(key)
                    input_fields, calc_fields = PERF_FIELDS_MAP.get(tt, ([], []))
                    pk_options = input_fields + calc_fields

                    pk_data.append({
                        "id": str(uuid.uuid4()),
                        "model": model,
                        "test_type": tt,
                        "pk_options": pk_options,
                        "selected_pk": "",
                    })

        return perf_data, pk_data

    @staticmethod
    def calculate_throughput(perf_data):
        """计算推理吞吐数据"""
        for perf_row in perf_data:
            tt = perf_row["test_type"]
            if tt not in ["文本推理", "图文推理"]:
                continue

            input_vals = perf_row["input_values"]
            required_fields = ["输入长度（tokens）", "输出长度（tokens）", "总吞吐（tokens/s）"]
            if not all(f in input_vals for f in required_fields):
                continue

            try:
                input_len = float(input_vals["输入长度（tokens）"] or 0)
                output_len = float(input_vals["输出长度（tokens）"] or 0)
                total_throughput = float(input_vals["总吞吐（tokens/s）"] or 0)
                gpu_count = float(perf_row["gpu_count"] or 1)
            except ValueError:
                continue

            # 计算
            if input_len + output_len > 0:
                total_output_throughput = total_throughput * (
                    output_len / (input_len + output_len)
                )
            else:
                total_output_throughput = 0

            single_card_throughput = (
                total_output_throughput / gpu_count if gpu_count > 0 else 0
            )

            # 更新计算值
            perf_row["calc_values"]["总输出吞吐（tokens/s）"] = f"{total_output_throughput:.2f}"
            perf_row["calc_values"]["单卡输出吞吐（tokens/s）"] = f"{single_card_throughput:.2f}"

    @staticmethod
    def init_problem_data():
        """初始化项目问题数据"""
        return [
            {
                "id": str(uuid.uuid4()),
                "category": "",
                "description": "",
                "person": "",
                "solution": "",
            }
        ]
