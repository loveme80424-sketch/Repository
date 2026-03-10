import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔍 系統連線診斷工具")

# 1. 檢查 Secrets 是否讀取成功
try:
    test_url = st.secrets["gsheet_url"]
    st.success(f"✅ 已讀取到 Secrets 網址")
except Exception as e:
    st.error(f"❌ 無法讀取 Secrets: {e}")
    st.stop()

# 2. 嘗試建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 測試讀取：這段會印出所有分頁名稱，幫我們抓錯
try:
    st.write("正在嘗試抓取試算表資訊...")
    
    # 這裡不指定 worksheet，讓它抓取整個試算表物件
    # 如果這裡報錯，代表「網址」或「權限」有問題
    # 不要寫 worksheet="庫存表"，直接讓它讀取預設的第一張表
df = conn.read(spreadsheet=st.secrets["gsheet_url"], ttl=0)
    
    st.success("✅ 成功連線到 Google Sheets！")
    st.write("### 📊 偵測到的資料內容：")
    st.dataframe(raw_data)

except Exception as e:
    st.error("⚠️ 連線失敗診斷報告：")
    st.code(str(e))
    
    if "400" in str(e):
        st.warning("💡 錯誤代碼 400：通常是網址格式錯誤。請檢查 Secrets 裡的網址是否包含多餘的空白或字元。")
    if "403" in str(e):
        st.warning("💡 錯誤代碼 403：權限不足。請再次確認 Google 試算表是否已設為『知道連結的任何人皆可編輯』。")
    
    st.write("---")
    st.write("📋 **請將上面的紅色錯誤訊息截圖給我，我能直接看出問題在哪。**")

