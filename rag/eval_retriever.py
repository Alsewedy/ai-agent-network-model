"""
eval_retriever.py – Evaluate retriever quality for all test questions.

Run: python rag/eval_retriever.py

Tests both v1 and v2 retrievers and reports:
  - must-have chunk recall per question
  - type distribution per question
  - aggregate scores
"""

import sys
import json
import subprocess
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "rag"))


# ─── Test cases ─────────────────────────────────────────────────
# Each test: (label, question, top_k, must_have_chunks, expected_types)

TESTS = [
    {
        "label": "Q1: Dependency Lookup",
        "question": "What does APP01 depend on?",
        "top_k": 10,
        "must_have": {
            # Dependencies chunk for APP01
            "chunk_0030": "dependencies: APP01",
        },
        "expected_top_types": ["dependencies", "port_matrix"],
    },
    {
        "label": "Q2: Required Flows for APP02",
        "question": "What communication must remain open for APP02?",
        "top_k": 10,
        "must_have": {
            "chunk_0081": "pm: APP02 -> IAM01",
            "chunk_0082": "pm: APP02 -> DB01",
            "chunk_0083": "pm: APP02 -> Vault",
            "chunk_0098": "pm: APP02 -> PROXY01",
        },
        "expected_top_types": ["port_matrix", "flows"],
    },
    {
        "label": "Q3: Port/Protocol Lookup",
        "question": "What exact port and protocol does APP01 use to reach the Internal API?",
        "top_k": 10,
        "must_have": {
            "chunk_0080": "pm: APP01 -> Internal API on IAM01",
        },
        "expected_top_types": ["port_matrix"],
    },
    {
        "label": "Q4: Current vs Target",
        "question": "Is broad APP_ZONE access aligned with the target security intent?",
        "top_k": 10,
        "must_have": {
            # Should retrieve APP_ZONE target intent chunk
        },
        "expected_top_types": ["target_intent", "blocked_flows"],
    },
    {
        "label": "Q5: Uncertainty/Unresolved",
        "question": "What parts of the network model are still unresolved or not fully confirmed?",
        "top_k": 10,
        "must_have": {},
        "expected_top_types": ["open_questions"],
    },
    {
        "label": "Q6: Transition Plan (HARD)",
        "question": "Generate the final least-privilege transition plan for APP_ZONE. "
                    "Include all required flows, all flows to be blocked, and all unresolved blockers.",
        "top_k": 15,
        "must_have": {
            "chunk_0077": "pm: APP01 -> IAM01 :8080",
            "chunk_0078": "pm: APP01 -> DB01 :3307",
            "chunk_0079": "pm: APP01 -> Vault :8200",
            "chunk_0080": "pm: APP01 -> IntAPI :9090",
            "chunk_0081": "pm: APP02 -> IAM01 :8080",
            "chunk_0082": "pm: APP02 -> DB01 :3307",
            "chunk_0083": "pm: APP02 -> Vault :8200",
            "chunk_0097": "pm: APP01 -> PROXY01 :3128",
            "chunk_0098": "pm: APP02 -> PROXY01 :3128",
        },
        "expected_top_types": ["port_matrix", "blocked_flows", "target_intent", "open_questions"],
    },
    {
        "label": "Q6b: Transition Plan (top_k=20)",
        "question": "Generate the final least-privilege transition plan for APP_ZONE. "
                    "Include all required flows, all flows to be blocked, and all unresolved blockers.",
        "top_k": 20,
        "must_have": {
            "chunk_0077": "pm: APP01 -> IAM01 :8080",
            "chunk_0078": "pm: APP01 -> DB01 :3307",
            "chunk_0079": "pm: APP01 -> Vault :8200",
            "chunk_0080": "pm: APP01 -> IntAPI :9090",
            "chunk_0081": "pm: APP02 -> IAM01 :8080",
            "chunk_0082": "pm: APP02 -> DB01 :3307",
            "chunk_0083": "pm: APP02 -> Vault :8200",
            "chunk_0097": "pm: APP01 -> PROXY01 :3128",
            "chunk_0098": "pm: APP02 -> PROXY01 :3128",
        },
        "expected_top_types": ["port_matrix", "blocked_flows", "target_intent", "open_questions"],
    },
]


def run_eval(retrieve_fn, version_label: str):
    print(f"\n{'='*70}")
    print(f"  EVALUATING: {version_label}")
    print(f"{'='*70}\n")

    total_must = 0
    total_found = 0

    for test in TESTS:
        results = retrieve_fn(test["question"], top_k=test["top_k"])
        selected_ids = {c["chunk_id"] for _, c in results}
        types = Counter(c["chunk_type"] for _, c in results)

        must = test["must_have"]
        found = sum(1 for cid in must if cid in selected_ids)
        total_must += len(must)
        total_found += found

        recall_pct = (found / len(must) * 100) if must else 100.0
        status = "PASS" if recall_pct == 100 else ("PARTIAL" if found > 0 else "FAIL")

        print(f"  [{status:7s}] {test['label']}")
        print(f"           Recall: {found}/{len(must)} ({recall_pct:.0f}%)")
        print(f"           Types:  {dict(types.most_common())}")

        if must and found < len(must):
            for cid, desc in must.items():
                if cid not in selected_ids:
                    print(f"           MISS: {cid} ({desc})")
        print()

    overall = (total_found / total_must * 100) if total_must > 0 else 100.0
    print(f"  OVERALL: {total_found}/{total_must} must-have chunks ({overall:.1f}%)")
    print(f"{'='*70}\n")
    return overall


def main():
    # ── Run v1 ──
    subprocess.run(
        ["python", str(PROJECT_ROOT / "rag" / "build_chunks.py")],
        capture_output=True, cwd=str(PROJECT_ROOT),
    )
    # Import v1 retriever
    if "retrieve_chunks" in sys.modules:
        del sys.modules["retrieve_chunks"]
    from retrieve_chunks import retrieve_top_chunks as v1_retrieve
    v1_score = run_eval(v1_retrieve, "Retriever v1 (keyword + static quotas)")

    # ── Run v2 ──
    subprocess.run(
        ["python", str(PROJECT_ROOT / "rag" / "build_chunks.py")],
        capture_output=True, cwd=str(PROJECT_ROOT),
    )
    # Reimport v2 retriever (chunks.json has been overwritten)
    if "retrieve_chunks_v2" in sys.modules:
        del sys.modules["retrieve_chunks_v2"]
    from retrieve_chunks_v2 import retrieve_top_chunks as v2_retrieve
    v2_score = run_eval(v2_retrieve, "Retriever v2 (connectivity-aware + dynamic quotas)")

    # ── Summary ──
    print(f"\n{'#'*70}")
    print(f"  SUMMARY")
    print(f"  v1 must-have recall: {v1_score:.1f}%")
    print(f"  v2 must-have recall: {v2_score:.1f}%")
    delta = v2_score - v1_score
    print(f"  Improvement: +{delta:.1f}pp")
    print(f"{'#'*70}")


if __name__ == "__main__":
    main()
