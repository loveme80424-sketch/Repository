import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. 初始化 Google Sheets 連線
def init_gspread():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    # 確保 ID 正確
    spreadsheet_id = '1Uyr_GSbMw53qBc7ZQ81ociX2eCll5B0Qrmudw1YRvaA'
    return client.open_by_key(spreadsheet_id)

# 2. 更新資料核心邏輯
def update_data(item_name, qty, action_type, note, price_gbp):
    sh = init_gspread()
    inv_wks = sh.worksheet("庫存")
    hist_wks = sh.worksheet("紀錄")
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 1. 寫入【紀錄】分頁 (維持原樣)
    hist_wks.append_row([now_str, action_type, item_name, qty, 0, note])
    
    # 2. 更新【庫存】分頁
    cell = inv_wks.find(item_name)
    
    if cell:
        # --- 修改重點：只更新第 3 欄(C) 或 第 4 欄(D) ---
        col_to_update = 3 if action_type == "進貨" else 4
        
        current_val = inv_wks.cell(cell.row, col_to_update).value
        try:
            current_val = int(current_val) if current_val else 0
        except:
            current_val = 0
            
        new_val = current_val + qty
        # 這裡只更新 C 或 D，絕對不要去碰 E 欄 (第 5 欄)！
        inv_wks.update_cell(cell.row, col_to_update, new_val)
        st.success(f"✅ 已更新：{item_name}")
    else:
        # 如果是新商品，直接新增一行，E 欄(第 5 格) 留空，讓公式自己算
        # 欄位：[名稱, 英鎊, 進貨, 銷貨, "", 備註]
        if action_type == "進貨":
            inv_wks.append_row([item_name, price_gbp, qty, 0, "", note])
        else:
            inv_wks.append_row([item_name, 0, 0, qty, "", note])
        st.info(f"✨ 庫存表已自動新增品項：{item_name}")
    
    return True

# --- Streamlit 介面 ---
st.title("🇬🇧 英國代購庫存管理系統")

# 顯示目前庫存
if st.button("查看最新庫存表"):
    sh = init_gspread()
    data = sh.worksheet("庫存").get_all_records()
    st.table(pd.DataFrame(data))

st.divider()

with st.form("my_form", clear_on_submit=True):
    item = st.text_input("娃娃名稱/客戶名稱")
    action = st.selectbox("類型", ["進貨", "銷貨"])
    qty = st.number_input("數量", min_value=1, step=1)
    gbp = st.number_input("英鎊價格", min_value=0.0)
    note = st.text_input("備註")
    
    submit = st.form_submit_button("確認送出")
    
    if submit:
        if item:
            # 銷貨自動轉負數以符合你的表格加總邏輯 (D + E = F)
            final_qty = qty if action == "進貨" else -qty
            update_data(item, final_qty, action, note, gbp)
        else:
            st.error("請輸入名稱！")
