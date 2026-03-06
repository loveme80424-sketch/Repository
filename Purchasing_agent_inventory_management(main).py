import streamlit as st
import pandas as pd

st.title("🇬🇧 英國代購庫存管理系統")

# 使用 session_state 模擬資料庫 (若要永久保存，建議連動 Google Sheets)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["商品名稱", "英鎊原價", "台幣售價", "庫存數量"])

menu = ["新增商品庫存", "售出商品", "查看目前庫存"]
choice = st.sidebar.selectbox("選單", menu)

if choice == "新增商品庫存":
    with st.form("add_form"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊原價 (£)", min_value=0.0)
        stock = st.number_input("入庫數量", min_value=1)
        submit = st.form_submit_button("新增入庫")
        
        if submit:
            twd = gbp * 42  # 匯率設定
            new_row = pd.DataFrame([{"商品名稱": name, "英鎊原價": gbp, "台幣售價": twd, "庫存數量": stock}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success(f"✅ {name} 已入庫")

elif choice == "售出商品":
    names = st.session_state.df["商品名稱"].tolist()
    selected_name = st.selectbox("選擇售出商品", names)
    num = st.number_input("售出數量", min_value=1)
    if st.button("確認售出"):
        idx = st.session_state.df[st.session_state.df["商品名稱"] == selected_name].index[0]
        if st.session_state.df.at[idx, "庫存數量"] >= num:
            st.session_state.df.at[idx, "庫存數量"] -= num
            st.success(f"✅ {selected_name} 剩餘庫存: {st.session_state.df.at[idx, '庫存數量']}")
        else:
            st.error("❌ 庫存不足")

elif choice == "查看目前庫存":
    st.write("### 📦 目前庫存清單")
    st.dataframe(st.session_state.df)
    
    # 提供下載 Excel 功能
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載庫存報表 (CSV)", data=csv, file_name="inventory.csv", mime="text/csv")
