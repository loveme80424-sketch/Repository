import streamlit as st
import pandas as pd

st.title("🇬🇧 英國代購庫存管理系統 (雲端同步版)")

# 這裡換成你從 Google 試算表複製來的「共用連結」
sheet_url = "https://docs.google.com/spreadsheets/d/https://docs.google.com/spreadsheets/d/17nWLvgRzV5IL5Ri0lXh3QW3f-xRnwChd/edit?gid=397360371#gid=397360371/edit"

# 自動將網址轉換成 CSV 下載格式，這樣 Python 才讀得到
if "/edit" in sheet_url:
    csv_url = sheet_url.split("/edit")[0] + "/export?format=csv"
else:
    csv_url = sheet_url

# 讀取雲端資料
try:
    df = pd.read_csv(csv_url)
    st.write("### 📦 目前雲端庫存")
    st.dataframe(df)
except Exception as e:
    st.error("讀取失敗，請確認試算表是否已開啟「知道連結的任何人都能檢視」權限。")

st.info(f"👉 [點我前往雲端表單手動修改資料]({sheet_url})")
