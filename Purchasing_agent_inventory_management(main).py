import streamlit as st
import pandas as pd

# 1. 密碼鎖
ADMIN_PASSWORD = "1123" 

st.title("🇬🇧 英國代購管理 (穩定讀取版)")

# 2. 核心：將 Google Sheets 網址轉換為 CSV 格式 (這行最重要)
def get_csv_url(url):
    # 強制將網址結尾換成 export?format=csv，這能繞過 99% 的讀取錯誤
    if "/edit" in url:
        return url.split("/edit")[0] + "/export?format=csv"
    return url

# 3. 讀取資料 (直接用 pandas 抓，不透過連線套件)
try:
    # 從 Secrets 抓網址並轉換
    raw_url = st.secrets["gsheet_url"]
    csv_url = get_csv_url(raw_url)
    
    # 讀取資料，不指定分頁名稱，直接讀取預設內容
    df = pd.read_csv(csv_url)
    df = df.dropna(how="all") # 移除空行
    st.success("✅ 資料讀取成功！")
except Exception as e:
    st.error(f"❌ 讀取依舊失敗：{e}")
    st.info("請檢查 Secrets 裡的網址是否正確包在雙引號內。")
    st.stop()

# 4. 功能顯示
st.sidebar.header("🔐 權限驗證")
pw = st.sidebar.text_input("輸入密碼", type="password")

if pw == ADMIN_PASSWORD:
    st.write("### 📦 庫存管理模式")
    # 讓你可以直接在網頁上編輯表格
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 下載修改後的報表 (CSV)"):
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("點我下載", csv, "updated_inventory.csv", "text/csv")
        st.info("💡 提醒：此版本為穩定讀取版。修改後請下載並上傳回 Google 表格，或點擊下方連結手動更新。")
else:
    st.write("### 📦 目前庫存清單 (唯讀)")
    st.dataframe(df, use_container_width=True)

# 5. 直接跳轉編輯
st.markdown(f"👉 [點我開啟 Google 試算表直接修改資料]({st.secrets['gsheet_url']})")
