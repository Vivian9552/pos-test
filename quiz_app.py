# quiz_app.py
import streamlit as st
import json
import os
import random

QUESTION_FILE = "questions.json"
CONFIG_FILE = "quiz_config.json"

# 載入題庫
def load_questions():
    if not os.path.exists(QUESTION_FILE):
        st.error("❌ 找不到題庫檔案")
        return []
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 載入設定
def load_config():
    if not os.path.exists(CONFIG_FILE):
        st.error("❌ 尚未設定今日章節與題數，請至管理頁設定")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 根據章節抽題
def get_questions_by_chapter(all_questions, chapter, count):
    pool = [q for q in all_questions if q.get("chapter") == chapter]
    return random.sample(pool, min(len(pool), count))

# 顯示單題
def display_question(index, q):
    st.markdown(f"**題目 {index + 1}：{q['question']}**")
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
    selected_chapter = config["chapter"]
    num_questions = config["num_questions"]
    questions = get_questions_by_chapter(all_questions, selected_chapter, num_questions)

    # 初始化狀態
    if "responses" not in st.session_state:
        st.session_state.responses = ["" for _ in questions]
    if "submitted" not in st.session_state:
        st.session_state.submitted = [False for _ in questions]
    if "score_shown" not in st.session_state:
        st.session_state.score_shown = False

    st.subheader(f"{username}，今日考題為【{selected_chapter}】章，請開始作答：")

    for idx, q in enumerate(questions):
        display_question(idx, q)

    if st.button("提交答題結果"):
        show_score(questions)
        st.session_state.score_shown = True

if __name__ == "__main__":
    main()
