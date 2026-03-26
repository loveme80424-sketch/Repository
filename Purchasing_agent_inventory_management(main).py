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
    
    # 1. 寫入【紀錄】分頁 (日期, 類型, 名稱, 數量, 英鎊, 備註)
    hist_wks.append_row([now_str, action_type, item_name, qty, 0, note])
    
    # 2. 更新【庫存】分頁
    cell = inv_wks.find(item_name)
    
    if cell:
        # --- 核心修正：進貨對應第 3 欄(C)，銷貨對應第 4 欄(D) ---
        if action_type == "進貨":
            col_to_update = 3  # C 欄
        else:
            col_to_update = 4  # D 欄 (銷貨要在這裡更新)
        
        # 取得該格原本的數值
        current_val = inv_wks.cell(cell.row, col_to_update).value
        try:
            # 如果格子是空的或是非數字，就從 0 開始算
            current_val = int(current_val) if current_val else 0
        except:
            current_val = 0
            
        # 累加數量 (銷貨時 qty 會是負數，例如 10 + (-2) = 8)
        new_val = current_val + qty
        
        # 【重要】只更新指定欄位，絕對不准寫入第 5 欄 (E 欄)
        inv_wks.update_cell(cell.row, col_to_update, new_val)
        st.success(f"✅ 已在庫存表更新【{action_type}】：{item_name}")
        
    else:
        # 如果庫存表完全沒有這個品項，直接新增一行
        # 格式：[名稱(A), 英鎊(B), 進貨(C), 銷貨(D), 庫存公式(E)留空, 備註(F)]
        if action_type == "進貨":
            inv_wks.append_row([item_name, price_gbp, qty, 0, "", note])
        else:
            inv_wks.append_row([item_name, 0, 0, qty, "", note])
        st.info(f"✨ 庫存表已自動新增新品項：{item_name}")
    
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
