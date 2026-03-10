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
    
    # B. 更新【庫存】分頁
    cell = inv_wks.find(item_name)
    if cell:
        # 根據你的表格欄位：D欄(4)是進貨，E欄(5)是銷貨
        col_to_update = 4 if action_type == "進貨" else 5
        
        # 讀取原本數值 (若空白則設為 0)
        current_val = inv_wks.cell(cell.row, col_to_update).value
        current_val = int(current_val) if current_val and str(current_val).isdigit() else 0
        
        # 累加新數量 (銷貨如果是輸入正數，這裡要用加的，因為公式是 進+銷)
        # 如果你銷貨習慣打 5，表格就會變 -5，這裡我們統一用加法
        new_val = current_val + qty
        inv_wks.update_cell(cell.row, col_to_update, new_val)
        return True
    else:
        st.error(f"找不到商品：{item_name}，請先手動在 Excel 新增該品項名稱。")
        return False

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
