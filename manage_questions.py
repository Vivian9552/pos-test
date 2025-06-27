import streamlit as st
import json
import os
import re

QUESTION_FILE = "questions.json"
CONFIG_FILE = "quiz_config.json"

# 將章節字串轉為可比較的 tuple（如 6.6 → (6,6)，10.1.7 → (10,1,7)）
def chapter_to_tuple(chapter_str):
    return tuple(map(int, re.findall(r'\d+', chapter_str)))

# 初始化題庫檔案
def init_questions():
    if not os.path.exists(QUESTION_FILE):
        with open(QUESTION_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# 載入題庫
def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    for q in questions:
        q.setdefault("question", "")
        q.setdefault("keywords", [])
        q.setdefault("explanation", "")
        q.setdefault("chapter", "")
    return questions

# 儲存題庫
def save_questions(questions):
    with open(QUESTION_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

# 顯示單題編輯區塊
def edit_question(idx, q):
    st.markdown(f"### ✏️ 編輯題目 {idx + 1}")
    q["question"] = st.text_input(f"題目內容 {idx + 1}", value=q["question"], key=f"q_{idx}")
    q["keywords"] = st.text_input(f"關鍵字（用逗號分隔）", value=",".join(q["keywords"]), key=f"k_{idx}").split(",")
    q["explanation"] = st.text_area(f"說明", value=q["explanation"], key=f"e_{idx}")
    q["chapter"] = st.text_input("章節", value=q["chapter"], key=f"c_{idx}")
    return q

# 顯示題庫管理頁
def show_question_manager():
    st.title("📚 題庫管理頁")

    init_questions()
    questions = load_questions()

    # 題目列表
    st.subheader("題目列表")
    for idx, q in enumerate(questions):
        with st.expander(f"題目 {idx + 1}"):
            updated_q = edit_question(idx, q)
            questions[idx] = updated_q
            if st.button("❌ 刪除", key=f"del_{idx}"):
                questions.pop(idx)
                save_questions(questions)
                st.experimental_rerun()

    # 新增題目
    st.markdown("---")
    st.header("➕ 新增新題目")
    new_q = st.text_input("題目內容", key="new_q")
    new_k = st.text_input("關鍵字（用逗號分隔）", key="new_k")
    new_e = st.text_area("說明", key="new_e")
    new_c = st.text_input("章節（如 6.6、10.1.7）", key="new_c")

    if st.button("新增題目"):
        if new_q and new_k:
            questions.append({
                "question": new_q,
                "keywords": [k.strip() for k in new_k.split(",")],
                "explanation": new_e,
                "chapter": new_c
            })
            save_questions(questions)
            st.success("✅ 新題目已加入")
            st.experimental_rerun()
        else:
            st.warning("❗ 題目與關鍵字為必填欄位")

    if st.button("💾 儲存所有修改"):
        save_questions(questions)
        st.success("✅ 題庫已更新")

    # 題庫設定區
    st.markdown("---")
    st.header("🧪 每日考題設定")

    # 整理章節（僅保留有效格式）
    chapter_list = sorted(
        {q["chapter"] for q in questions if re.match(r"^\d+(\.\d+)*$", q.get("chapter", ""))},
        key=chapter_to_tuple
    )

    selected_chapter = st.selectbox("📘 今日出題章節上限", chapter_list, format_func=lambda x: f"CH{x}")

    if selected_chapter:
        selected_tuple = chapter_to_tuple(selected_chapter)
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
        # 預設值 7 題（讀設定檔 fallback）
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

# 執行入口
if __name__ == "__main__":
    show_question_manager()
