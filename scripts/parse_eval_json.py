from typing import List, Dict, Optional
from pydantic import BaseModel
import json


# --- Score/comment pair for each aspect ---
class ScoreComment(BaseModel):
    score: float
    comment: str


# --- Scores for a response (baseline or proposed) ---
class ResponseScores(BaseModel):
    clarity_structure: ScoreComment
    completeness: ScoreComment
    technical_accuracy: ScoreComment
    depth: ScoreComment
    readability: ScoreComment
    examples: ScoreComment
    references: ScoreComment
    summary_takeaway: ScoreComment
    average_score: float


# --- Verdict and recommendation ---
class VerdictRecommendation(BaseModel):
    better_response: str
    justification: str
    recommendation: Dict[str, str]


# --- Evaluation arguments ---
class EvaluationArguments(BaseModel):
    question: str
    expected_answer: str
    baseline_scores: ResponseScores
    proposed_scores: ResponseScores
    verdict: VerdictRecommendation


# --- Evaluation object ---
class Evaluation(BaseModel):
    name: str
    arguments: EvaluationArguments


# --- Main evaluation item ---
class EvalItem(BaseModel):
    index: int
    question: str
    expected_answer: str
    baseline_response: str
    proposed_response: str
    evaluation: Evaluation


# --- Script to read and parse the file ---
def load_eval_items(path: str) -> List[EvalItem]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [EvalItem(**item) for item in data]


if __name__ == "__main__":
    items = load_eval_items("eval/eval.json")
    print(f"Loaded {len(items)} evaluation items.")
    # Print the first item as an example
    print(json.dumps(items[0].model_dump(), indent=2, ensure_ascii=False))
