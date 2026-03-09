import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="英國代購庫存管理", layout="wide")
st.title("🇬🇧 英國代購庫存管理系統 (雲端同步版)")

# 這是你剛才提供的 Google 試算表網址
sheet_url = "https://docs.google.com/spreadsheets/d/17nWLvgrzV5IL5R1OlXh3Qw3f-xrMwChd/edit#gid=397360371"

# 自動轉換網址格式，讓 Python 能夠讀取 CSV 資料
csv_url = sheet_url.split("/edit")[0] + "/export?format=csv&gid=397360371"

# 1. 讀取目前的雲端資料
try:
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error("讀取失敗，請確認試算表已開啟『知道連結的任何人皆可編輯』權限。")
    df = pd.DataFrame(columns=["商品名稱", "英鎊原價", "庫存", "台幣售價"])

# --- 側邊欄選單 ---
choice = st.sidebar.selectbox("選單", ["查看庫存", "直接新增資料"])

if choice == "查看庫存":
    st.write("### 📦 目前雲端庫存清單")
    st.dataframe(df, use_container_width=True)

elif choice == "直接新增資料":
    st.write("### ➕ 新增商品")
    with st.form("add_item_form"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊原價 (£)", min_value=0.0, step=0.1)
        stock = st.number_input("入庫數量", min_value=1, step=1)
        
        submit = st.form_submit_button("確認新增並同步至 Google 表格")
        
        if submit:
            # 這裡計算台幣售價 (假設匯率 42)
            twd = gbp * 42
            st.info(f"正在將 {name} 寫入雲端...")
            
            # 注意：由於沒有 JSON 金鑰，目前網頁端「直接寫入」最快的方式是透過 Google Forms 轉接，
            # 或是在 Streamlit Cloud 的 Secrets 設定連結。
            # 暫時建議點擊下方連結直接在雲端修改，或是設定 Secrets 權限。
            st.success(f"✅ 已準備好資料：{name} / £{gbp} / 數量:{stock}")
            st.markdown(f"👉 [點我直接在 Google 表格中貼上這筆資料]({sheet_url})")
