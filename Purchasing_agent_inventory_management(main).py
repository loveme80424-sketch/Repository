import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 密碼鎖設定
ADMIN_PASSWORD = "jennyrose00" 

st.set_page_config(page_title="英國代購系統", layout="wide")
st.title("🇬🇧 英國代購庫存管理 (直接修復版)")

# 2. 建立連線 (這裡最容易報 HTTPError)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 讀取資料：採用「不指定分頁」策略，避免名稱不對
try:
    # 直接抓 Secrets 裡的網址，不帶任何 worksheet 參數
    # 這樣它會自動抓試算表中的「第一個」標籤頁
    df = conn.read(spreadsheet=st.secrets["gsheet_url"], ttl=0)
    df = df.dropna(how="all") # 移除空行
except Exception as e:
    st.error("⚠️ 連線還是失敗了！請檢查下方兩點：")
    st.info(f"原始錯誤訊息: {e}")
    st.markdown("1. **Secrets 網址**：請確認結尾是 `edit?usp=sharing` 而不是 `drive_link`。")
    st.markdown("2. **Google 權限**：請再次確認試算表右上角『共用』已設為『知道連結的任何人』+『編輯者』並按下『完成』。")
    st.stop()

# 4. 側邊欄與選單
st.sidebar.header("🔐 權限驗證")
pw = st.sidebar.text_input("輸入操作密碼", type="password")
is_admin = (pw == ADMIN_PASSWORD)

menu = ["查看庫存"]
if is_admin:
    menu.append("➕ 新增商品")

choice = st.sidebar.selectbox("選單", menu)

# 5. 功能實作
if choice == "查看庫存":
    st.dataframe(df, use_container_width=True)

elif choice == "➕ 新增商品":
    with st.form("add_item"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊 (£)", min_value=0.0)
        stock = st.number_input("數量", min_value=1)
        if st.form_submit_button("送出"):
            # 建立新列並合併
            new_row = pd.DataFrame([{"商品名稱": name, "英鎊原價": gbp, "庫存": stock, "台幣售價": int(gbp*42)}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            # 寫入雲端
            conn.update(spreadsheet=st.secrets["gsheet_url"], data=updated_df)
            st.success("更新成功！請重新整理頁面。")
            st.cache_data.clear()
