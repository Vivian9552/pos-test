
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
    questions = load_questions()
    score = 0
    total = len(questions)

    st.markdown("---")
    for i, q in enumerate(questions):
        st.subheader(f"第 {i+1} 題")
        user_input = st.text_area(q["question"], key=f"q{i}")

        if user_input:
            is_correct = False

            # 判斷方式：完整詞組 or 關鍵字
            if "must_include" in q:
                is_correct = match_required_phrases(user_input, q["must_include"])
            elif "keywords" in q:
                is_correct = match_keywords(user_input, q["keywords"])

            if is_correct:
                st.success("✅ 回答正確")
                score += 1
            else:
                st.error("❌ 回答不正確")
                st.info(f"正確解說：{q['explanation']}")

        st.markdown("---")

    if st.button("提交測驗"):
        st.success(f"🎯 你共答對 {score} / {total} 題，正確率：{round(score/total*100, 1)}%")

if __name__ == "__main__":
    main()
