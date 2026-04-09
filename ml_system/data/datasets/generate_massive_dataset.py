"""
Massive synthetic English activity dataset generator.

This generator is designed to create broad lexical coverage with:
- clean templates
- paraphrase variants
- typo and grammar noise variants
- balanced label splits for Indoor/Outdoor/Mixed/Unclear

Usage:
  python -m ml_system.data.datasets.generate_massive_dataset --per-label 60000 --output-dir ml_system/data/datasets
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Dict, List


RNG = random.Random(42)

INDOOR_VERBS = [
    "read", "study", "write", "work", "code", "draw", "paint", "cook", "bake",
    "clean", "organize", "practice", "watch", "listen", "meditate", "exercise",
    "meet", "present", "design", "review", "edit", "learn", "research", "assemble",
]

OUTDOOR_VERBS = [
    "run", "walk", "hike", "cycle", "jog", "camp", "fish", "swim", "climb",
    "garden", "mow", "travel", "commute", "shop", "explore", "play", "race",
    "trek", "train", "surf", "kayak", "skate", "photograph", "patrol",
]

MIXED_VERBS = [
    "commute", "transfer", "visit", "attend", "travel", "move", "switch", "work",
    "study", "shop", "tour", "coordinate", "manage", "plan",
]

UNCLEAR_VERBS = [
    "think", "plan", "consider", "reflect", "pause", "wait", "decide", "review",
    "process", "start", "stop", "continue", "prepare", "arrange", "handle",
]

INDOOR_OBJECTS = [
    "a report", "homework", "a coding task", "a design draft", "a recipe", "laundry",
    "documents", "a presentation", "a workshop", "a board game", "a puzzle", "emails",
    "a lesson", "music practice", "a budget sheet", "a project brief", "an article",
]

OUTDOOR_OBJECTS = [
    "a trail", "a park route", "the neighborhood", "the field", "the beach", "the road",
    "the market", "the tobacco shop", "a grocery store", "the stadium", "a campsite",
    "a mountain path", "a river route", "a cycling lane", "the courtyard",
]

MIXED_OBJECTS = [
    "an airport transfer", "a station commute", "a campus day", "a mall visit",
    "a hotel event", "a conference center", "a mixed-use complex", "a logistics run",
    "an indoor-outdoor event", "a venue tour", "a hub visit",
]

UNCLEAR_OBJECTS = [
    "something important", "some task", "an activity", "a pending item", "a routine",
    "something productive", "a plan", "a personal thing", "an errand", "a future action",
]

TIME_CONTEXTS = [
    "this morning", "this afternoon", "tonight", "later today", "tomorrow morning",
    "this weekend", "after lunch", "before dinner", "right now", "soon",
]

STYLE_PREFIXES = [
    "I need to", "I want to", "I am going to", "I am", "I'm", "Can we", "Let's",
    "We are", "Planning to", "Currently", "Today I will", "I just",
]

LOCATION_HINTS_INDOOR = [
    "at home", "inside", "in the office", "in the room", "indoors", "in the lab",
]

LOCATION_HINTS_OUTDOOR = [
    "outside", "in the park", "on the street", "outdoors", "in open air", "on the trail",
]

LOCATION_HINTS_MIXED = [
    "between indoor and outdoor areas", "across multiple zones", "between building and street",
]


def _clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def typo_noise(text: str) -> str:
    if len(text) < 5:
        return text
    chars = list(text)
    idxs = [i for i, c in enumerate(chars) if c.isalpha()]
    if not idxs:
        return text
    i = RNG.choice(idxs)
    op = RNG.choice(["drop", "swap", "dup"])

    if op == "drop":
        chars.pop(i)
    elif op == "swap" and i + 1 < len(chars):
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    else:
        chars.insert(i, chars[i])

    return _clean_space("".join(chars))


def grammar_noise(text: str) -> str:
    variants = [
        text.replace("I am", "I"),
        text.replace("I am going to", "me going"),
        text.replace("Let's", "let us"),
        text.replace("I need to", "need to"),
    ]
    return _clean_space(RNG.choice(variants))


def make_base_phrase(label: str) -> str:
    if label == "Indoor":
        verb = RNG.choice(INDOOR_VERBS)
        obj = RNG.choice(INDOOR_OBJECTS)
        loc = RNG.choice(LOCATION_HINTS_INDOOR)
    elif label == "Outdoor":
        verb = RNG.choice(OUTDOOR_VERBS)
        obj = RNG.choice(OUTDOOR_OBJECTS)
        loc = RNG.choice(LOCATION_HINTS_OUTDOOR)
    elif label == "Mixed":
        verb = RNG.choice(MIXED_VERBS)
        obj = RNG.choice(MIXED_OBJECTS)
        loc = RNG.choice(LOCATION_HINTS_MIXED)
    else:
        verb = RNG.choice(UNCLEAR_VERBS)
        obj = RNG.choice(UNCLEAR_OBJECTS)
        loc = ""

    prefix = RNG.choice(STYLE_PREFIXES)
    time = RNG.choice(TIME_CONTEXTS)

    phrase = f"{prefix} {verb} {obj} {loc} {time}"
    return _clean_space(phrase)


def expand_variants(base: str) -> List[str]:
    variants = {
        base,
        base.lower(),
        base.capitalize(),
        base + " please",
        base + " with friends",
    }

    if RNG.random() < 0.7:
        variants.add(typo_noise(base))
    if RNG.random() < 0.7:
        variants.add(grammar_noise(base))
    if RNG.random() < 0.4:
        variants.add(grammar_noise(typo_noise(base)))

    return [_clean_space(v) for v in variants if v and len(v) > 2]


def generate_records(per_label: int) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    labels = ["Indoor", "Outdoor", "Mixed", "Unclear"]

    for label in labels:
        collected: List[str] = []
        while len(collected) < per_label:
            base = make_base_phrase(label)
            collected.extend(expand_variants(base))
        for phrase in collected[:per_label]:
            records.append({"phrase": phrase, "label": label})

    RNG.shuffle(records)
    return records


def split_records(records: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    by_label: Dict[str, List[Dict[str, str]]] = {"Indoor": [], "Outdoor": [], "Mixed": [], "Unclear": []}
    for record in records:
        by_label[record["label"]].append(record)

    splits = {"train": [], "val": [], "test": [], "hardset": []}

    for label, items in by_label.items():
        RNG.shuffle(items)
        n = len(items)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        n_test = int(n * 0.10)

        splits["train"].extend(items[:n_train])
        splits["val"].extend(items[n_train:n_train + n_val])
        splits["test"].extend(items[n_train + n_val:n_train + n_val + n_test])
        splits["hardset"].extend(items[n_train + n_val + n_test:])

    for key in splits:
        RNG.shuffle(splits[key])

    return splits


def write_jsonl(path: Path, rows: List[Dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate massive synthetic English activity dataset")
    parser.add_argument("--per-label", type=int, default=60000, help="Number of samples per label")
    parser.add_argument("--output-dir", type=str, default="ml_system/data/datasets", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = generate_records(args.per_label)
    splits = split_records(records)

    for name, rows in splits.items():
        out_file = output_dir / f"{name}.jsonl"
        write_jsonl(out_file, rows)
        print(f"wrote {name}: {len(rows)} rows -> {out_file}")

    summary = {
        "per_label": args.per_label,
        "total": len(records),
        "splits": {k: len(v) for k, v in splits.items()},
    }
    summary_path = output_dir / "massive_dataset_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"summary -> {summary_path}")


if __name__ == "__main__":
    main()
