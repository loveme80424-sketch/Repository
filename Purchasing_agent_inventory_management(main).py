import streamlit as st
import pandas as pd
import os

st.title("🇬🇧 英國代購庫存管理系統")

# --- 這裡修改成你現有的檔名 ---
# 如果檔案跟程式碼放在同一個資料夾，直接寫檔名即可
# 如果在不同地方，請寫完整路徑，例如 "C:/Users/Desktop/英國代購庫存表.xlsx"
excel_file = "英國代購庫存表.xlsx" 

# 讀取現有表單的函式
def load_data():
    try:
        # 讀取你電腦上現有的 Excel 檔
        return pd.read_excel(excel_file)
    except FileNotFoundError:
        st.error(f"找不到檔案：{excel_file}，請確認檔名是否正確或路徑是否完整。")
        return pd.DataFrame(columns=["商品名稱", "英鎊原價", "台幣售價", "庫存數量"])

# 儲存到現有表單的函式
def save_data(df):
    df.to_excel(excel_file, index=False)

# 初始化：讀取你現有的資料
if 'df' not in st.session_state:
    st.session_state.df = load_data()

menu = ["查看目前庫存", "新增商品庫存", "售出商品"]
choice = st.sidebar.selectbox("功能選單", menu)

if choice == "查看目前庫存":
    st.write(f"### 📦 讀取自：{excel_file}")
    # 重新讀取按鈕，確保跟 Excel 同步
    if st.button("整理並同步 Excel 資料"):
        st.session_state.df = load_data()
        st.rerun()
    st.dataframe(st.session_state.df)

elif choice == "新增商品庫存":
    with st.form("add_form"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊原價 (£)", min_value=0.0)
        stock = st.number_input("入庫數量", min_value=1)
        submit = st.form_submit_button("寫入現有表單")

        if submit:
            twd = gbp * 42  # 匯率可自行調整
            new_row = pd.DataFrame([{"商品名稱": name, "英鎊原價": gbp, "台幣售價": twd, "庫存數量": stock}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"✅ 已成功更新至 {excel_file}")

elif choice == "售出商品":
    if not st.session_state.df.empty:
        names = st.session_state.df["商品名稱"].tolist()
        selected_name = st.selectbox("選擇售出商品", names)
        num = st.number_input("售出數量", min_value=1)
        if st.button("確認售出並更新表單"):
            idx = st.session_state.df[st.session_state.df["商品名稱"] == selected_name].index[0]
            if st.session_state.df.at[idx, "庫存數量"] >= num:
                st.session_state.df.at[idx, "庫存數量"] -= num
                save_data(st.session_state.df)
                st.success(f"✅ 庫存已扣除，檔案已更新")
            else:
                st.error("❌ 庫存不足")
