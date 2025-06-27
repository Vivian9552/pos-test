
import streamlit as st
import json

# 判斷是否符合所有關鍵字
def match_keywords(user_input, keywords):
    return all(k in user_input.lower() for k in keywords)

# 判斷是否符合完整詞組
def match_required_phrases(user_input, phrases):
    return all(p in user_input for p in phrases)

# 載入題庫
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("📝 POS 功能測驗 - 問答模式")

    name = st.text_input("👤 請輸入作答者姓名")

    questions = load_questions()
    user_answers = []
    evaluate = False

    st.markdown("---")
    for i, q in enumerate(questions):
        st.subheader(f"第 {i+1} 題")
        answer = st.text_area(q["question"], key=f"q{i}")
        user_answers.append(answer)

    if st.button("✅ 確認提交"):
        st.markdown("---")
        score = 0
        total = len(questions)
        st.subheader(f"👤 {name or '未填寫姓名'} 的測驗結果")
        for i, (q, user_input) in enumerate(zip(questions, user_answers)):
            st.markdown(f"**第 {i+1} 題：{q['question']}**")
            is_correct = False
            if "must_include" in q:
                is_correct = all(p in user_input for p in q["must_include"])
            elif "keywords" in q:
                is_correct = all(k in user_input.lower() for k in q["keywords"])
            if is_correct:
                st.success("✅ 回答正確")
                score += 1
            else:
                st.error("❌ 回答不正確")
                st.info(f"正確解說：{q['explanation']}")
            st.markdown("---")

        st.success(f"🎯 {name or '使用者'} 共答對 {score} / {total} 題，正確率：{round(score/total*100, 1)}%")

if __name__ == "__main__":
    main()
