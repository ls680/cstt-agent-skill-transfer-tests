from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Any


OPERATION_COMMAND = {
    "CleanObject": ("clean", "sinkbasin"),
    "HeatObject": ("heat", "microwave"),
    "CoolObject": ("cool", "fridge"),
    "ToggleObject": ("use", None),
}

SEARCH_PRIORITY = {
    name: rank
    for rank, name in enumerate(
        (
            "countertop", "diningtable", "coffeetable", "sidetable", "desk",
            "shelf", "bed", "sofa", "armchair", "coffeemachine", "stoveburner",
            "sinkbasin", "garbagecan", "toaster", "fridge", "microwave",
            "cabinet", "drawer", "safe",
        )
    )
}


@dataclass(frozen=True)
class TargetBinding:
    subject: str
    destination: str


@dataclass
class ExecutorState:
    visited: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)
    known_target_locations: list[str] = field(default_factory=list)
    placed_instances: set[str] = field(default_factory=set)
    transformed_instances: set[str] = field(default_factory=set)
    stage_locations_tried: set[str] = field(default_factory=set)
    holding: str | None = None
    current_location: str | None = None
    lamp_used: bool = False

    def public(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("visited", "opened", "placed_instances", "transformed_instances", "stage_locations_tried"):
            result[key] = sorted(result[key])
        return result


@dataclass(frozen=True)
class CandidateSelection:
    phase: str
    candidates: list[str]
    rejected: list[dict[str, str]]


def target_binding(task: dict[str, Any]) -> TargetBinding:
    family = task["family"]
    segment = task["task_id"].split("/")[2]
    prefix = family + "-"
    if not segment.startswith(prefix):
        raise ValueError(f"Task ID does not match family: {task['task_id']}")
    fields = segment[len(prefix) :].rsplit("-", 3)
    if len(fields) != 4:
        raise ValueError(f"Unexpected ALFWorld task identifier: {task['task_id']}")
    return TargetBinding(subject=fields[0].lower(), destination=fields[2].lower())


def _base_location(action_or_location: str) -> str:
    value = re.sub(r"^go to ", "", action_or_location)
    return re.sub(r"\s+\d+$", "", value)


def _search_key(action: str) -> tuple[int, str]:
    location = re.sub(r"^go to ", "", action)
    return SEARCH_PRIORITY.get(_base_location(location), len(SEARCH_PRIORITY)), location


class AuditableSkillExecutor:
    """Filter native actions using only a target binding and a source contract."""

    def __init__(self, binding: TargetBinding, contract: dict[str, Any] | None, mode: str, search_width: int = 5):
        if mode not in {"raw", "binding", "skill"}:
            raise ValueError(f"Unknown executor mode: {mode}")
        if mode == "skill" and contract is None:
            raise ValueError("Skill mode requires a source contract")
        self.binding = binding
        self.contract = contract
        self.mode = mode
        self.search_width = search_width
        self.state = ExecutorState()

    def record(self, action: str) -> None:
        if action.startswith("go to "):
            location = action.removeprefix("go to ")
            self.state.current_location = location
            self.state.visited.add(location)
            if self.state.holding is not None:
                self.state.stage_locations_tried.add(location)
        elif action.startswith("open "):
            self.state.opened.add(action.removeprefix("open "))
        elif action.startswith("take "):
            match = re.match(r"take (.+?) from (.+)$", action)
            if match:
                self.state.holding = match.group(1)
                self.state.stage_locations_tried.clear()
        elif action.startswith(("clean ", "heat ", "cool ")):
            match = re.match(r"(?:clean|heat|cool) (.+?) with ", action)
            if match:
                self.state.transformed_instances.add(match.group(1))
                self.state.stage_locations_tried.clear()
        elif action.startswith("use "):
            self.state.lamp_used = True
        elif action.startswith("move "):
            match = re.match(r"move (.+?) to (.+)$", action)
            if match:
                instance, destination = match.groups()
                if _base_location(destination) == self.binding.destination:
                    self.state.placed_instances.add(instance)
                if self.state.holding == instance:
                    self.state.holding = None
                    self.state.stage_locations_tried.clear()

    def _target_take_actions(self, actions: list[str]) -> list[str]:
        prefix = f"take {self.binding.subject} "
        result = []
        for action in actions:
            if not action.startswith(prefix):
                continue
            match = re.match(r"take (.+?) from (.+)$", action)
            if match and match.group(1) not in self.state.placed_instances:
                result.append(action)
                location = match.group(2)
                if location not in self.state.known_target_locations:
                    self.state.known_target_locations.append(location)
        return sorted(result)

    def _goto(self, actions: list[str], base: str) -> list[str]:
        return sorted(
            action for action in actions
            if action.startswith("go to ")
            and _base_location(action) == base
            and action.removeprefix("go to ") != self.state.current_location
            and action.removeprefix("go to ") not in self.state.stage_locations_tried
        )

    def _open_current(self, actions: list[str]) -> list[str]:
        if self.state.current_location is None:
            return []
        wanted = f"open {self.state.current_location}"
        return [wanted] if wanted in actions else []

    def _search(self, actions: list[str]) -> CandidateSelection:
        take = self._target_take_actions(actions)
        if take:
            return self._selection("acquire_target", take, actions)
        opening = self._open_current(actions)
        if opening:
            return self._selection("inspect_closed_receptacle", opening, actions)
        known = [
            f"go to {location}" for location in self.state.known_target_locations
            if f"go to {location}" in actions and location != self.state.current_location
        ]
        if known:
            return self._selection("return_to_known_target", known[: self.search_width], actions)
        unseen = sorted(
            (action for action in actions if action.startswith("go to ") and action.removeprefix("go to ") not in self.state.visited),
            key=_search_key,
        )
        if unseen:
            return self._selection("systematic_search", unseen[: self.search_width], actions)
        remaining = sorted((action for action in actions if action.startswith("go to ")), key=_search_key)
        if remaining:
            return self._selection("search_exhausted_revisit", remaining[:1], actions)
        return self._selection("no_navigation", self._benign(actions), actions)

    def _skill_candidates(self, actions: list[str]) -> CandidateSelection:
        assert self.contract is not None
        desired_count = int(self.contract["object_count"])
        operation = str(self.contract["operation"])
        if self.state.holding is None:
            if len(self.state.placed_instances) >= desired_count:
                return self._selection("source_contract_complete_target_not_done", self._benign(actions), actions)
            return self._search(actions)

        held = self.state.holding
        if operation in OPERATION_COMMAND and held not in self.state.transformed_instances:
            command, fixed_device = OPERATION_COMMAND[operation]
            if operation == "ToggleObject":
                direct = sorted(action for action in actions if action.startswith(f"use {self.binding.destination} "))
                if direct:
                    return self._selection("apply_source_operation", direct, actions)
                device = self.binding.destination
            else:
                direct = sorted(action for action in actions if action.startswith(f"{command} {held} with "))
                if direct:
                    return self._selection("apply_source_operation", direct, actions)
                device = str(fixed_device)
            opening = self._open_current(actions)
            if opening and _base_location(self.state.current_location or "") == device:
                return self._selection("open_source_device", opening, actions)
            goto = self._goto(actions, device)
            if goto:
                return self._selection("navigate_to_source_device", goto, actions)
            return self._selection("source_device_unavailable", self._benign(actions), actions)

        if not bool(self.contract["requires_placement"]):
            return self._selection("source_contract_complete_target_not_done", self._benign(actions), actions)
        moves = sorted(action for action in actions if action.startswith(f"move {held} to {self.binding.destination} "))
        if moves:
            return self._selection("place_target", moves, actions)
        opening = self._open_current(actions)
        if opening and _base_location(self.state.current_location or "") == self.binding.destination:
            return self._selection("open_destination", opening, actions)
        goto = self._goto(actions, self.binding.destination)
        if goto:
            return self._selection("navigate_to_destination", goto, actions)
        return self._selection("destination_unavailable", self._benign(actions), actions)

    def _binding_candidates(self, actions: list[str]) -> CandidateSelection:
        target_takes = self._target_take_actions(actions)
        if target_takes:
            return self._selection("binding_only_acquire", target_takes, actions)
        opening = self._open_current(actions)
        if self.state.holding is None and opening:
            return self._selection("binding_only_inspect", opening, actions)
        relevant = []
        for action in actions:
            if action.startswith("take "):
                continue
            if action.startswith(("move ", "clean ", "heat ", "cool ")):
                prefixes = tuple(f"{verb} {self.state.holding}" for verb in ("move", "clean", "heat", "cool"))
                if self.state.holding is None or not action.startswith(prefixes):
                    continue
            relevant.append(action)
        useful = [action for action in relevant if action not in {"help", "inventory", "look"} and not action.startswith("examine ")]
        direct = [action for action in useful if not action.startswith("go to ")]
        unseen_go = sorted(
            (
                action for action in useful
                if action.startswith("go to ") and action.removeprefix("go to ") not in self.state.visited
            ),
            key=lambda action: (0 if _base_location(action) == self.binding.destination else 1, _search_key(action)),
        )
        candidates = direct + unseen_go
        if not candidates:
            candidates = sorted((action for action in useful if action.startswith("go to ")), key=_search_key)
        candidates = candidates or self._benign(actions)
        return self._selection("binding_only", candidates[: max(self.search_width, 8)], actions)

    @staticmethod
    def _benign(actions: list[str]) -> list[str]:
        return ["look"] if "look" in actions else actions[:1]

    @staticmethod
    def _selection(phase: str, candidates: list[str], actions: list[str]) -> CandidateSelection:
        selected = set(candidates)
        rejected = [{"action": action, "reason": f"excluded_by_{phase}"} for action in actions if action not in selected]
        return CandidateSelection(phase=phase, candidates=candidates, rejected=rejected)

    def select(self, actions: list[str]) -> CandidateSelection:
        if not actions:
            return CandidateSelection("no_admissible_actions", [], [])
        if self.mode == "raw":
            return self._selection("unfiltered", actions, actions)
        if self.mode == "binding":
            return self._binding_candidates(actions)
        return self._skill_candidates(actions)
