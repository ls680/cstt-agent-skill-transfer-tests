#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT = Path(__file__).resolve().parents[1]
SUMMARY = PROJECT / "results/confirmation/analysis/summary.json"


def percent(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}"


def p_value(value: float) -> str:
    if value < 0.0001:
        mantissa, exponent = f"{value:.2e}".split("e")
        return rf"{mantissa}\times 10^{{{int(exponent)}}}"
    return f"{value:.4f}"


def tex(value: str) -> str:
    return value.replace("_", r"\_")


def write_macros(result: dict) -> None:
    design = result["design"]
    summary = result["summary"]
    primary = result["primary"]
    causal = result["causal_vs_binding_only"]
    ci_low, ci_high = primary["bootstrap_95ci"]
    macro_low, macro_high = primary["family_macro_bootstrap_95ci"]
    values = {
        "TargetCount": str(design["targets"]),
        "ModelCount": str(len(design["models"])),
        "BlockCount": str(design["target_model_blocks"]),
        "EpisodeCount": str(design["episodes"]),
        "MatchedFarRate": percent(summary["matched_far"]["success_rate"]),
        "LureNearRate": percent(summary["lure_near"]["success_rate"]),
        "BindingRate": percent(summary["binding_only"]["success_rate"]),
        "PrimaryEffect": percent(primary["effect"]),
        "PrimaryCILow": percent(ci_low),
        "PrimaryCIHigh": percent(ci_high),
        "MacroEffect": percent(primary["family_macro_effect"]),
        "MacroCILow": percent(macro_low),
        "MacroCIHigh": percent(macro_high),
        "RandomizationP": p_value(primary["task_clustered_randomization_p_one_sided"]),
        "CausalNet": percent(causal["net_effect"]),
        "HarmRate": percent(causal["harm_rate"]),
        "HelpfulCount": str(causal["helpful"]),
        "HarmfulCount": str(causal["harmful"]),
    }
    lines = [f"\\newcommand{{\\{key}}}{{{value}}}" for key, value in values.items()]
    (PROJECT / "paper/results_macros.tex").write_text("\n".join(lines) + "\n")


def write_main_table(result: dict) -> None:
    summary = result["summary"]
    labels = {
        "no_skill": "No skill",
        "binding_only": "Binding only",
        "matched_near": "Matched, near",
        "matched_far": "Matched, far",
        "lure_near": "Lure, near",
        "lure_far": "Lure, far",
    }
    rows = []
    for condition in result["design"]["conditions"]:
        item = summary[condition]
        rows.append(
            f"{labels[condition]} & {item['successes']}/{item['episodes']} & "
            f"{percent(item['success_rate'])} & {item['mean_steps']:.1f} \\\\"
        )
    table = """\\begin{table}[t]
\\centering
\\caption{Frozen confirmation outcomes. Success rate is over target--model blocks; steps include failed runs.}
\\label{tab:main}
\\begin{tabular}{lrrr}
\\toprule
Condition & Successes & Rate (\\%) & Mean steps \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    output = PROJECT / "results/confirmation/analysis"
    (output / "table_main.tex").write_text(table)
    labels_zh = {
        "no_skill": "\\mbox{无 Skill}",
        "binding_only": "\\mbox{仅绑定}",
        "matched_near": "\\mbox{匹配、词面近}",
        "matched_far": "\\mbox{匹配、词面远}",
        "lure_near": "\\mbox{诱饵、词面近}",
        "lure_far": "\\mbox{诱饵、词面远}",
    }
    rows_zh = []
    for condition in result["design"]["conditions"]:
        item = summary[condition]
        rows_zh.append(
            f"{labels_zh[condition]} & {item['successes']}/{item['episodes']} & "
            f"{percent(item['success_rate'])} & {item['mean_steps']:.1f} \\\\"
        )
    table_zh = """\\begin{table}[t]
\\centering
\\caption{冻结确认结果。成功率的分母是目标--模型块；平均步数包含失败执行。}
\\label{tab:main}
\\begin{tabular}{lrrr}
\\toprule
条件 & 成功数 & 成功率 (\\%) & 平均步数 \\\\
\\midrule
""" + "\n".join(rows_zh) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    (output / "table_main_zh.tex").write_text(table_zh)


def write_effect_tables(result: dict) -> None:
    primary = result["primary"]
    model_labels = {
        "qwen3_4b": "Qwen3-4B",
        "phi4_mini": "Phi-4-mini",
        "mistral7b_v03": "Mistral-7B-v0.3",
    }
    family_labels = {
        "pick_and_place_simple": "Simple placement",
        "pick_clean_then_place_in_recep": "Clean then place",
        "pick_heat_then_place_in_recep": "Heat then place",
        "pick_cool_then_place_in_recep": "Cool then place",
        "look_at_obj_in_light": "Look under light",
        "pick_two_obj_and_place": "Two-object placement",
    }
    model_rows = [
        f"{model_labels.get(name, tex(name))} & {percent(value)} \\\\"
        for name, value in primary["by_model"].items()
    ]
    family_rows = [
        f"{family_labels.get(name, tex(name))} & {percent(value)} \\\\"
        for name, value in primary["by_family"].items()
    ]
    output = PROJECT / "results/confirmation/analysis"
    (output / "table_by_model.tex").write_text(
        "\\begin{table}[t]\n\\centering\n"
        "\\caption{Primary matched-far minus lure-near effect by model.}\n"
        "\\label{tab:model}\n\\begin{tabular}{lr}\n\\toprule\nModel & Effect (pp) \\\\\n\\midrule\n" + "\n".join(model_rows) +
        "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    (output / "table_by_family.tex").write_text(
        "\\begin{table}[t]\n\\centering\n"
        "\\caption{Primary effect by native ALFWorld task family.}\n"
        "\\label{tab:family}\n\\begin{tabular}{lr}\n\\toprule\nFamily & Effect (pp) \\\\\n\\midrule\n" + "\n".join(family_rows) +
        "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    family_zh = {
        "pick_and_place_simple": "简单放置",
        "pick_clean_then_place_in_recep": "清洗后放置",
        "pick_heat_then_place_in_recep": "加热后放置",
        "pick_cool_then_place_in_recep": "冷却后放置",
        "look_at_obj_in_light": "灯下查看",
        "pick_two_obj_and_place": "双对象放置",
    }
    family_rows_zh = [
        f"{family_zh.get(name, tex(name))} & {percent(value)} \\\\"
        for name, value in primary["by_family"].items()
    ]
    (output / "table_by_model_zh.tex").write_text(
        "\\begin{table}[t]\n\\centering\n"
        "\\caption{各模型的主效应（匹配远减诱饵近）。}\n"
        "\\label{tab:model}\n\\begin{tabular}{lr}\n\\toprule\n模型 & 效应（百分点） \\\\\n\\midrule\n" + "\n".join(model_rows) +
        "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    (output / "table_by_family_zh.tex").write_text(
        "\\begin{table}[t]\n\\centering\n"
        "\\caption{各 ALFWorld 原生任务族的主效应。}\n"
        "\\label{tab:family}\n\\begin{tabular}{lr}\n\\toprule\n任务族 & 效应（百分点） \\\\\n\\midrule\n" + "\n".join(family_rows_zh) +
        "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def write_figure(result: dict) -> None:
    summary = result["summary"]
    conditions = result["design"]["conditions"]
    labels = ["No skill", "Binding", "Match\nnear", "Match\nfar", "Lure\nnear", "Lure\nfar"]
    rates = [100 * summary[key]["success_rate"] for key in conditions]
    colors = ["#707070", "#466A7F", "#248277", "#176B5B", "#C46A35", "#A33D32"]
    figure, axis = plt.subplots(figsize=(7.2, 3.7))
    bars = axis.bar(labels, rates, color=colors, width=0.72)
    axis.set_ylabel("Native task success (%)")
    axis.set_ylim(0, 105)
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color="#dddddd", linewidth=0.7)
    axis.set_axisbelow(True)
    axis.bar_label(bars, labels=[f"{value:.1f}" for value in rates], padding=3, fontsize=8)
    figure.tight_layout()
    output = PROJECT / "results/figures"
    output.mkdir(parents=True, exist_ok=True)
    figure.savefig(output / "condition_success.pdf", bbox_inches="tight")
    figure.savefig(output / "condition_success.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    if not SUMMARY.exists():
        raise SystemExit(f"Missing final confirmation summary: {SUMMARY}")
    result = json.loads(SUMMARY.read_text())
    if not result.get("all_gates_pass"):
        raise SystemExit("Confirmation gates did not all pass; paper assets not rendered")
    write_macros(result)
    write_main_table(result)
    write_effect_tables(result)
    write_figure(result)
    print("paper macros, tables, and figures rendered")


if __name__ == "__main__":
    main()
