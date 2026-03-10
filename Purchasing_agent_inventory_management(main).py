import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. 初始化設定 ---
ADMIN_PASSWORD = "jennyrose00" 

st.set_page_config(page_title="英國代購管理系統", layout="wide")
st.title("🇬🇧 英國代購庫存與銷售管理系統")

# 讀取隱藏的網址 (從 Secrets 讀取)
try:
    SHEET_URL = st.secrets["gsheet_url"]
except:
    st.error("❌ 尚未在 Streamlit 後台設定 Secrets (gsheet_url)！")
    st.stop()

# --- 2. 權限驗證 ---
st.sidebar.header("🔐 管理員登入")
pw = st.sidebar.text_input("輸入操作密碼", type="password")
is_admin = (pw == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("✅ 認證成功")
    menu = ["查看目前庫存", "➕ 新增商品入庫", "🤝 登記售出紀錄", "📊 查看銷售報表"]
else:
    st.sidebar.info("🔒 目前為一般檢視模式")
    menu = ["查看目前庫存"]

choice = st.sidebar.selectbox("切換功能", menu)

# --- 3. 建立雲端連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. 功能實作 ---

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 自動抓取「第一個」分頁，避免中文名稱辨識出錯
all_sheets = conn.read(spreadsheet=st.secrets["gsheet_url"], ttl=0)
df = all_sheets # 直接讀取預設的第一個分頁

# if choice == "查看目前庫存":
#     # 讀取庫存分頁
#     df = conn.read(spreadsheet=SHEET_URL, worksheet="庫存表", ttl=0)
#     st.write("### 📦 目前雲端庫存清單")
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#     else:
#         st.warning("目前暫無資料，請先新增商品。")

# elif choice == "➕ 新增商品入庫" and is_admin:
#     st.write("### ➕ 新增商品入庫")
#     existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="庫存表", ttl=0)
    
#     with st.form("add_form"):
#         col1, col2 = st.columns(2)
#         with col1:
#             name = st.text_input("商品名稱")
#             gbp = st.number_input("英鎊原價 (£)", min_value=0.0, step=0.1)
#         with col2:
#             stock = st.number_input("入庫數量", min_value=1, step=1)
#             rate = 42 # 預設匯率
        
#         submitted = st.form_submit_button("確認新增並同步雲端")
        
#         if submitted and name:
#             new_row = pd.DataFrame([{
#                 "商品名稱": name, 
#                 "英鎊原價": gbp, 
#                 "台幣售價": round(gbp * rate), 
#                 "庫存數量": stock
#             }])
#             updated_df = pd.concat([existing_df, new_row], ignore_index=True)
#             conn.update(spreadsheet=SHEET_URL, worksheet="庫存表", data=updated_df)
#             st.success(f"✅ {name} 已成功入庫！")
#             st.cache_data.clear()

# elif choice == "🤝 登記售出紀錄" and is_admin:
#     st.write("### 🤝 售出紀錄登記 (自動扣除庫存)")
#     inventory_df = conn.read(spreadsheet=SHEET_URL, worksheet="庫存表", ttl=0)
#     sales_df = conn.read(spreadsheet=SHEET_URL, worksheet="銷售紀錄", ttl=0)
    
#     if not inventory_df.empty:
#         with st.form("sales_form"):
#             item_to_sell = st.selectbox("選擇商品", inventory_df["商品名稱"].tolist())
#             sell_num = st.number_input("售出數量", min_value=1, step=1)
#             sell_date = st.date_input("售出日期", datetime.now())
#             confirm = st.form_submit_button("執行售出作業")
            
#             if confirm:
#                 idx = inventory_df[inventory_df["商品名稱"] == item_to_sell].index[0]
#                 current_stock = inventory_df.at[idx, "庫存數量"]
                
#                 if current_stock >= sell_num:
#                     # A. 扣除庫存
#                     inventory_df.at[idx, "庫存數量"] = current_stock - sell_num
#                     conn.update(spreadsheet=SHEET_URL, worksheet="庫存表", data=inventory_df)
                    
#                     # B. 寫入銷售紀錄
#                     new_sale = pd.DataFrame([{
#                         "商品名稱": item_to_sell,
#                         "售出數量": sell_num,
#                         "售出日期": sell_date.strftime("%Y-%m-%d")
#                     }])
#                     updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
#                     conn.update(spreadsheet=SHEET_URL, worksheet="銷售紀錄", data=updated_sales)
                    
#                     st.success(f"✅ 銷售成功！{item_to_sell} 庫存剩餘: {inventory_df.at[idx, '庫存數量']}")
#                     st.cache_data.clear()
#                 else:
#                     st.error(f"❌ 庫存不足！(目前剩餘: {current_stock})")
#     else:
#         st.error("庫存表中沒有任何商品。")

# elif choice == "📊 查看銷售報表":
#     st.write("### 📈 歷史銷售明細")
#     sales_data = conn.read(spreadsheet=SHEET_URL, worksheet="銷售紀錄", ttl=0)
#     if not sales_data.empty:
#         st.dataframe(sales_data, use_container_width=True)
#     else:
#         st.info("尚無銷售紀錄。")

