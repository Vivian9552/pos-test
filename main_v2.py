import streamlit as st
import json

# 判斷是否符合所有關鍵字
def match_keywords(user_input, keywords):
    return all(k in user_input.lower() for k in keywords)

# 載入題庫
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("📝 POS 功能測驗 - 問答模式")
    name = st.text_input("👤 請輸入作答者姓名")

    if not name:
        st.warning("請先輸入姓名後再作答")
        st.stop()

    questions = load_questions()
    user_answers = []
    correctness = []

    st.markdown("---")

    for i, q in enumerate(questions):
        st.subheader(f"第 {i+1} 題")
        st.markdown(q["question"])
        answer = st.text_area("請作答", key=f"input_{i}")

        if st.button("✅ 確認本題", key=f"check_{i}"):
            if match_keywords(answer, q["keywords"]):
                st.success("✅ 回答正確！")
                correctness.append(True)
            else:
                st.error("❌ 回答不正確")
                correctness.append(False)
        else:
            correctness.append(None)

        user_answers.append(answer)
        st.markdown("---")

    if st.button("📨 提交全部結果"):
        total_answered = sum(c is not None for c in correctness)
        total_correct = sum(c is True for c in correctness)

        st.markdown("## 📊 測驗結果")
        st.markdown(f"作答者：**{name}**")
        st.markdown(f"總共回答：{total_answered} 題")
        st.markdown(f"正確題數：{total_correct} 題")

        if total_answered > 0:
            st.markdown(f"正確率：**{round(total_correct / total_answered * 100, 1)}%**")
        else:
            st.markdown("尚未確認任何題目")

if __name__ == "__main__":
    main()