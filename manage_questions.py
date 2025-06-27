# manage_questions.py
import streamlit as st
import json
import os
import re
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    st.error("❗ 本功能需要安裝 pandas 套件，請在終端機執行：pip install pandas openpyxl")
    st.stop()

QUESTION_FILE = "questions.json"
CONFIG_FILE = "quiz_config.json"
BACKUP_FILE = "questions_backup.json"

def chapter_to_tuple(chapter_str):
    return tuple(map(int, re.findall(r'\d+', chapter_str)))

def init_questions():
    if not os.path.exists(QUESTION_FILE):
        with open(QUESTION_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
    for q in questions:
        q.setdefault("question", "")
        q.setdefault("keywords", [])
        q.setdefault("explanation", "")
        q.setdefault("chapter", "")
    return questions

def backup_questions(data):
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"questions_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_external_change(current_data):
    if not os.path.exists(BACKUP_FILE):
        return False
    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
        backup_data = json.load(f)
    return current_data != backup_data

def save_questions(questions):
    with open(QUESTION_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    backup_questions(questions)
    st.toast("✅ 題庫儲存與備份成功", icon="💾")

def show_question_manager():
    st.title("📚 題庫管理頁")

    init_questions()
    questions = load_questions()

    if check_external_change(questions):
        st.warning("⚠️ 偵測到題庫檔案與上次備份不同，可能被外部修改過")

    st.subheader("題目列表")

    for idx, q in enumerate(questions):
        expander_label = q["question"] if q["question"] else f"題目 {idx + 1}"
        with st.expander(expander_label):
            q["chapter"] = st.text_input("章節", value=q["chapter"], key=f"c_{idx}")
            q["question"] = st.text_input("題目內容", value=q["question"], key=f"q_{idx}")
            q["keywords"] = st.text_input("關鍵字（用逗號分隔）", value=",".join(q["keywords"]), key=f"k_{idx}").split(",")
            q["explanation"] = st.text_area("說明", value=q["explanation"], key=f"e_{idx}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 儲存", key=f"save_{idx}"):
                    save_questions(questions)
            with col2:
                if st.button("❌ 刪除", key=f"del_{idx}"):
                    questions.pop(idx)
                    save_questions(questions)
                    st.success("✅ 已刪除該題")
                    st.rerun()

    if st.button("💾 一鍵儲存"):
        save_questions(questions)
        st.success("✅ 所有修改已儲存")

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
            st.rerun()
        else:
            st.warning("❗ 題目與關鍵字為必填欄位")

    st.markdown("---")
    st.header("📥 匯入 Excel 題庫")

    uploaded_file = st.file_uploader("選擇 Excel 檔案（需包含：章節、題目、關鍵字、說明 四欄）", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            required_columns = {"章節", "題目", "關鍵字", "說明"}

            if not required_columns.issubset(set(df.columns)):
                st.error("❗ 欄位錯誤，請確認 Excel 包含：章節、題目、關鍵字、說明")
            else:
                imported = 0
                for _, row in df.iterrows():
                    q = {
                        "chapter": str(row["章節"]).strip(),
                        "question": str(row["題目"]).strip(),
                        "keywords": [k.strip() for k in str(row["關鍵字"]).split(",")],
                        "explanation": str(row["說明"]).strip()
                    }
                    questions.append(q)
                    imported += 1

                save_questions(questions)
                st.success(f"✅ 成功匯入 {imported} 題題目！")
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ 匯入失敗：{e}")

    st.markdown("---")
    st.header("🧪 每日考題設定")

    input_chapter = st.text_input("章節 CH【】 輸入上限（如 6.6）", key="chapter_limit")
    if input_chapter:
        try:
            limit_tuple = chapter_to_tuple(input_chapter)

            def chapter_valid(chapter_str):
                try:
                    return chapter_to_tuple(chapter_str) <= limit_tuple
                except:
                    return False

            available_questions = [q for q in questions if chapter_valid(q.get("chapter", ""))]
        except Exception:
            st.error("❗ 請輸入正確格式，例如 6.6 或 10.1.7")
            available_questions = []
    else:
        available_questions = []

    max_questions = len(available_questions)

    if max_questions == 0:
        st.warning("⚠️ 符合條件的題目為 0，請先建立相關題目")
    else:
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
                "chapter": input_chapter,
                "num_questions": num_questions
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            st.success(f"✅ 已儲存：CH{input_chapter}，共 {num_questions} 題")

    if os.path.exists(CONFIG_FILE):
        if st.button("🗑️ 清除設定"):
            os.remove(CONFIG_FILE)
            st.success("✅ 設定已清除，將回到預設 7 題")
            st.rerun()

if __name__ == "__main__":
    show_question_manager()
