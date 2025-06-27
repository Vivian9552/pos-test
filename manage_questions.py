# manage_questions.py
import streamlit as st
import json
import os

QUESTION_FILE = "questions.json"

# 初始化題庫檔案（若不存在）
def init_questions():
    if not os.path.exists(QUESTION_FILE):
        with open(QUESTION_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# 載入題庫
def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 儲存題庫
def save_questions(questions):
    with open(QUESTION_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

# 題庫欄位驗證工具
def validate_questions(questions):
    for idx, q in enumerate(questions):
        if not isinstance(q, dict):
            st.error(f"❌ 第 {idx+1} 題格式錯誤：不是字典型態")
            return False
        for field in ["question", "explanation", "keywords"]:
            if field not in q:
                st.error(f"❌ 第 {idx+1} 題缺少欄位：{field}")
                return False
        if not isinstance(q["keywords"], list):
            st.error(f"❌ 第 {idx+1} 題關鍵字格式錯誤，應為列表型態")
            return False
    return True

init_questions()
questions = load_questions()

if not validate_questions(questions):
    st.stop()

st.title("題庫管理頁")
st.markdown("這裡可以新增、編輯或刪除測驗題目")

# 顯示現有題目
for i, q in enumerate(questions):
    with st.expander(f"題目 {i+1}"):
        q["question"] = st.text_input(f"題目內容 {i+1}", q.get("question", ""), key=f"q_{i}")
        q["explanation"] = st.text_area(f"說明 {i+1}", q.get("explanation", ""), key=f"e_{i}")
        q["keywords"] = st.text_input(
            f"正確關鍵字（逗號分隔） {i+1}",
            ",".join(q.get("keywords", [])),
            key=f"k_{i}"
        ).split(",")
        if st.button(f"刪除題目 {i+1}", key=f"del_{i}"):
            questions.pop(i)
            save_questions(questions)
            st.experimental_rerun()

# 新增新題目
st.markdown("---")
st.subheader("新增新題目")
new_q = st.text_input("題目內容")
new_e = st.text_area("說明")
new_k = st.text_input("正確關鍵字（逗號分隔）")

if st.button("新增題目"):
    if new_q and new_k:
        questions.append({
            "question": new_q,
            "explanation": new_e,
            "keywords": [k.strip() for k in new_k.split(",") if k.strip()]
        })
        save_questions(questions)
        st.success("✅ 題目新增成功！")
        st.experimental_rerun()
    else:
        st.warning("請填寫題目與關鍵字")
