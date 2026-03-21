#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert official LongMemEval JSON into Memoria's rustbench ScenarioDataset format."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to an official LongMemEval JSON file (oracle / S / M variants).",
    )
    parser.add_argument("output", type=Path, help="Path to write rustbench dataset JSON")
    parser.add_argument(
        "--variant",
        choices=("oracle", "s", "m"),
        required=True,
        help="Official LongMemEval split to convert. Required so dataset identity does not depend on a local filename.",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        help="Optional path to write a lossless conversion manifest. "
        "Defaults to <output>.manifest.json.",
    )
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


def iter_json_array(path: Path) -> Iterator[dict]:
    """Stream large top-level JSON arrays via jq when available."""
    jq = shutil.which("jq")
    if jq:
        proc = subprocess.Popen(
            [jq, "-c", ".[]", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip()
            if line:
                yield json.loads(line)
        _, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"jq failed for {path}: {stderr.strip()}")
        return

    # Fallback for environments without jq. This is more memory-intensive.
    raw = json.loads(path.read_text())
    for item in raw:
        yield item


def variant_metadata(variant: str) -> tuple[str, str, str]:
    if variant == "oracle":
        return ("oracle", "oracle", "longmemeval-oracle-rustbench")
    if variant == "s":
        return ("s", "longmemeval-s", "longmemeval-s-rustbench")
    if variant == "m":
        return ("m", "longmemeval-m", "longmemeval-m-rustbench")
    raise ValueError(f"Unsupported variant: {variant}")


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


def unmarked_answer_session_ids(item: dict) -> list[str]:
    answer_session_ids = set(item["answer_session_ids"])
    missing = []
    for session_id, session in zip(item["haystack_session_ids"], item["haystack_sessions"]):
        if session_id not in answer_session_ids:
            continue
        if not any(turn.get("has_answer") for turn in session):
            missing.append(session_id)
    return missing


def difficulty_for(item: dict) -> str:
    sessions = len(item["haystack_sessions"])
    if sessions <= 2:
        return "L1"
    if sessions <= 4:
        return "L2"
    return "L3"


def build_scenario(item: dict, variant: str, horizon: str, source_file: str) -> tuple[dict | None, str | None]:
    question_id = str(item["question_id"])
    if question_id.endswith("_abs"):
        return None, "abstention_question"

    expected_contents = answer_snippets(item)
    if not expected_contents:
        return None, "no_marked_answer_turn"

    missing_answer_markers = unmarked_answer_session_ids(item)

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
        "horizon": horizon,
        "tags": [variant, question_type],
        "source_family": "longmemeval",
        "question_type": question_type,
        "metadata": {
            "longmemeval_variant": variant,
            "source_file": source_file,
            "question_date": item["question_date"],
            "question_date_rfc3339": to_rfc3339(item["question_date"]),
            "gold_answer": item["answer"],
            "answer_session_ids": item["answer_session_ids"],
            "unmarked_answer_session_ids": missing_answer_markers,
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
    }, None


def manifest_record(
    item: dict,
    *,
    variant: str,
    horizon: str,
    source_file: str,
    record_index: int,
    status: str,
    reason: str | None,
    scenario_id: str | None,
) -> dict:
    return {
        "record_index": record_index,
        "question_id": str(item["question_id"]),
        "question_type": item["question_type"],
        "variant": variant,
        "horizon": horizon,
        "source_file": source_file,
        "status": status,
        "reason": reason,
        "scenario_id": scenario_id,
        "is_abstention": str(item["question_id"]).endswith("_abs"),
        "haystack_session_count": len(item["haystack_sessions"]),
        "answer_session_count": len(item["answer_session_ids"]),
        "unmarked_answer_session_ids": unmarked_answer_session_ids(item),
        "question_date": item["question_date"],
    }


def main() -> None:
    args = parse_args()
    manifest_out = args.manifest_out or args.output.with_suffix(args.output.suffix + ".manifest.json")
    variant, horizon, dataset_id = variant_metadata(args.variant)

    scenarios = []
    manifest = []
    dropped_reasons: Counter[str] = Counter()
    seen_runtime_ids: Counter[str] = Counter()
    input_records = 0
    for idx, item in enumerate(iter_json_array(args.input)):
        input_records += 1
        scenario, reason = build_scenario(item, variant, horizon, args.input.name)
        if scenario is None:
            dropped_reasons[reason or "unknown"] += 1
            manifest.append(
                manifest_record(
                    item,
                    variant=variant,
                    horizon=horizon,
                    source_file=args.input.name,
                    record_index=idx,
                    status="unsupported",
                    reason=reason,
                    scenario_id=None,
                )
            )
            continue

        raw_question_id = scenario["scenario_id"]
        duplicate_index = seen_runtime_ids[raw_question_id]
        seen_runtime_ids[raw_question_id] += 1
        if duplicate_index > 0:
            scenario["scenario_id"] = f"{raw_question_id}__dup{duplicate_index + 1}"
        scenario["metadata"]["raw_question_id"] = raw_question_id
        scenario["metadata"]["scenario_duplicate_index"] = duplicate_index

        scenarios.append(scenario)
        manifest.append(
            manifest_record(
                item,
                variant=variant,
                horizon=horizon,
                source_file=args.input.name,
                record_index=idx,
                status="runnable",
                reason=None,
                scenario_id=scenario["scenario_id"],
            )
        )

    dataset = {
        "dataset_id": dataset_id,
        "version": "2025-09-cleaned",
        "scenarios": scenarios,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, indent=2) + "\n")
    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(
        json.dumps(
            {
                "source_file": args.input.name,
                "variant": variant,
                "dataset_id": dataset_id,
                "version": "2025-09-cleaned",
                "input_records": input_records,
                "runnable_scenarios": len(scenarios),
                "unsupported_counts": dict(dropped_reasons),
                "records": manifest,
            },
            indent=2,
        )
        + "\n"
    )

    print(
        json.dumps(
            {
                "input_records": input_records,
                "output_scenarios": len(scenarios),
                "unsupported_counts": dict(dropped_reasons),
                "output_path": str(args.output),
                "manifest_path": str(manifest_out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
