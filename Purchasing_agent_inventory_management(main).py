import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 密碼與網址設定
ADMIN_PASSWORD = "jennyrose00" 
SHEET_URL = "https://docs.google.com/spreadsheets/d/17nWLvgRzV5IL5Ri0lXh3QW3f-xRnwChd/edit?usp=drive_link&ouid=117663170755599340480&rtpof=true&sd=true"

st.title("🇬🇧 英國代購庫存管理系統 (完全同步版)")

# 2. 權限驗證
st.sidebar.header("🔐 權限驗證")
user_password = st.sidebar.text_input("輸入操作密碼", type="password")

if user_password == ADMIN_PASSWORD:
    st.sidebar.success("✅ 認證成功")
    is_admin = True
    menu = ["查看目前庫存", "直接新增商品"]
else:
    is_admin = False
    menu = ["查看目前庫存"]

choice = st.sidebar.selectbox("選單", menu)

# 3. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

if choice == "查看目前庫存":
    df = conn.read(spreadsheet=SHEET_URL)
    st.dataframe(df, use_container_width=True)

elif choice == "直接新增商品" and is_admin:
    st.write("### ➕ 新增商品至雲端")
    
    # 讀取現有資料以獲取格式
    existing_data = conn.read(spreadsheet=SHEET_URL)
    
    with st.form("add_form"):
        new_name = st.text_input("商品名稱")
        new_gbp = st.number_input("英鎊原價 (£)", min_value=0.0)
        new_stock = st.number_input("入庫數量", min_value=1)
        
        submitted = st.form_submit_button("確認新增並同步至 Google 表格")
        
        if submitted:
            # 計算台幣
            new_twd = new_name * 42
            # 建立新列
            new_entry = pd.DataFrame([{
                "商品名稱": new_name,
                "英鎊原價": new_gbp,
                "台幣售價": new_twd,
                "庫存數量": new_stock
            }])
            # 合併並更新
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success(f"✅ {new_name} 已成功寫入雲端表格！")


