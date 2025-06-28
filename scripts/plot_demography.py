import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# Đảm bảo thư mục charts/ tồn tại
os.makedirs("charts", exist_ok=True)

# Dữ liệu domain of papers
domain_data = {
    "Domain": ["Math", "Physics", "Computer Science"],
    "Number of Papers": [110, 140, 750],
}
df_domain = pd.DataFrame(domain_data)

# Dữ liệu question type
question_data = {
    "Question Type": ["Definition", "Comparision", "Explanation", "Synthesis"],
    "Number of Questions": [15, 12, 21, 12],
}
df_question = pd.DataFrame(question_data)

# Biểu đồ 1: Domain of papers
plt.figure(figsize=(6, 4))
sns.barplot(data=df_domain, x="Domain", y="Number of Papers", palette="Set2")
plt.title("Number of Papers by Domain")
plt.xlabel("Domain")
plt.ylabel("Number of Papers")
plt.tight_layout()
plt.savefig("charts/papers_by_domain_seaborn.png")
plt.close()

# Biểu đồ 2: Question type
plt.figure(figsize=(6, 4))
sns.barplot(
    data=df_question, x="Question Type", y="Number of Questions", palette="Set3"
)
plt.title("Number of Questions by Type")
plt.xlabel("Question Type")
plt.ylabel("Number of Questions")
plt.tight_layout()
plt.savefig("charts/questions_by_type_seaborn.png")
plt.close()

# Biểu đồ tròn 1: Domain of papers (pie chart)
plt.figure(figsize=(6, 6))
colors = sns.color_palette("Set2", len(df_domain))


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f"{pct:.1f}%\n({val})"

    return my_autopct


plt.pie(
    df_domain["Number of Papers"],
    labels=df_domain["Domain"],
    autopct=make_autopct(df_domain["Number of Papers"]),
    startangle=140,
    colors=colors,
    textprops={"fontsize": 12},
)
plt.title("Distribution of Papers by Domain")
plt.legend(
    df_domain["Domain"], title="Domain", loc="best", fontsize=10, title_fontsize=11
)
plt.tight_layout()
plt.savefig("charts/papers_by_domain_pie.png")
plt.close()

# Biểu đồ tròn 2: Question type (pie chart)
plt.figure(figsize=(6, 6))
colors = sns.color_palette("Set3", len(df_question))
plt.pie(
    df_question["Number of Questions"],
    labels=df_question["Question Type"],
    autopct=make_autopct(df_question["Number of Questions"]),
    startangle=140,
    colors=colors,
    textprops={"fontsize": 12},
)
plt.title("Distribution of Questions by Type")
plt.legend(
    df_question["Question Type"],
    title="Question Type",
    loc="best",
    fontsize=10,
    title_fontsize=11,
)
plt.tight_layout()
plt.savefig("charts/questions_by_type_pie.png")
plt.close()

print("Đã lưu hai biểu đồ cột và hai biểu đồ tròn vào thư mục charts/.")
