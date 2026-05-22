import streamlit as st


st.set_page_config(page_title="FinScientist", page_icon="📈")

st.title("FinScientist")

ticker = st.text_input("股票代码", placeholder="例如：AAPL、MSFT、TSLA")

if st.button("生成研究摘要"):
    cleaned_ticker = ticker.strip().upper()

    if not cleaned_ticker:
        st.warning("请输入股票代码。")
    else:
        st.subheader("研究摘要")
        st.write(
            f"""
            **{cleaned_ticker} 模拟研究摘要**

            - 公司近期表现整体保持稳定，市场关注度较高。
            - 估值水平需要结合行业平均水平和未来盈利预期进一步判断。
            - 主要风险包括宏观利率变化、行业竞争加剧以及盈利增长不及预期。
            - 本地演示版本仅展示模拟内容，不构成投资建议。
            """
        )
else:
    st.info("输入股票代码后，点击按钮生成本地模拟研究摘要。")
