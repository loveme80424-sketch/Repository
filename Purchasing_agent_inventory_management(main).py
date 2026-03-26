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
    
    # ✅ 修正後的 ID (請確保引號內完全正確)
    spreadsheet_id = '1Uyr_GSbMw53qBc7ZQ81ociX2eCll5B0Qrmudw1YRvaA'
    
    return client.open_by_key(spreadsheet_id)

# 2. 更新資料核心邏輯
def update_data(item_name, qty, action_type, note, price_gbp):
    sh = init_gspread()
    inv_wks = sh.worksheet("庫存")
    hist_wks = sh.worksheet("紀錄")
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # --- 步驟 A：寫入【紀錄】分頁 ---
    # 格式：時間, 動作, 名稱, 數量, 售價(台幣), 備註
    # 銷貨時數量帶負數，進貨時帶正數
    final_qty = -qty if action_type == "銷貨" else qty
    hist_wks.append_row([now_str, action_type, item_name, final_qty, 0, note])
    
    # --- 步驟 B：更新【庫存】分頁 ---
    try:
        cell = inv_wks.find(item_name)
    except:
        cell = None

    # ... 前面是連線和定義變數 ...

    if cell:
        # --- 情況 1：找到舊商品 (更新現有的 C 欄或 D 欄) ---
        col_to_update = 3 if action_type == "進貨" else 4
        
        current_val = inv_wks.cell(cell.row, col_to_update).value
        try:
            current_val = int(current_val) if current_val else 0
        except:
            current_val = 0
            
        new_val = current_val + (qty if action_type == "進貨" else -qty)
        inv_wks.update_cell(cell.row, col_to_update, new_val)
        st.success(f"✅ 已成功更新庫存：{item_name}")
        
    else:
        # --- 情況 2：這是新商品 (就是放這裡！) ---
        # 欄位順序：A名稱, B英鎊, C進貨, D銷貨, E庫存(留空), F備註
        if action_type == "進貨":
            inv_wks.append_row([item_name, price_gbp, qty, 0, "", note])
        else:
            # 如果第一次建立就是銷貨(雖然少見)，進貨填0，銷貨填負數
            inv_wks.append_row([item_name, 0, 0, -qty, "", note])
            
        st.info(f"✨ 庫存表已自動新增品項：{item_name}")

    return True

# 3. Streamlit 介面
st.title("🇬🇧 英國代購庫存管理系統")

# 查看功能
if st.button("查看最新庫存表"):
    sh = init_gspread()
    data = sh.worksheet("庫存").get_all_records()
    st.table(pd.DataFrame(data))

st.divider()

# 輸入表單
with st.form("my_form", clear_on_submit=True):
    st.subheader("新增進銷貨紀錄")
    item = st.text_input("娃娃名稱/品項名稱")
    action = st.selectbox("動作類型", ["進貨", "銷貨"])
    qty = st.number_input("數量", min_value=1, step=1)
    gbp = st.number_input("英鎊單價", min_value=0.0)
    note = st.text_input("備註")
    
    submit = st.form_submit_button("確認提交至雲端")
    
    if submit:
        if item:
            # 💡 提示：請確保 Google Sheets 庫存分頁的 E2 公式為：
            # =ARRAYFORMULA(IF(A2:A="", "", C2:C + D2:D))
            # 且 E3 往下必須清空。
            update_data(item, qty, action, note, gbp)
            st.balloons() # 成功的特效
        else:
            st.error("請輸入品項名稱！")

st.info("💡 提示：請確保 Google Sheets 庫存分頁的 E2 公式已設定，且 E3 以下保持全空。")
