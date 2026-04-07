import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load_json(name: str) -> dict:
    path = ROOT / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_label_policy(data: dict) -> None:
    labels = data.get("labels", [])
    names = {label.get("name") for label in labels}
    required = {"Indoor", "Outdoor", "Mixed", "Unclear"}

    _assert(required.issubset(names), "label_policy.json missing required labels")
    _assert(data.get("abstain_policy", {}).get("enabled") is True, "abstain_policy.enabled must be true")



def validate_release_gates(data: dict) -> None:
    thresholds = data.get("evaluation", {}).get("thresholds", {})
    required_keys = {
        "macro_f1",
        "accuracy",
        "indoor_recall",
        "outdoor_recall",
        "ece_max",
        "p95_latency_ms",
    }

    _assert(required_keys.issubset(thresholds.keys()), "release_gates.json missing thresholds")
    _assert(float(thresholds["macro_f1"]) >= 0.9, "macro_f1 threshold should be at least 0.9")



def validate_edge_cases(data: dict) -> None:
    rules = data.get("rules", [])
    _assert(len(rules) >= 4, "edge_case_policy.json should include at least 4 rules")

    commute_rule = [rule for rule in rules if rule.get("id") == "COMMUTE_001"]
    _assert(bool(commute_rule), "COMMUTE_001 rule is required")
    _assert(commute_rule[0].get("default_label") == "Outdoor", "COMMUTE_001 must default to Outdoor")



def main() -> None:
    label_policy = _load_json("label_policy.json")
    release_gates = _load_json("release_gates.json")
    edge_case_policy = _load_json("edge_case_policy.json")

    validate_label_policy(label_policy)
    validate_release_gates(release_gates)
    validate_edge_cases(edge_case_policy)

    print("Phase 0 validation passed")


if __name__ == "__main__":
    main()
