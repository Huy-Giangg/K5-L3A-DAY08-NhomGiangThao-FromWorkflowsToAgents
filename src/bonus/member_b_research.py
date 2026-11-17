"""Tạo báo cáo R2 bằng benchmark gốc và hai nhánh chỉ khác nguồn delay."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from lab8.app import register_extra_shapes
from lab8.benchmark import render_table, run_benchmark
from lab8.console import utf8_stdio
from lab8.db import load_json, load_jsonl
from lab8.shapes import SHAPES

VARIANT = "swarm_no_ticket_override"
SEEDS = [11, 22, 33, 44, 55]


def build_report() -> dict[str, Any]:
    register_extra_shapes([f"{VARIANT}=bonus.swarm_no_ticket_override:run_claim"])
    try:
        benchmark = run_benchmark(
            world=load_json("data/public_world_state.json"),
            claims=load_jsonl("data/public_claims.jsonl"),
            shapes=["swarm", VARIANT],
            seeds=SEEDS,
        )
    finally:
        SHAPES.pop(VARIANT, None)
    paired = {
        (row["claim_id"], row["seed"]): row
        for row in benchmark["trials"] if row["shape"] == VARIANT
    }
    failures = []
    for row in benchmark["trials"]:
        if row["shape"] == "swarm" and not row["passed"]:
            comparison = paired[(row["claim_id"], row["seed"])]
            failures.append({
                "claim_id": row["claim_id"], "seed": row["seed"],
                "baseline_run_id": row["run_id"], "reason": row["reason"],
                "variant_run_id": comparison["run_id"], "variant_passed": comparison["passed"],
                "mast_category": "task_verification",
                "classification_basis": (
                    "Swarm thay delay_days có cấu trúc bằng số từ ticket khi seed % 5 == 0; "
                    "thiếu đối chiếu căn cứ trước khi đề xuất tiền. Đây là diễn giải của nhóm."
                ),
            })
    code = Path("lab8/shapes/swarm_reference.py").read_bytes()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False,
    )
    return {
        "question": "R2", "source": "https://arxiv.org/abs/2503.13657v3",
        "intervention": "Tắt việc parse delay từ ticket; không tắt sanitization/approval.",
        "fixed": ["MockLLM", "tools", "seeds", "corpus", "pricing", "evaluator", "host"],
        "provenance": {
            "git_head_at_run": head.stdout.strip() if head.returncode == 0 else None,
            "reference_sha256": hashlib.sha256(code).hexdigest(),
            "trace_identity": "Mỗi nhánh có run_id riêng; chỉ đổi nhãn, không đổi seed/prompt.",
        },
        "failure_analysis": failures,
        "benchmark": benchmark,
        "limitations": [
            "MockLLM và 14 claim public, không suy rộng thành tỷ lệ lỗi của model thật.",
            "MAST là khung diễn giải; không phải kết quả gán nhãn được tác giả paper xác nhận.",
            "latency unavailable; chi phí mô phỏng, không phải hóa đơn API.",
        ],
    }


def main() -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="reports/research_r2_ablation.json")
    args = parser.parse_args()
    report = build_report()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(render_table(report["benchmark"]))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
