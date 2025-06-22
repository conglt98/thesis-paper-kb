import json
from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from parse_eval_json import load_eval_items

# Ensure charts directory exists
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "../charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Load data
EVAL_PATH = os.path.join(os.path.dirname(__file__), "../eval/eval.json")
items = load_eval_items(EVAL_PATH)


# Extract scores for each criterion
def extract_scores(items: List) -> pd.DataFrame:
    records = []
    for item in items:
        for system in ["baseline", "proposed"]:
            scores = getattr(item.evaluation.arguments, f"{system}_scores")
            records.append(
                {
                    "index": item.index,
                    "system": system,
                    "clarity_structure": scores.clarity_structure.score,
                    "completeness": scores.completeness.score,
                    "technical_accuracy": scores.technical_accuracy.score,
                    "depth": scores.depth.score,
                    "readability": scores.readability.score,
                    "examples": scores.examples.score,
                    "references": scores.references.score,
                    "summary_takeaway": scores.summary_takeaway.score,
                    "average_score": scores.average_score,
                }
            )
    return pd.DataFrame(records)


df = extract_scores(items)

# Output DataFrame to CSV
csv_path = os.path.join(CHARTS_DIR, "eval_results.csv")
df.to_csv(csv_path, index=False)
print(f"Eval results saved to CSV: {csv_path}")

# List of basic criteria (exclude average_score)
basic_criteria = [
    "clarity_structure",
    "completeness",
    "technical_accuracy",
    "depth",
    "readability",
    "examples",
    "references",
    "summary_takeaway",
]

# Calculate mean for each criterion by system and output to CSV
mean_df = df.groupby("system")[basic_criteria + ["average_score"]].mean().reset_index()
mean_csv_path = os.path.join(CHARTS_DIR, "eval_results_mean.csv")
mean_df.to_csv(mean_csv_path, index=False)
print(f"Mean eval results (per system) saved to CSV: {mean_csv_path}")

# Set style
sns.set(style="whitegrid", font_scale=1.1)

# --- Grouped bar chart for all basic criteria ---
df_melt = df.melt(
    id_vars=["index", "system"],
    value_vars=basic_criteria,
    var_name="criterion",
    value_name="score",
)
plt.figure(figsize=(12, 6))
sns.barplot(
    data=df_melt,
    x="criterion",
    y="score",
    hue="system",
    ci="sd",
    palette="muted",
    capsize=0.1,
)
plt.title("Comparison of Baseline vs Proposed System Across Evaluation Criteria")
plt.ylabel("Score")
plt.xlabel("Evaluation Criterion")
plt.ylim(0, 10)
plt.xticks(rotation=25)
plt.legend(title="System")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "comparison_grouped_criteria.png"))
plt.close()

# --- Average score: barplot with annotation, and boxplot for distribution ---
plt.figure(figsize=(7, 5))
ax = sns.barplot(
    data=df, x="system", y="average_score", ci="sd", palette="muted", capsize=0.1
)
# Annotate mean values on bars
means = df.groupby("system")["average_score"].mean()
for i, system in enumerate(means.index):
    mean_val = means[system]
    ax.text(
        i,
        mean_val + 0.1,
        f"{mean_val:.2f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
plt.title("Overall Average Score Comparison (Mean ± SD)")
plt.ylabel("Average Score")
plt.ylim(0, 10)
plt.xlabel("System")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "average_score_barplot.png"))
plt.close()

# Boxplot for average score distribution
plt.figure(figsize=(5, 5))
sns.boxplot(
    data=df,
    x="system",
    y="average_score",
    palette="muted",
    showmeans=True,
    meanprops={
        "marker": "o",
        "markerfacecolor": "white",
        "markeredgecolor": "black",
        "markersize": "8",
    },
)
sns.swarmplot(data=df, x="system", y="average_score", color="k", alpha=0.5, size=4)
plt.title("Distribution of Average Scores by System")
plt.ylabel("Average Score")
plt.ylim(0, 10)
plt.xlabel("System")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "average_score_boxplot.png"))
plt.close()

print(f"Analysis complete. Charts saved in {CHARTS_DIR} directory.")
