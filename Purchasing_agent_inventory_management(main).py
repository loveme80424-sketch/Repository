import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 基礎設定
ADMIN_PASSWORD = "你的密碼" # <--- 改成你要的密碼
st.set_page_config(page_title="英國代購管理系統", layout="wide")

st.title("🇬🇧 英國代購管理系統 (庫存與銷售同步)")

# 2. 建立 Google Sheets 連線
# 注意：這裡會自動抓取 Secrets 裡的 gsheet_url
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 側邊欄權限驗證
st.sidebar.header("🔐 權限驗證")
pw = st.sidebar.text_input("輸入操作密碼", type="password")
is_admin = (pw == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("✅ 已開啟編輯模式")
    menu = ["查看目前庫存", "➕ 新增商品"]
else:
    st.sidebar.info("🔒 檢視模式 (輸入密碼以編輯)")
    menu = ["查看目前庫存"]

choice = st.sidebar.selectbox("功能選單", menu)

# 4. 讀取資料 (不指定名稱，自動抓第一個分頁)
try:
    # 直接讀取，不帶 worksheet 參數，避免名稱不對報錯
    df = conn.read(spreadsheet=st.secrets["gsheet_url"], ttl=0)
    # 移除空行
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"❌ 連線失敗：請檢查 Google 試算表是否已開啟『知道連結的任何人都能編輯』權限。")
    st.stop()

# 5. 功能實作
if choice == "查看目前庫存":
    st.subheader("📦 目前雲端庫存")
    st.dataframe(df, use_container_width=True)

elif choice == "➕ 新增商品" and is_admin:
    st.subheader("新增商品資料")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("商品名稱")
            gbp = st.number_input("英鎊原價 (£)", min_value=0.0, step=0.1)
        with col2:
            stock = st.number_input("入庫數量", min_value=1, step=1)
            rate = 42 # 預設匯率
            
        submit = st.form_submit_button("確認新增並更新表單")
        
        if submit and name:
            # 建立新資料列
            new_data = pd.DataFrame([{
                "商品名稱": name,
                "英鎊原價": gbp,
                "庫存": stock,
                "台幣售價": int(gbp * rate)
            }])
            
            # 合併舊資料與新資料
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # 重點：直接寫入 Google Sheets
            conn.update(spreadsheet=st.secrets["gsheet_url"], data=updated_df)
            st.success(f"✅ 【{name}】已成功寫入雲端表單！")
            st.cache_data.clear() # 清除快取以便下次讀取看到最新資料
