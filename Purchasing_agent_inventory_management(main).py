import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 基本設定
ADMIN_PASSWORD = "jennyrose00" 
SHEET_URL = "https://docs.google.com/spreadsheets/d/17nWLvgRzV5IL5Ri0lXh3QW3f-xRnwChd/edit?usp=drive_link&ouid=117663170755599340480&rtpof=true&sd=true"

st.set_page_config(page_title="英國代購管理系統", layout="wide")
st.title("🇬🇧 英國代購管理系統 (庫存與銷售同步)")

# 2. 權限驗證
st.sidebar.header("🔐 權限驗證")
pw = st.sidebar.text_input("輸入操作密碼", type="password")
is_admin = (pw == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("✅ 認證成功")
    menu = ["查看目前庫存", "➕ 新增商品入庫", "🤝 登記售出紀錄", "📊 查看銷售報表"]
else:
    menu = ["查看目前庫存"]

choice = st.sidebar.selectbox("功能選單", menu)

# 3. 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 功能實作 ---

if choice == "查看目前庫存":
    # 讀取庫存分頁 (假設名稱為 Sheet1)
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1", ttl=0)
    st.write("### 📦 目前雲端庫存")
    st.dataframe(df, use_container_width=True)

elif choice == "➕ 新增商品入庫" and is_admin:
    st.write("### ➕ 商品入庫登記")
    existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1", ttl=0)
    
    with st.form("add_form"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊原價 (£)", min_value=0.0, step=0.1)
        stock = st.number_input("入庫數量", min_value=1, step=1)
        submitted = st.form_submit_button("確認入庫")
        
        if submitted and name:
            new_row = pd.DataFrame([{"商品名稱": name, "英鎊原價": gbp, "台幣售價": gbp*42, "庫存數量": stock}])
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Sheet1", data=updated_df)
            st.success(f"✅ {name} 已入庫")
            st.cache_data.clear()

elif choice == "🤝 登記售出紀錄" and is_admin:
    st.write("### 🤝 售出商品登記")
    inventory_df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1", ttl=0)
    sales_df = conn.read(spreadsheet=SHEET_URL, worksheet="銷售紀錄", ttl=0)
    
    with st.form("sales_form"):
        item_to_sell = st.selectbox("選擇售出商品", inventory_df["商品名稱"].tolist())
        sell_num = st.number_input("售出數量", min_value=1, step=1)
        sell_date = st.date_input("售出日期", datetime.now())
        confirm = st.form_submit_button("確認售出並更新庫存")
        
        if confirm:
            idx = inventory_df[inventory_df["商品名稱"] == item_to_sell].index[0]
            current_stock = inventory_df.at[idx, "庫存數量"]
            
            if current_stock >= sell_num:
                # A. 更新庫存表
                inventory_df.at[idx, "庫存數量"] = current_stock - sell_num
                conn.update(spreadsheet=SHEET_URL, worksheet="Sheet1", data=inventory_df)
                
                # B. 新增銷售紀錄
                new_sale = pd.DataFrame([{
                    "商品名稱": item_to_sell,
                    "售出數量": sell_num,
                    "售出日期": sell_date.strftime("%Y-%m-%d")
                }])
                updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, worksheet="銷售紀錄", data=updated_sales)
                
                st.success(f"✅ 售出紀錄已存檔！{item_to_sell} 剩餘庫存: {inventory_df.at[idx, '庫存數量']}")
                st.cache_data.clear()
            else:
                st.error(f"❌ 庫存不足！目前僅剩 {current_stock}")

elif choice == "📊 查看銷售報表":
    st.write("### 📈 歷史銷售紀錄")
    sales_data = conn.read(spreadsheet=SHEET_URL, worksheet="銷售紀錄", ttl=0)
    st.dataframe(sales_data, use_container_width=True)
