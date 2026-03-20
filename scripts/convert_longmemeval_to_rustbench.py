#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert official LongMemEval JSON into Memoria's rustbench ScenarioDataset format."
    )
    parser.add_argument("input", type=Path, help="Path to official longmemeval_oracle.json")
    parser.add_argument("output", type=Path, help="Path to write rustbench dataset JSON")
    return parser.parse_args()


def to_rfc3339(raw: str) -> str:
    dt = datetime.strptime(raw, "%Y/%m/%d (%a) %H:%M")
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def render_session(raw_date: str, session_id: str, session: list[dict]) -> str:
    lines = [f"Session date: {raw_date}", f"Session id: {session_id}"]
    for turn in session:
        role = turn.get("role", "unknown").strip()
        content = turn.get("content", "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def answer_snippets(item: dict) -> list[str]:
    snippets: list[str] = []
    seen: set[str] = set()
    answer_session_ids = set(item["answer_session_ids"])
    for session_id, session in zip(item["haystack_session_ids"], item["haystack_sessions"]):
        if session_id not in answer_session_ids:
            continue
        for turn in session:
            content = turn.get("content", "").strip()
            if turn.get("has_answer") and content and content not in seen:
                seen.add(content)
                snippets.append(content)
    return snippets


def every_answer_session_has_marked_turn(item: dict) -> bool:
    answer_session_ids = set(item["answer_session_ids"])
    for session_id, session in zip(item["haystack_session_ids"], item["haystack_sessions"]):
        if session_id not in answer_session_ids:
            continue
        if not any(turn.get("has_answer") for turn in session):
            return False
    return True


def difficulty_for(item: dict) -> str:
    sessions = len(item["haystack_sessions"])
    if sessions <= 2:
        return "L1"
    if sessions <= 4:
        return "L2"
    return "L3"


def build_scenario(item: dict) -> dict | None:
    question_id = str(item["question_id"])
    if question_id.endswith("_abs"):
        return None

    if not every_answer_session_has_marked_turn(item):
        return None

    expected_contents = answer_snippets(item)
    if not expected_contents:
        return None

    seed_memories = []
    for session_id, raw_date, session in zip(
        item["haystack_session_ids"],
        item["haystack_dates"],
        item["haystack_sessions"],
    ):
        seed_memories.append(
            {
                "content": render_session(raw_date, session_id, session),
                "memory_type": "semantic",
                "session_id": session_id,
                "observed_at": to_rfc3339(raw_date),
            }
        )

    top_k = max(1, len(item["answer_session_ids"]))
    question_type = item["question_type"]

    return {
        "scenario_id": question_id,
        "title": question_type,
        "description": item["question"],
        "domain": "longmem",
        "difficulty": difficulty_for(item),
        "horizon": "oracle",
        "tags": ["oracle", question_type],
        "source_family": "longmemeval",
        "question_type": question_type,
        "metadata": {
            "question_date": item["question_date"],
            "question_date_rfc3339": to_rfc3339(item["question_date"]),
            "answer_session_ids": item["answer_session_ids"],
            "haystack_session_ids": item["haystack_session_ids"],
            "seed_memory_count": len(seed_memories),
        },
        "seed_memories": seed_memories,
        "maturation": [],
        "steps": [],
        "assertions": [
            {
                "query": item["question"],
                "top_k": top_k,
                "include_cross_session": True,
                "expected_contents": expected_contents,
                "excluded_contents": [],
            }
        ],
    }


def main() -> None:
    args = parse_args()
    raw = json.loads(args.input.read_text())

    scenarios = []
    skipped_abstention = 0
    skipped_unscorable = 0
    for item in raw:
        scenario = build_scenario(item)
        if scenario is None:
            if str(item["question_id"]).endswith("_abs"):
                skipped_abstention += 1
            else:
                skipped_unscorable += 1
            continue
        scenarios.append(scenario)

    dataset = {
        "dataset_id": "longmemeval-oracle-rustbench",
        "version": "2025-09-cleaned",
        "scenarios": scenarios,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, indent=2) + "\n")

    print(
        json.dumps(
            {
                "input_records": len(raw),
                "output_scenarios": len(scenarios),
                "skipped_abstention": skipped_abstention,
                "skipped_unscorable": skipped_unscorable,
                "output_path": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
