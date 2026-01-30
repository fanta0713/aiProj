# summary_generator.py - 项目总结生成模块
from datetime import datetime


class SummaryGenerator:
    """基于性能数据生成项目总结"""

    @staticmethod
    def generate(app_ref):
        """生成完整的项目总结"""
        summary_parts = []

        # 标题和基本信息
        summary_parts.append(f"# {app_ref.project_name.get()} 项目总结与性能对比报告")
        summary_parts.append(f"**测试周期**：{app_ref.test_cycle.get()}")
        summary_parts.append(f"**参与厂家**：{app_ref.vendor_str.get()}")
        summary_parts.append(
            f"**测试模型**：{'、'.join(app_ref.selected_models) if app_ref.selected_models else '无'}"
        )
        summary_parts.append("")
        
        # 新增：客户和中标信息
        summary_parts.append("## 零、客户及中标信息")
        if app_ref.customer_name.get():
            summary_parts.append(f"- **客户名称**：{app_ref.customer_name.get()}")
        if app_ref.customer_industry.get():
            summary_parts.append(f"- **客户行业**：{app_ref.customer_industry.get()}")
        if app_ref.bid_status.get():
            summary_parts.append(f"- **中标情况**：{app_ref.bid_status.get()}")
            if app_ref.bid_status.get() == "已中标" and app_ref.bid_share.get():
                summary_parts.append(f"- **中标份额**：{app_ref.bid_share.get()}")
            elif app_ref.bid_status.get() == "未中标" and app_ref.bid_fail_reason.get():
                summary_parts.append(f"- **未中标原因**：{app_ref.bid_fail_reason.get()}")
        if app_ref.test_owner.get():
            summary_parts.append(f"- **测试负责人**：{app_ref.test_owner.get()}")
        summary_parts.append("")

        # 1. 项目概述
        summary_parts.append("## 一、项目概述")
        vendor_count = len(
            SummaryGenerator._parse_vendor_str(app_ref.vendor_str.get())
        )
        summary_parts.append(
            f"- 本次测试覆盖 {len(app_ref.selected_models)} 个模型，针对 {vendor_count} 家厂商的GPU性能进行验证。"
        )

        if app_ref.env_data:
            test_types = set([item["test_type"] for item in app_ref.env_data])
            summary_parts.append(
                f"- 测试类型包括 {', '.join(test_types)}，核心关注吞吐、延迟等关键指标。"
            )
        summary_parts.append("")

        # 2. 性能数据深度对比（以 H3C 厂商 GPU 为基准）
        summary_parts.append("## 二、性能数据横向对比（以 H3C GPU 为基准）")
        SummaryGenerator._add_performance_analysis_h3c(summary_parts, app_ref)
        summary_parts.append("")

        # 3. 项目问题与风险
        summary_parts.append("## 三、项目问题与风险")
        SummaryGenerator._add_problems_analysis(summary_parts, app_ref)
        summary_parts.append("")

        # 4. 结论与建议
        summary_parts.append("## 四、结论与建议")
        SummaryGenerator._add_conclusions(summary_parts, app_ref)
        summary_parts.append("")

        # 生成时间
        summary_parts.append(
            f"**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return "\n".join(summary_parts)

    @staticmethod
    def _parse_vendor_str(vendor_str):
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
    def _is_h3c_vendor(vendor_name: str) -> bool:
        if not vendor_name:
            return False
        return "h3c" in vendor_name.lower()

    @staticmethod
    def _add_performance_analysis_h3c(summary_parts, app_ref):
        """按照要求对性能进行 H3C 基准的逐模型逐 GPU 对比"""
        perf_data = getattr(app_ref, "perf_data", []) or []
        pk_data = getattr(app_ref, "pk_data", []) or []

        if not perf_data:
            summary_parts.append("- 暂无性能数据可用于对比分析。")
            return

        # 按 (model, test_type) 分组
        groups = {}
        for row in perf_data:
            key = (row.get("model", ""), row.get("test_type", ""))
            groups.setdefault(key, []).append(row)

        for (model, test_type), rows in groups.items():
            summary_parts.append(f"### 模型：{model} / 测试类型：{test_type}")

            # 找到 H3C 条目
            h3c_rows = [r for r in rows if SummaryGenerator._is_h3c_vendor(r.get("vendor", ""))]
            if not h3c_rows:
                summary_parts.append("- 无 H3C 厂商 GPU 卡的数据；跳过本模型的 H3C 对比。")
                summary_parts.append("")
                continue

            # 将其他厂商按 (vendor, gpu) 分组
            others = [r for r in rows if not SummaryGenerator._is_h3c_vendor(r.get("vendor", ""))]
            other_groups = {}
            for r in others:
                other_groups.setdefault((r.get("vendor", ""), r.get("gpu", "")), []).append(r)

            # H3C 可能有多款 GPU，需要分别对每款 GPU 进行对比
            h3c_gpu_types = {}
            for r in h3c_rows:
                h3c_gpu_types.setdefault(r.get("gpu", ""), []).append(r)

                # 使用 PK 表中为该 (model, test_type) 选择的指标作为对比指标
                # 如果未选择任何 PK 指标，则跳过本模型/测试类型的对比（按用户要求只体现 PK 指标）
                pk_map = {(p.get("model"), p.get("test_type")): p.get("selected_pk") for p in pk_data}
                selected_pk_raw = pk_map.get((model, test_type))
                if not selected_pk_raw:
                    summary_parts.append("- 未在 PK 表中选择对比指标，跳过本模型/测试类型的 PK 对比。")
                    summary_parts.append("")
                    continue

                # 允许用户在 PK 表中用逗号分隔选择多个指标
                metric_keys = set([k.strip() for k in str(selected_pk_raw).split(",") if k.strip()])

            def _mean_numeric(values):
                nums = []
                for v in values:
                    try:
                        nums.append(float(v))
                    except Exception:
                        continue
                return sum(nums) / len(nums) if nums else None

            # 文本类场景拆分需要额外处理
            is_text = test_type in ("文本推理", "图文推理")

            for h3c_gpu, h3c_list in h3c_gpu_types.items():
                summary_parts.append(f"- 基准：H3C GPU 型号 {h3c_gpu}（样本数 {len(h3c_list)}）")

                # 准备 H3C 指标均值（仅针对 PK 指标）
                h3c_metrics = {}
                for k in metric_keys:
                    vals = []
                    for r in h3c_list:
                        v = r.get("calc_values", {}).get(k)
                        if v is None:
                            v = r.get("input_values", {}).get(k)
                        if v is not None and str(v).strip() != "":
                            vals.append(v)
                    h3c_metrics[k] = _mean_numeric(vals)

                # 针对文本类模型按场景拆分
                if is_text:
                    # 三个固定场景：短输入长输出、长输入短输出、总上下文长度分级
                    scenarios = {
                        "短输入长输出": [],
                        "长输入短输出": [],
                        "总上下文短( <4096 )": [],
                        "总上下文中(4096-8191)": [],
                        "总上下文长( >=8192 )": [],
                    }
                    for r in rows:
                        iv = r.get("input_values", {})
                        try:
                            inp = float(iv.get("输入长度（tokens）", 0) or 0)
                            out = float(iv.get("输出长度（tokens）", 0) or 0)
                        except Exception:
                            inp = out = 0
                        total = inp + out
                        if inp < out:
                            scenarios["短输入长输出"].append(r)
                        elif inp > out:
                            scenarios["长输入短输出"].append(r)

                        if total < 4096:
                            scenarios["总上下文短( <4096 )"].append(r)
                        elif 4096 <= total <= 8191:
                            scenarios["总上下文中(4096-8191)"].append(r)
                        else:
                            scenarios["总上下文长( >=8192 )"].append(r)

                    for scen_name, scen_rows in scenarios.items():
                        if not scen_rows:
                            continue
                        summary_parts.append(f"  - 场景：{scen_name}（样本数 {len(scen_rows)}）")
                        # 计算场景内 H3C 均值
                        scen_h3c = [r for r in scen_rows if SummaryGenerator._is_h3c_vendor(r.get("vendor", "")) and r.get("gpu", "") == h3c_gpu]
                        if not scen_h3c:
                            summary_parts.append("    - 本场景下无 H3C 数据，跳过。")
                            continue
                        scen_h3c_metrics = {}
                        for k in metric_keys:
                            vals = []
                            for r in scen_h3c:
                                v = r.get("calc_values", {}).get(k) or r.get("input_values", {}).get(k)
                                if v is not None and str(v).strip() != "":
                                    vals.append(v)
                            scen_h3c_metrics[k] = _mean_numeric(vals)

                        # 对比场景内其他厂商
                        other_by_gpu = {}
                        for r in scen_rows:
                            if SummaryGenerator._is_h3c_vendor(r.get("vendor", "")):
                                continue
                            other_by_gpu.setdefault((r.get("vendor", ""), r.get("gpu", "")), []).append(r)

                        for (ovendor, ogpu), orows in other_by_gpu.items():
                            summary_parts.append(f"    - 对比对象：{ovendor} / GPU {ogpu}（样本数 {len(orows)}）")
                            for k in sorted(metric_keys):
                                hval = scen_h3c_metrics.get(k)
                                ovals = [row.get("calc_values", {}).get(k) or row.get("input_values", {}).get(k) for row in orows]
                                oval = _mean_numeric(ovals)
                                if hval is None or oval is None:
                                    continue
                                try:
                                    diff = hval - oval
                                    ratio = hval / oval if oval != 0 else float('inf')
                                except Exception:
                                    continue
                                summary_parts.append(f"      - 指标 {k}：H3C {hval:.2f} vs {ovendor} {oval:.2f}（差值 {diff:+.2f}，倍数 {ratio:.2f}x）")

                # 非文本或总体对比
                else:
                    # 对比所有其他厂商的每个 GPU
                    for (ovendor, ogpu), orows in other_groups.items():
                        summary_parts.append(f"  - 对比对象：{ovendor} / GPU {ogpu}（样本数 {len(orows)}）")
                        # 计算 other 的均值
                        other_metrics = {}
                        for k in metric_keys:
                            vals = []
                            for r in orows:
                                v = r.get("calc_values", {}).get(k) or r.get("input_values", {}).get(k)
                                if v is not None and str(v).strip() != "":
                                    vals.append(v)
                            other_metrics[k] = _mean_numeric(vals)

                        # 输出每个指标对比（以 H3C 均值为准）
                        for k in sorted(metric_keys):
                            hval = h3c_metrics.get(k)
                            oval = other_metrics.get(k)
                            if hval is None or oval is None:
                                continue
                            try:
                                diff = hval - oval
                                ratio = hval / oval if oval != 0 else float('inf')
                            except Exception:
                                continue
                            summary_parts.append(f"    - 指标 {k}：H3C {hval:.2f} vs {ovendor} {oval:.2f}（差值 {diff:+.2f}，倍数 {ratio:.2f}x）")

                summary_parts.append("")

    @staticmethod
    def _add_performance_analysis(summary_parts, app_ref):
        """添加性能分析部分"""
        if not app_ref.perf_data:
            summary_parts.append(
                "- 暂无有效性能测试数据，无法进行对比分析。"
            )
            return

        # 按测试类型分组
        test_type_groups = {}
        for perf_row in app_ref.perf_data:
            tt = perf_row["test_type"]
            if tt not in test_type_groups:
                test_type_groups[tt] = []
            test_type_groups[tt].append(perf_row)

        # 分析各测试类型
        for test_type, rows in test_type_groups.items():
            summary_parts.append(f"### 📊 {test_type} 性能对比")

            if test_type in ["文本推理", "图文推理"]:
                SummaryGenerator._analyze_inference(summary_parts, rows)
            elif test_type == "图像识别":
                SummaryGenerator._analyze_image_recognition(summary_parts, rows)

            summary_parts.append("")

    @staticmethod
    def _analyze_inference(summary_parts, rows):
        """分析推理性能"""
        metrics = []
        for row in rows:
            try:
                vendor = row["vendor"]
                model = row["model"]
                total_throughput = float(
                    row["input_values"].get("总吞吐（tokens/s）", 0)
                )
                single_throughput = float(
                    row["calc_values"].get("单卡输出吞吐（tokens/s）", 0)
                )
                ttft = float(row["input_values"].get("TTFT（ms）", 0))
                tpot = float(row["input_values"].get("TPOT（ms）", 0))

                metrics.append({
                    "vendor": vendor,
                    "model": model,
                    "total_throughput": total_throughput,
                    "single_throughput": single_throughput,
                    "ttft": ttft,
                    "tpot": tpot,
                })
            except (ValueError, KeyError):
                continue

        if metrics:
            # 按单卡吞吐排序
            metrics.sort(key=lambda x: x["single_throughput"], reverse=True)
            top_vendor = metrics[0]["vendor"]
            top_single = metrics[0]["single_throughput"]
            top_total = metrics[0]["total_throughput"]

            summary_parts.append(
                f"- **性能最优厂商**：{top_vendor}（单卡输出吞吐：{top_single:.2f} tokens/s，总吞吐：{top_total:.2f} tokens/s）"
            )
            summary_parts.append("- 详细对比：")
            for m in metrics:
                summary_parts.append(
                    f"  - {m['vendor']}（{m['model']}）：单卡吞吐 {m['single_throughput']:.2f} tokens/s，TTFT {m['ttft']:.0f} ms，TPOT {m['tpot']:.0f} ms"
                )

            # 延迟分析
            latency_metrics = [m for m in metrics if m["ttft"] > 0]
            if latency_metrics:
                latency_metrics.sort(key=lambda x: x["ttft"])
                best_latency_vendor = latency_metrics[0]["vendor"]
                best_latency = latency_metrics[0]["ttft"]
                summary_parts.append(
                    f"- **延迟最优厂商**：{best_latency_vendor}（TTFT：{best_latency:.0f} ms）"
                )

    @staticmethod
    def _analyze_image_recognition(summary_parts, rows):
        """分析图像识别性能"""
        fps_metrics = []
        for row in rows:
            try:
                vendor = row["vendor"]
                fps = float(row["input_values"].get("FPS", 0))
                fps_metrics.append({"vendor": vendor, "fps": fps})
            except (ValueError, KeyError):
                continue

        if fps_metrics:
            fps_metrics.sort(key=lambda x: x["fps"], reverse=True)
            top_vendor = fps_metrics[0]["vendor"]
            top_fps = fps_metrics[0]["fps"]

            summary_parts.append(
                f"- **性能最优厂商**：{top_vendor}（FPS：{top_fps:.2f}）"
            )
            summary_parts.append("- 详细对比：")
            for m in fps_metrics:
                summary_parts.append(f"  - {m['vendor']}：FPS {m['fps']:.2f}")

    @staticmethod
    def _add_problems_analysis(summary_parts, app_ref):
        """添加问题分析部分"""
        if app_ref.problem_data:
            tech_problems = [
                p for p in app_ref.problem_data if p["category"] == "技术问题"
            ]
            proj_problems = [
                p for p in app_ref.problem_data if p["category"] == "项目问题"
            ]

            if tech_problems:
                summary_parts.append(f"- **技术问题**：共 {len(tech_problems)} 个，主要包括：")
                for p in tech_problems:
                    solution = p["solution"] if p["solution"] else "待确认"
                    summary_parts.append(
                        f"  - {p['description']}（责任人：{p['person']}，解决方案：{solution}）"
                    )

            if proj_problems:
                summary_parts.append(f"- **项目问题**：共 {len(proj_problems)} 个，主要包括：")
                for p in proj_problems:
                    solution = p["solution"] if p["solution"] else "待确认"
                    summary_parts.append(
                        f"  - {p['description']}（责任人：{p['person']}，解决方案：{solution}）"
                    )
        else:
            summary_parts.append(
                "- 项目实施过程中未记录明显问题，整体进展顺利。"
            )

    @staticmethod
    def _add_conclusions(summary_parts, app_ref):
        """添加结论和建议"""
        if app_ref.perf_data and app_ref.pk_data:
            summary_parts.append("- **性能结论**：")
            summary_parts.append(
                "  综合对比各厂商数据，建议根据性能指标优先选择性能最优的厂商进行后续部署。"
            )
            summary_parts.append("- **优化建议**：")
            summary_parts.append(
                "  建议进一步排查模型推理框架或硬件配置以提升整体性能。"
            )
            if app_ref.problem_data:
                summary_parts.append(
                    "  针对已发现的问题，建议尽快推动解决方案落地，避免影响后续测试进度。"
                )
        else:
            summary_parts.append(
                "- 测试数据尚未完善，建议补充完整性能测试数据后再进行综合评估。"
            )
