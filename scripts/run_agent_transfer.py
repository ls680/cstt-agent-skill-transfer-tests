#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


PROJECT = Path(__file__).resolve().parents[1]
PAPER1 = PROJECT.parent / "01_skilllineage"
sys.path.insert(0, str(PAPER1 / "src"))
from skilllineage.interactive import (  # noqa: E402
    ACTION_SYSTEM_PROMPT,
    LocalChatModel,
    action_prompt,
    fallback_action_index,
    parse_choice,
)
from skilllineage.interactive_envs import AlfworldEpisode  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append(path: Path, value: dict) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")
        handle.flush()


def state_signature(observation: str, objective: str, actions: list[str]) -> str:
    payload = {"observation": observation, "objective": objective, "actions": actions}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def choose_action(model: LocalChatModel, objective: str, skill: str, history: list, observation: str,
                  actions: list[str], config: dict, turn: int) -> tuple[str, dict]:
    prompt = action_prompt(
        task_description=objective,
        skill=skill,
        history=history[-config["history_turns"] :],
        observation=observation,
        admissible_actions=actions,
    )
    response = model.respond(
        ACTION_SYSTEM_PROMPT,
        prompt,
        max_new_tokens=config["max_new_tokens"],
        seed=config["seed"] + turn,
    )
    choice = parse_choice(response.text, len(actions))
    valid = choice is not None
    if choice is None:
        choice = fallback_action_index(actions)
    return actions[choice], {
        "response": asdict(response),
        "choice": choice,
        "valid": valid,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    }


def run_episode(model: LocalChatModel, task: dict, condition: str, skill: str, config: dict) -> dict:
    gamefile = Path(os.environ["ALFWORLD_DATA"]) / task["gamefile"]
    adapter = AlfworldEpisode(gamefile, max_steps=config["max_steps"], expert=False)
    try:
        observation, objective, actions = adapter.reset()
        initial = state_signature(observation, objective, actions)
        history: list[tuple[str, str]] = []
        turns = []
        score = 0.0
        started = time.perf_counter()
        for turn in range(config["max_steps"]):
            if not actions:
                break
            action, decision = choose_action(model, objective, skill, history, observation, actions, config, turn)
            new_observation, score, done, new_actions = adapter.step(action)
            turns.append({
                "turn": turn,
                "observation": observation,
                "admissible_actions": actions,
                "decision": decision,
                "action": action,
                "feedback": new_observation,
                "score": score,
                "done": done,
            })
            history.append((action, new_observation))
            observation, actions = new_observation, new_actions
            if done:
                break
        return {
            "task_id": task["task_id"],
            "family": task["family"],
            "condition": condition,
            "initial_state_sha256": initial,
            "objective": objective,
            "skill_sha256": hashlib.sha256(skill.encode()).hexdigest(),
            "success": score >= 0.999,
            "score": max(0.0, min(1.0, score)),
            "steps": len(turns),
            "invalid_outputs": sum(not row["decision"]["valid"] for row in turns),
            "input_tokens": sum(row["decision"]["response"]["input_tokens"] for row in turns),
            "output_tokens": sum(row["decision"]["response"]["output_tokens"] for row in turns),
            "elapsed_seconds": time.perf_counter() - started,
            "turns": turns,
        }
    finally:
        adapter.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "configs/development.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = PROJECT / config["output_dir"]
    pairs_path = output / "pairs.json"
    if not pairs_path.exists():
        raise FileNotFoundError("Run build_development_inputs.py first")
    pairs = json.loads(pairs_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    run_spec = {
        "config": config,
        "config_sha256": digest(args.config),
        "pairs_sha256": digest(pairs_path),
        "runner_sha256": digest(Path(__file__)),
        "paper1_interactive_sha256": digest(PAPER1 / "src/skilllineage/interactive.py"),
        "paper1_environments_sha256": digest(PAPER1 / "src/skilllineage/interactive_envs.py"),
    }
    spec_path = output / "run_spec.json"
    if spec_path.exists() and json.loads(spec_path.read_text()) != run_spec:
        raise ValueError("Run inputs differ from existing specification")
    if not spec_path.exists():
        spec_path.write_text(json.dumps(run_spec, ensure_ascii=False, indent=2) + "\n")
    episodes_path = output / "episodes.jsonl"
    saved = rows(episodes_path)
    completed = {(row["task_id"], row["condition"]) for row in saved}
    if len(completed) != len(saved):
        raise ValueError("Duplicate saved episode")
    initial_by_task = {}
    for row in saved:
        previous = initial_by_task.setdefault(row["task_id"], row["initial_state_sha256"])
        if previous != row["initial_state_sha256"]:
            raise ValueError("Existing state-matched block is inconsistent")
    model = LocalChatModel(config["model"]["id"], revision=config["model"]["revision"], local_files_only=True)
    started = time.perf_counter()
    for index, pair in enumerate(pairs["records"]):
        task = pair["target"]
        conditions = config["conditions"]
        shift = index % len(conditions)
        for condition in conditions[shift:] + conditions[:shift]:
            key = task["task_id"], condition
            if key in completed:
                continue
            skill = "" if condition == "no_skill" else pair["sources"][condition]["skill_text"]
            result = run_episode(model, task, condition, skill, config)
            previous = initial_by_task.setdefault(task["task_id"], result["initial_state_sha256"])
            if previous != result["initial_state_sha256"]:
                raise ValueError("Native arms did not start from the same state")
            append(episodes_path, result)
            completed.add(key)
            print(json.dumps({key: value for key, value in result.items() if key != "turns"}), flush=True)
    completion = {
        "status": "completed",
        "episodes": len(rows(episodes_path)),
        "target_blocks": len(pairs["records"]),
        "peak_cuda_memory_gib": model.torch.cuda.max_memory_reserved() / 1024**3,
        "elapsed_seconds_this_process": time.perf_counter() - started,
        "episodes_sha256": digest(episodes_path),
    }
    (output / "completion.json").write_text(json.dumps(completion, indent=2) + "\n")
    print(json.dumps(completion, indent=2), flush=True)


if __name__ == "__main__":
    main()
