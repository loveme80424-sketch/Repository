import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 1. 初始化 Google Sheets 連線 (使用 Streamlit Secrets)
def init_gspread():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # 這裡會讀取你在 Streamlit 網頁設定的 Secrets
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    # 請確保這是你最新的試算表 ID
    spreadsheet_id = '1Uyr_GSbMw53qBc7ZQ81ociX2eCll5B0Qrmudw1YRvaA'
    return client.open_by_key(spreadsheet_id)

# 2. 更新庫存與紀錄的邏輯
def update_data(item_name, qty, action_type, note, price_gbp):
    sh = init_gspread()
    inv_wks = sh.worksheet("庫存")
    hist_wks = sh.worksheet("紀錄")
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # A. 寫入【紀錄】分頁 (日期, 類型, 名稱, 數量, 英鎊單價, 備註)
    hist_wks.append_row([now_str, action_type, item_name, qty, price_gbp, note])
    
    #B. --- 更新【庫存】分頁的強化邏輯 ---
    cell = inv_wks.find(item_name)
    
    if cell:
        # A. 如果找到了，就更新那一行的數字
        col_to_update = 4 if action_type == "進貨" else 5
        current_val = inv_wks.cell(cell.row, col_to_update).value
        current_val = int(current_val) if current_val and str(current_val).isdigit() else 0
        new_val = current_val + qty
        inv_wks.update_cell(cell.row, col_to_update, new_val)
    else:
        # B. 如果【找不到名稱】，就直接在最下面新增一行
        # 欄位順序：娃娃名稱(A), 英鎊(B), 台幣(C), 進貨(D), 銷貨(E)
        if action_type == "進貨":
            # 新增一行：[名稱, 英鎊價格, 0, 數量, 0]
            inv_wks.append_row([item_name, price_gbp, 0, qty, 0])
        else:
            # 銷貨情況下新增（通常不建議，但為了程式不報錯）：[名稱, 0, 0, 0, 數量]
            inv_wks.append_row([item_name, 0, 0, 0, qty])
        
        st.info(f"✨ 庫存表原本沒有「{item_name}」，已自動為您新增該品項！")

# --- Streamlit 介面 ---
st.title("🇬🇧 英國代購雲端庫存系統")

# 顯示目前庫存 (從 Google Sheets 讀取)
if st.button("更新/讀取最新庫存"):
    sh = init_gspread()
    df = pd.DataFrame(sh.worksheet("庫存").get_all_records())
    st.dataframe(df)

st.divider()

# 輸入表單
with st.form("inventory_form", clear_on_submit=True):
    st.subheader("新增進銷貨紀錄")
    
    col1, col2 = st.columns(2)
    with col1:
        item = st.text_input("娃娃名稱 (需與 Excel 一致)")
        action = st.selectbox("動作類型", ["進貨", "銷貨"])
    
    with col2:
        # 如果是銷貨，自動建議輸入負數，或者你在這裡處理
        qty = st.number_input("數量", step=1)
        gbp = st.number_input("英鎊單價 (選填)", min_value=0.0)
    
    note = st.text_input("備註 (例如：客人王小姐預訂)")
    
    submit = st.form_submit_button("確認提交至雲端")
    
    if submit:
        if item:
            # 自動處理銷貨數量為負數 (為了符合你表格 進+銷=現貨 的邏輯)
            final_qty = qty if action == "進貨" else -abs(qty)
            
            success = update_data(item, final_qty, action, note, gbp)
            if success:
                st.success(f"✅ 已成功同步！品項：{item} | 數量：{final_qty} | 備註：{note}")
        else:
            st.warning("請輸入娃娃名稱")

st.info("💡 提示：請確保 Google Sheets 的 F 欄公式為 `=D2+E2`，即可自動計算現貨。")

