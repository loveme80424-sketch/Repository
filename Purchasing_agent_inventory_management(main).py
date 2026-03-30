import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 設定網頁標題與圖示
st.set_page_config(page_title="英國代購庫存管理", page_icon="🇬🇧")

# 1. 初始化 Google Sheets 連線
def init_gspread():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # ✅ 確認過的試算表 ID
        spreadsheet_id = '1Uyr_GSbMw53qBc7ZQ81ociX2eCll5B0Qrmudw1YRvaA'
        return client.open_by_key(spreadsheet_id)
    except Exception as e:
        st.error(f"連線至 Google Sheets 失敗: {e}")
        return None

# 2. 更新資料核心邏輯
def update_data(item_name, qty, action_type, note, price_gbp):
    sh = init_gspread()
    if not sh: return False
    
    try:
        inv_wks = sh.worksheet("庫存")
        hist_wks = sh.worksheet("紀錄")
        
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # --- 步驟 A：寫入【紀錄】分頁 ---
        # 銷貨時數量顯示為負數，方便直接在紀錄分頁加總看變動
        final_qty = -qty if action_type == "銷貨" else qty
        hist_wks.append_row([now_str, action_type, item_name, final_qty, 0, note])
        
        # --- 步驟 B：更新【庫存】分頁 ---
        try:
            cell = inv_wks.find(item_name)
        except:
            cell = None

        if cell:
            # 情況 1：找到舊商品
            col_to_update = 3 if action_type == "進貨" else 4
            
            # 取得目前格子裡的值
            current_val = inv_wks.cell(cell.row, col_to_update).value
            try:
                current_val = int(current_val) if current_val else 0
            except:
                current_val = 0
            
            # 進貨加正數，銷貨加負數
            new_val = current_val + (qty if action_type == "進貨" else -qty)
            
            # 只更新 C 或 D 欄，絕對不碰 E 欄
            inv_wks.update_cell(cell.row, col_to_update, new_val)
            st.success(f"✅ 已成功更新庫存：{item_name}")
            
        else:
            # 情況 2：新商品
            # 欄位順序：A名稱, B英鎊, C進貨, D銷貨, E庫存(留空), F備註
            if action_type == "進貨":
                inv_wks.append_row([item_name, price_gbp, qty, 0, "", note])
            else:
                # 先銷貨：進貨填 0，銷貨填負數，E 欄必須是空字串 ""
                inv_wks.append_row([item_name, 0, 0, -qty, "", note])
                
            st.info(f"✨ 庫存表已自動新增品項：{item_name}")
        return True
    except Exception as e:
        st.error(f"寫入資料時發生錯誤: {e}")
        return False

# 3. Streamlit 介面
st.title("🇬🇧 英國代購庫存管理系統")

# 查看功能
if st.button("查看最新庫存表"):
    sh = init_gspread()
    if sh:
        try:
            data = sh.worksheet("庫存").get_all_records()
            if data:
                st.table(pd.DataFrame(data))
            else:
                st.write("目前庫存表是空的。")
        except Exception as e:
            st.error(f"讀取資料表失敗，請確認分頁名稱是否為『庫存』: {e}")

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
            with st.spinner('正在同步至 Google Sheets...'):
                if update_data(item, qty, action, note, gbp):
                    st.balloons()
        else:
            st.error("請輸入品項名稱！")

st.info("💡 提示：請確保 Google Sheets 庫存分頁的 E2 公式已設定為 ARRAYFORMULA，且 E3 以下保持全空。")
