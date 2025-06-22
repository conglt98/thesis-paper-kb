import os
import json
import time
from openai import OpenAI

client = OpenAI()

function_schema = {
    "type": "function",
    "name": "evaluate_responses",
    "description": "Evaluate two LLM-generated responses and return scores for clarity, completeness, accuracy, etc., with a verdict and recommendation.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The original question being answered",
            },
            "expected_answer": {
                "type": "string",
                "description": "What kind of answer is expected (e.g., comparison and analysis)",
            },
            "baseline_scores": {
                "type": "object",
                "properties": {
                    "clarity_structure": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "completeness": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "technical_accuracy": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "depth": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "readability": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "examples": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "references": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "summary_takeaway": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "average_score": {"type": "number"},
                },
            },
            "proposed_scores": {
                "type": "object",
                "properties": {
                    "clarity_structure": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "completeness": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "technical_accuracy": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "depth": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "readability": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "examples": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "references": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "summary_takeaway": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "comment": {"type": "string"},
                        },
                    },
                    "average_score": {"type": "number"},
                },
            },
            "verdict": {
                "type": "object",
                "properties": {
                    "better_response": {
                        "type": "string",
                        "enum": ["baseline", "proposed"],
                    },
                    "justification": {"type": "string"},
                    "recommendation": {
                        "type": "object",
                        "properties": {
                            "baseline_best_for": {"type": "string"},
                            "proposed_best_for": {"type": "string"},
                        },
                    },
                },
            },
        },
        "required": [
            "question",
            "expected_answer",
            "baseline_scores",
            "proposed_scores",
            "verdict",
        ],
    },
}

RESULTS_PATH = "eval/results.json"
EVAL_PATH = "eval/eval.json"

os.makedirs(os.path.dirname(EVAL_PATH), exist_ok=True)


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_json_array(path, obj):
    data = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()


def main():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)
    done = load_jsonl(EVAL_PATH)
    done_indices = set(item.get("index") for item in done if "index" in item)

    for idx, item in enumerate(results):
        if idx in done_indices:
            print(f"[SKIP] Item {idx} already evaluated.")
            continue
        question = item.get("question")
        expected = item.get("expect_answer", "")
        response_baseline = item.get("response_baseline")
        response_proposed = item.get("response_proposed_system")
        if not response_baseline or not response_proposed:
            print(f"[SKIP] Item {idx} missing baseline/proposed response.")
            continue
        prompt = f"""
You MUST use the provided function tool to return your evaluation as structured JSON.
You are an expert evaluator. Compare the two responses to the question below and return an evaluation in JSON using the function schema provided.

### Question:
{question}

### Expected Answer Type:
{expected}

### Baseline Response:
{response_baseline}

### Proposed Response:
{response_proposed}
"""
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": prompt}],
                tools=[function_schema],
                tool_choice={"type": "function", "name": "evaluate_responses"},
                temperature=0.3,
            )
            if (
                hasattr(response, "output")
                and response.output
                and len(response.output) > 0
            ):
                tool_call = response.output[0]
                arguments = tool_call.arguments
                try:
                    arguments_dict = json.loads(arguments)
                except Exception as e:
                    print(f"[ERROR] Parse arguments failed for item {idx}: {e}")
                    arguments_dict = arguments
                structured_output = {
                    "name": tool_call.name,
                    "arguments": arguments_dict,
                }
            else:
                print(f"[ERROR] Item {idx}: No function_call in response.")
                print(f"Raw response: {response}")
                continue
            result = {
                "index": idx,
                "question": question,
                "expected_answer": expected,
                "baseline_response": response_baseline,
                "proposed_response": response_proposed,
                "evaluation": structured_output,
            }
            append_json_array(EVAL_PATH, result)
            print(f"[DONE] Item {idx} evaluated and saved.")
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Item {idx}: {e}")
            print("You can rerun the script to resume.")
            break


if __name__ == "__main__":
    main()
