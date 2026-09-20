from __future__ import annotations

from collections import Counter
import math
import re
from typing import Any


OPERATOR_TEXT = {
    "GotoLocation": "Navigate to the location required for the next operation.",
    "PickupObject": "Acquire one currently required target object and verify that it is held.",
    "PutObject": "Place the held target object at the current objective's requested destination.",
    "CleanObject": "Clean the held target with an available cleaning fixture before final placement.",
    "HeatObject": "Heat the held target with an available heating fixture before final placement.",
    "CoolObject": "Cool the held target with an available cooling fixture before final placement.",
    "ToggleObject": "Activate the objective-relevant device while the required target is available.",
    "NoOp": "Stop only after environment feedback confirms the objective.",
}

OBJECTIVE_TEMPLATES = {
    "pick_and_place_simple": "move {subject} to {destination}",
    "pick_clean_then_place_in_recep": "put a clean {subject} in {destination}",
    "pick_heat_then_place_in_recep": "put a hot {subject} in {destination}",
    "pick_cool_then_place_in_recep": "put a cool {subject} in {destination}",
    "look_at_obj_in_light": "look at {subject} under the light of {destination}",
    "pick_two_obj_and_place": "put two {subject} in {destination}",
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def lexical_similarity(left: str, right: str) -> float:
    """Cosine similarity over transparent unigram counts."""
    a, b = Counter(tokens(left)), Counter(tokens(right))
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    return dot / math.sqrt(sum(value * value for value in a.values()) * sum(value * value for value in b.values()))


def _words(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).lower()


def alfworld_objective_from_task_id(task_id: str) -> str:
    segment = task_id.split("/")[2]
    family = next((name for name in OBJECTIVE_TEMPLATES if segment.startswith(name + "-")), None)
    if family is None:
        raise ValueError(f"Unsupported ALFWorld family in {task_id}")
    fields = segment[len(family) + 1 :].rsplit("-", 3)
    if len(fields) != 4:
        raise ValueError(f"Unexpected ALFWorld task identifier: {task_id}")
    subject, _, destination, _ = fields
    return OBJECTIVE_TEMPLATES[family].format(
        subject=_words(subject),
        destination=_words(destination),
    )


def operator_signature(actions: list[str]) -> list[str]:
    result: list[str] = []
    for action in actions:
        match = re.match(r"([A-Za-z]+)\(", action)
        if not match:
            continue
        operator = match.group(1)
        if operator in OPERATOR_TEXT:
            result.append(operator)
    return result


def procedural_contract(signature: list[str]) -> dict[str, Any]:
    """Compile a source trace into the small contract exposed to the executor."""
    operation = next(
        (name for name in ("CleanObject", "HeatObject", "CoolObject", "ToggleObject") if name in signature),
        "None",
    )
    return {
        "object_count": 2 if signature.count("PickupObject") >= 2 and signature.count("PutObject") >= 2 else 1,
        "operation": operation,
        "requires_placement": "PutObject" in signature,
    }


def render_skill(source: dict[str, Any]) -> str:
    signature = operator_signature(source["actions"])
    contract = procedural_contract(signature)
    if signature.count("PickupObject") >= 2 and signature.count("PutObject") >= 2:
        stages = [
            "Locate and acquire one object matching the CURRENT objective.",
            "Navigate to the CURRENT destination and place that object there.",
            "Locate a different object of the same requested type.",
            "Acquire it, return to the CURRENT destination, and place it there.",
        ]
    elif "CleanObject" in signature:
        stages = [
            "Locate and acquire the object named by the CURRENT objective.",
            "Navigate to an available sink basin and clean that object.",
            "Only after cleaning succeeds, navigate to the CURRENT destination and place it there.",
        ]
    elif "HeatObject" in signature:
        stages = [
            "Locate and acquire the object named by the CURRENT objective.",
            "Navigate to an available microwave, open it if needed, and heat that object.",
            "Only after heating succeeds, navigate to the CURRENT destination and place it there.",
        ]
    elif "CoolObject" in signature:
        stages = [
            "Locate and acquire the object named by the CURRENT objective.",
            "Navigate to an available refrigerator, open it if needed, and cool that object.",
            "Only after cooling succeeds, navigate to the CURRENT destination and place it there.",
        ]
    elif "ToggleObject" in signature:
        stages = [
            "Locate and acquire the object named by the CURRENT objective.",
            "Navigate to the objective-relevant lamp and use or activate it while retaining the target.",
            "Stop when environment feedback confirms that the target has been examined under the light.",
        ]
    else:
        stages = [
            "Locate and acquire the object named by the CURRENT objective.",
            "Navigate to the CURRENT objective's destination.",
            "Place the held target at that destination and stop after confirmation.",
        ]
    procedure = "\n".join(f"{index}. {stage}" for index, stage in enumerate(stages, start=1))
    signature_text = " -> ".join(
        operator for operator in signature if operator not in {"GotoLocation", "NoOp"}
    )
    return f"""Verified role-normalized procedure
Source witness operator signature: {signature_text}
Executable contract: object_count={contract['object_count']}; operation={contract['operation']}; requires_placement={str(contract['requires_placement']).lower()}

Transfer rules:
- Bind every subject, count, device, and destination from the CURRENT objective; source entity names are intentionally absent.
- During search, systematically inspect new locations or containers. Do not loop between already inspected locations.
- Never acquire or transform an object whose type does not match the CURRENT target.
- Follow actual feedback and choose only a currently admissible command.

Procedure:
{procedure}"""


def _ranked(target_text: str, sources: list[dict[str, Any]]) -> list[tuple[float, str, dict[str, Any]]]:
    return sorted(
        (
            lexical_similarity(target_text, source["task_description"]),
            source["task_id"],
            source,
        )
        for source in sources
    )


def build_pair_record(target: dict[str, Any], sources: list[dict[str, Any]]) -> dict[str, Any]:
    same = [source for source in sources if source["family"] == target["family"]]
    different = [source for source in sources if source["family"] != target["family"]]
    if len(same) < 2 or len(different) < 2:
        raise ValueError("Each target requires at least two matched and two mismatched sources")
    same_ranked = _ranked(target["task_description"], same)
    different_ranked = _ranked(target["task_description"], different)
    selected = {
        "matched_far": same_ranked[0],
        "matched_near": same_ranked[-1],
        "lure_far": different_ranked[0],
        "lure_near": different_ranked[-1],
    }
    return {
        "target": target,
        "sources": {
            condition: {
                "lexical_similarity": score,
                "task_id": source["task_id"],
                "family": source["family"],
                "task_description": source["task_description"],
                "operator_signature": operator_signature(source["actions"]),
                "procedural_contract": procedural_contract(operator_signature(source["actions"])),
                "skill_text": render_skill(source),
            }
            for condition, (score, _, source) in selected.items()
        },
    }
