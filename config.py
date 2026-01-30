# config.py - 全局配置文件

# ========== GUI窗口配置 ==========
WINDOW_TITLE = "GPU性能测试数据录入工具"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
WINDOW_MIN_WIDTH = 1400
WINDOW_MIN_HEIGHT = 850

# ========== 性能数据字段映射 ==========
# 测试类型→性能字段映射：key=测试类型，value=（输入字段列表, 计算字段列表）
PERF_FIELDS_MAP = {
    # 推理类：文本推理/图文推理
    "文本推理": (
        ["客户端设置并发", "实际并发", "输入长度（tokens）", "输出长度（tokens）", "TTFT（ms）", "TPOT（ms）", "总吞吐（tokens/s）"],
        ["总输出吞吐（tokens/s）", "单卡输出吞吐（tokens/s）"],
    ),
    "图文推理": (
        ["客户端设置并发", "实际并发", "输入长度（tokens）", "输出长度（tokens）", "TTFT（ms）", "TPOT（ms）", "总吞吐（tokens/s）"],
        ["总输出吞吐（tokens/s）", "单卡输出吞吐（tokens/s）"],
    ),
    # 训练类
    "预训练": (
        ["batch_size", "训练轮数", "训练时间（min）"],
        [],
    ),
    "lora微调": (
        ["batch_size", "训练轮数", "训练时间（min）"],
        [],
    ),
    "全参微调": (
        ["batch_size", "训练轮数", "训练时间（min）"],
        [],
    ),
    # 其他类
    "图像识别": (["FPS"], []),
    "语音推理": (["推理时间（ms）"], []),
    "文档排序": (["推理时间（ms）"], []),
    "特征提取": (["推理时间（ms）"], []),
    "精度测试": (["得分（%）"], []),
}

# 默认配置
DEFAULT_PERF_FIELDS = (["未配置测试类型字段"], [])