from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def init_gspread():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    # 讀取雲端 Secrets
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    
    client = gspread.authorize(creds)
    # 這是你目前使用的 Inventory_System 試算表 ID
    spreadsheet_id = '1Uyr_GSbMw53qBc7ZQ81ociX2eCll5B0Qrmudw1YRvaA' 
    return client.open_by_key(spreadsheet_id)

# 載入分頁
try:
    sh = init_gspread()
    inv_wks = sh.worksheet("庫存")
    hist_wks = sh.worksheet("紀錄")
except Exception as e:
    st.error(f"連線失敗：{e}")
    st.stop()

st.title("🧸 英國代購進銷貨系統")

# 左側邊欄：輸入介面
with st.sidebar:
    st.header("➕ 新增交易")
    
    with st.form("input_form", clear_on_submit=True):
        # 取得現有商品清單 (A欄)
        existing_items = [row[0] for row in inv_wks.get_all_values()[1:]]
        
        item_name = st.selectbox("商品名稱", options=["--手動新增--"] + existing_items)
        if item_name == "--手動新增--":
            item_name = st.text_input("輸入新商品名稱")
            
        qty = st.number_input("數量", min_value=1, step=1)
        
        # 直接輸入英鎊價格
        price_gbp = st.number_input("單價 (英鎊 £)", min_value=0.0, step=0.01)
        
        action_type = st.radio("動作類型", ["進貨", "銷貨"])
        submit_button = st.form_submit_button("確認提交並更新雲端")

    if submit_button and item_name:
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # A. 寫入「紀錄」分頁
        # 格式：時間, 類型, 商品, 數量, 英鎊單價
        hist_wks.append_row([today, action_type, item_name, qty, price_gbp])
        
        # B. 更新「庫存」分頁
        cell = inv_wks.find(item_name)
        if cell:
            # 依據你的試算表結構：C欄(3)是英鎊，E欄(5)是現貨數量
            current_qty = int(inv_wks.cell(cell.row, 5).value or 0)
            new_qty = current_qty + qty if action_type == "進貨" else current_qty - qty
            
            # 更新數量與英鎊價格
            inv_wks.update_cell(cell.row, 5, new_qty)
            inv_wks.update_cell(cell.row, 3, price_gbp)
            
            st.success(f"✅ {item_name} 已更新！目前庫存：{new_qty}")
        else:
            if action_type == "進貨":
                # 新商品：娃娃名稱(A), 款式(B), 英鎊(C), 台幣(D), 數量(E)
                # D欄暫時留空，或依需求填入資料
                new_row = [item_name, "", price_gbp, "", qty] 
                inv_wks.append_row(new_row)
                
                st.success(f"🆕 新商品 {item_name} 已加入庫存，數量：{qty}")
            else:
                # 如果是銷貨但找不到商品，給予提示
                st.warning(f"⚠️ 找不到商品「{item_name}」，無法執行銷貨扣除。")

