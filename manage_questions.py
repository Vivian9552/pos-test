import re

# 將章節字串轉為可比較的 tuple（如 6.6 → (6,6)，10.1.7 → (10,1,7)）
def chapter_to_tuple(chapter_str):
    return tuple(map(int, re.findall(r'\d+', chapter_str)))

# 題庫設定區
st.markdown("---")
st.header("🧪 每日考題設定")

# 過濾有效章節（數字形式）並排序
chapter_list = sorted(
    {q["chapter"] for q in questions if re.match(r"^\d+(\.\d+)*$", q.get("chapter", ""))},
    key=chapter_to_tuple
)

selected_chapter = st.selectbox("📘 今日出題章節上限", chapter_list, format_func=lambda x: f"CH{x}")

if selected_chapter:
    selected_tuple = chapter_to_tuple(selected_chapter)
    # 篩選所有小於等於該章節的題目
    available_questions = [
        q for q in questions
        if q.get("chapter") and chapter_to_tuple(q["chapter"]) <= selected_tuple
    ]
else:
    available_questions = questions

max_questions = len(available_questions)

if max_questions == 0:
    st.warning("⚠️ 符合條件的題目為 0，請先建立相關題目")
else:
    # 嘗試讀取之前的設定，否則預設為 7 題
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        prev_num = config_data.get("num_questions", 7)
    else:
        prev_num = 7

    num_questions = st.number_input(
        "✏️ 每日出題數量",
        min_value=1,
        max_value=max_questions,
        value=min(prev_num, max_questions)
    )

    if st.button("📌 儲存今日設定"):
        config = {
            "chapter": selected_chapter,
            "num_questions": num_questions
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        st.success(f"✅ 已儲存：CH{selected_chapter}，共 {num_questions} 題")
