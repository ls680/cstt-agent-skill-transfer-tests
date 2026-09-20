from cstt import (
    alfworld_objective_from_task_id,
    build_pair_record,
    lexical_similarity,
    operator_signature,
    procedural_contract,
    render_skill,
)


def source(task_id: str, family: str, description: str, actions: list[str]) -> dict:
    return {"task_id": task_id, "family": family, "task_description": description, "actions": actions}


def test_similarity_is_symmetric_and_bounded() -> None:
    left, right = "clean apple in sink", "put clean apple in cabinet"
    assert lexical_similarity(left, right) == lexical_similarity(right, left)
    assert 0 < lexical_similarity(left, right) < 1


def test_alfworld_objective_is_reconstructed_without_family_token() -> None:
    task_id = (
        "json_2.1.1/valid_seen/pick_clean_then_place_in_recep-"
        "ButterKnife-None-Drawer-30/trial/game.tw-pddl"
    )
    assert alfworld_objective_from_task_id(task_id) == "put a clean butter knife in drawer"


def test_operator_signature_ignores_unknown_actions() -> None:
    assert operator_signature(["GotoLocation(kitchen)", "Unknown(x)", "PickupObject(apple)"]) == [
        "GotoLocation",
        "PickupObject",
    ]


def test_procedural_contract_distinguishes_count_and_operation() -> None:
    assert procedural_contract(["PickupObject", "HeatObject", "PutObject"]) == {
        "object_count": 1,
        "operation": "HeatObject",
        "requires_placement": True,
    }
    assert procedural_contract(["PickupObject", "PutObject", "PickupObject", "PutObject"])["object_count"] == 2


def test_pair_cells_cross_procedure_and_surface() -> None:
    target = {"task_id": "target", "family": "clean", "task_description": "clean apple cabinet"}
    sources = [
        source("same-far", "clean", "wash mug drawer", ["CleanObject(mug)"]),
        source("same-near", "clean", "clean apple drawer", ["CleanObject(apple)"]),
        source("lure-far", "place", "move book shelf", ["PutObject(book,shelf)"]),
        source("lure-near", "place", "move apple cabinet", ["PutObject(apple,cabinet)"]),
    ]
    record = build_pair_record(target, sources)
    assert record["sources"]["matched_far"]["task_id"] == "same-far"
    assert record["sources"]["matched_near"]["task_id"] == "same-near"
    assert record["sources"]["lure_far"]["task_id"] == "lure-far"
    assert record["sources"]["lure_near"]["task_id"] == "lure-near"


def test_rendered_skill_removes_source_entities() -> None:
    skill = render_skill(source("s", "clean", "clean a mug", ["CleanObject(mug)"]))
    assert "clean a mug" not in skill
    assert "mug" not in skill
    assert "CURRENT objective" in skill
    assert "clean that object" in skill
    assert "object_count=1" in skill
