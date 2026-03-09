import streamlit as st
import pandas as pd

st.title("🇬🇧 英國代購庫存管理系統 (雲端同步版)")

# 這是你剛才提供的 Google 試算表網址
sheet_url = "https://docs.google.com/spreadsheets/d/17nWLvgRzV5IL5Ri0lXh3QW3f-xRnwChd/edit?gid=397360371#gid=397360371"

# 自動轉換網址格式，讓 Python 能夠讀取 CSV 資料
# 我們會處理網址結尾，確保它能正確導向 CSV 下載
if "/edit" in sheet_url:
    base_url = sheet_url.split("/edit")[0]
    # 提取 gid (工作表 ID)
    if "gid=" in sheet_url:
        gid = sheet_url.split("gid=")[1].split("#")[0]
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
    else:
        csv_url = f"{base_url}/export?format=csv"
else:
    csv_url = sheet_url

# 讀取雲端資料
try:
    df = pd.read_csv(csv_url)
    st.write("### 📦 目前雲端庫存清單")
    st.dataframe(df)
    
    # 統計資訊
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("商品總數", len(df))
    if "庫存數量" in df.columns:
        col2.metric("總庫存量", int(df["庫存數量"].sum()))

except Exception as e:
    st.error("讀取失敗！請確保你的 Google 試算表已開啟「知道連結的任何人都能編輯」權限。")
    st.info("目前的 CSV 轉換網址為: " + csv_url)

st.divider()
st.info(f"💡 [點我前往雲端表單手動修改資料]({sheet_url})")
st.caption("修改完試算表後，回到此網頁重新整理即可看到更新。")
