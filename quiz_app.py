# quiz_app.py
import streamlit as st
import json
import random

# 題庫檔案路徑
QUESTION_FILE = "questions.json"

# 載入題庫
def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

st.title("新人測驗系統")

# 讓使用者輸入姓名
username = st.text_input("請輸入您的姓名：")

if username:
    questions = load_questions()
    if "responses" not in st.session_state:
        st.session_state.responses = ["" for _ in questions]
    if "submitted" not in st.session_state:
        st.session_state.submitted = [False for _ in questions]
    if "score_shown" not in st.session_state:
        st.session_state.score_shown = False

    st.subheader(f"Hi {username}，請開始作答：")

    for idx, q in enumerate(questions):
        st.markdown(f"**題目 {idx+1}：{q['question']}**")
        st.session_state.responses[idx] = st.text_input(f"你的回答 ({idx+1})", value=st.session_state.responses[idx], key=f"input_{idx}")

        if st.button(f"確認第 {idx+1} 題", key=f"btn_{idx}"):
            user_ans = st.session_state.responses[idx].strip()
            correct = all(kw in user_ans for kw in q["keywords"])
            st.session_state.submitted[idx] = correct
            if correct:
                st.success("✅ 回答正確")
            else:
                st.error("❌ 回答錯誤")

    if st.button("提交所有題目並計算正確率"):
        total = len(questions)
        correct_count = sum(st.session_state.submitted)
        accuracy = correct_count / total * 100
        st.session_state.score_shown = True
        st.success(f"共答對 {correct_count}/{total} 題，正確率：{accuracy:.1f}%")

elif username == "":
    st.info("請先輸入姓名後再作答。")
