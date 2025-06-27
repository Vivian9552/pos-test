import streamlit as st
import json
import os
import random
import re

QUESTION_FILE = "questions.json"
CONFIG_FILE = "quiz_config.json"

# 將章節字串轉為 tuple（如 6.6 → (6,6)，10.1.7 → (10,1,7)）
def chapter_to_tuple(chapter_str):
    if not chapter_str:
        return (0,)  # 未分類視為最小章節
    return tuple(map(int, re.findall(r'\d+', chapter_str)))

# 載入題庫
def load_questions():
    if not os.path.exists(QUESTION_FILE):
        st.error("❌ 找不到題庫檔案")
        return []
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    for q in questions:
        q.setdefault("question", "")
        q.setdefault("keywords", [])
        q.setdefault("explanation", "")
        q.setdefault("chapter", "")
    return questions

# 載入設定檔
def load_config():
    if not os.path.exists(CONFIG_FILE):
        st.error("❌ 找不到設定檔，請先在管理頁設定")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 根據章節範圍抽題（含空章節）
def get_questions_within_chapter(questions, max_chapter, count):
    max_tuple = chapter_to_tuple(max_chapter) if max_chapter else (9999,)
    pool = [
        q for q in questions
        if chapter_to_tuple(q.get("chapter", "")) <= max_tuple
    ]
    total_available = len(pool)
    selected = random.sample(pool, min(count, total_available))
    return selected, total_available

# 顯示單題（含章節提示）
def display_question(index, q):
    st.markdown(f"**題目 {index + 1}：{q['question']}**")
    chapter_label = q.get("chapter") or "未分類"
    st.caption(f"章節：CH{chapter_label}")
    user_input = st.text_input(f"你的回答 ({index + 1})", value=st.session_state.responses[index], key=f"input_{index}")
    st.session_state.responses[index] = user_input

    if st.button("確認", key=f"btn_{index}"):
        user_ans = user_input.strip()
        correct = all(kw in user_ans for kw in q["keywords"])
        st.session_state.submitted[index] = correct
        if correct:
            st.success("✅ 回答正確")
        else:
            st.error("❌ 回答錯誤")

# 顯示結果
def show_score(questions):
    correct = sum(st.session_state.submitted)
    total = len(questions)
    st.success(f"共答對 {correct}/{total} 題，正確率：{correct/total*100:.1f}%")

# 主程式
def main():
    st.title("新人每日小考")

    config = load_config()
    if not config:
        return

    username = st.text_input("請輸入您的姓名：")
    if not username:
        st.info("請先輸入姓名再開始作答")
        return

    all_questions = load_questions()
    if not all_questions:
        return

    selected_chapter = config.get("chapter")
    num_requested = config.get("num_questions", 7)

    questions, total_available = get_questions_within_chapter(all_questions, selected_chapter, num_requested)

    # 初始化狀態
    if "responses" not in st.session_state or len(st.session_state.responses) != len(questions):
        st.session_state.responses = ["" for _ in questions]
    if "submitted" not in st.session_state or len(st.session_state.submitted) != len(questions):
        st.session_state.submitted = [False for _ in questions]
    if "score_shown" not in st.session_state:
        st.session_state.score_shown = False

    # 顯示章節資訊
    chapter_label = f"CH{selected_chapter}" if selected_chapter else "全部題目"
    st.subheader(f"{username}，今日考題為【{chapter_label}】，共 {len(questions)} 題（原設定 {num_requested} 題，符合條件 {total_available} 題）")

    for idx, q in enumerate(questions):
        display_question(idx, q)

    if st.button("提交答題結果"):
        show_score(questions)
        st.session_state.score_shown = True

if __name__ == "__main__":
    main()
