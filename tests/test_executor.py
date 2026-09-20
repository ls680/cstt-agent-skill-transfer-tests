from cstt.executor import AuditableSkillExecutor, TargetBinding, target_binding, target_binding_from_objective


def executor(operation: str = "None", count: int = 1) -> AuditableSkillExecutor:
    return AuditableSkillExecutor(
        TargetBinding("apple", "diningtable"),
        {"object_count": count, "operation": operation, "requires_placement": True},
        "skill",
    )


def test_target_binding_comes_from_task_identity() -> None:
    task = {
        "family": "pick_heat_then_place_in_recep",
        "task_id": "json_2.1.1/valid_seen/pick_heat_then_place_in_recep-Apple-None-DiningTable-26/t/game.tw-pddl",
    }
    assert target_binding(task) == TargetBinding("apple", "diningtable")


def test_target_binding_is_parsed_from_environment_objective() -> None:
    assert target_binding_from_objective(
        "pick_clean_then_place_in_recep",
        "Your task is to: clean some butter knife and put it in coffee machine.",
    ) == TargetBinding("butterknife", "coffeemachine")
    assert target_binding_from_objective(
        "look_at_obj_in_light",
        "Your task is to: examine the bowl with the desklamp.",
    ) == TargetBinding("bowl", "desklamp")
    assert target_binding_from_objective(
        "pick_clean_then_place_in_recep",
        "Your task is to: put a clean butter knife in drawer.",
    ) == TargetBinding("butterknife", "drawer")
    assert target_binding_from_objective(
        "pick_heat_then_place_in_recep",
        "Your task is to: put a hot potato in fridge.",
    ) == TargetBinding("potato", "fridge")
    assert target_binding_from_objective(
        "pick_cool_then_place_in_recep",
        "Your task is to: put a cool tomato in microwave.",
    ) == TargetBinding("tomato", "microwave")
    assert target_binding_from_objective(
        "pick_two_obj_and_place",
        "Your task is to: put two key chain in safe.",
    ) == TargetBinding("keychain", "safe")


def test_skill_executor_rejects_wrong_object_and_follows_contract() -> None:
    agent = executor("HeatObject")
    agent.observe(["take egg 1 from table 1", "take apple 2 from table 1", "look"])
    first = agent.select(["take egg 1 from table 1", "take apple 2 from table 1", "look"])
    assert first.phase == "acquire_target"
    assert first.candidates == ["take apple 2 from table 1"]
    agent.record(first.candidates[0])
    second = agent.select(["go to microwave 1", "go to diningtable 1", "inventory"])
    assert second.phase == "navigate_to_source_device"
    assert second.candidates == ["go to microwave 1"]
    agent.record(second.candidates[0])
    third = agent.select(["heat apple 2 with microwave 1", "go to diningtable 1"])
    assert third.candidates == ["heat apple 2 with microwave 1"]


def test_observation_update_is_explicit_and_monotone() -> None:
    agent = executor()
    agent.observe(["take apple 1 from countertop 1", "take egg 1 from countertop 1"])
    assert agent.state.known_target_locations == ["countertop 1"]
    agent.observe(["take apple 2 from sidetable 1"])
    assert agent.state.known_target_locations == ["countertop 1", "sidetable 1"]


def test_two_object_contract_does_not_retake_placed_instance() -> None:
    agent = executor(count=2)
    agent.record("take apple 1 from countertop 1")
    agent.record("go to diningtable 1")
    agent.record("move apple 1 to diningtable 1")
    selection = agent.select([
        "take apple 1 from diningtable 1",
        "go to countertop 1",
        "go to cabinet 1",
    ])
    assert selection.phase != "acquire_target"
    assert "take apple 1 from diningtable 1" not in selection.candidates


def test_binding_only_filters_wrong_object_without_adding_a_procedure() -> None:
    agent = AuditableSkillExecutor(TargetBinding("mug", "cabinet"), None, "binding")
    selection = agent.select([
        "take apple 1 from table 1",
        "take mug 1 from table 1",
        "go to sinkbasin 1",
        "look",
    ])
    assert selection.phase == "binding_only_acquire"
    assert "take apple 1 from table 1" not in selection.candidates
    assert "take mug 1 from table 1" in selection.candidates


def test_binding_only_opens_current_container_before_leaving() -> None:
    agent = AuditableSkillExecutor(TargetBinding("mug", "cabinet"), None, "binding")
    agent.record("go to drawer 1")
    selection = agent.select(["open drawer 1", "go to cabinet 1", "go to countertop 1", "look"])
    assert selection.phase == "binding_only_inspect"
    assert selection.candidates == ["open drawer 1"]


def test_skill_device_navigation_does_not_cycle_between_instances() -> None:
    agent = executor("CleanObject")
    agent.record("take apple 1 from countertop 1")
    first = agent.select(["go to sinkbasin 1", "go to sinkbasin 2", "look"])
    agent.record(first.candidates[0])
    second = agent.select(["go to sinkbasin 2", "look"])
    agent.record(second.candidates[0])
    terminal = agent.select(["go to sinkbasin 1", "look"])
    assert terminal.phase == "source_device_unavailable"


def test_toggle_contract_searches_receptacles_for_non_navigable_device() -> None:
    agent = AuditableSkillExecutor(
        TargetBinding("cd", "desklamp"),
        {"object_count": 1, "operation": "ToggleObject", "requires_placement": False},
        "skill",
        search_width=2,
    )
    agent.record("take cd 1 from shelf 1")
    search = agent.select(["go to desk 1", "go to sidetable 1", "look"])
    assert search.phase == "search_for_source_device"
    agent.record(search.candidates[0])
    apply = agent.select(["use desklamp 1", "go to sidetable 1", "look"])
    assert apply.phase == "apply_source_operation"
    agent.record("use desklamp 1")
    assert "cd 1" in agent.state.transformed_instances
