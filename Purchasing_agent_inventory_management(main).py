import streamlit as st
import pandas as pd

# ==========================================
# 1. 基本設定（請在此修改你的資訊）
# ==========================================
ADMIN_PASSWORD = "jennyrose00"  # <--- 請改掉這個密碼
SHEET_URL = "https://docs.google.com/spreadsheets/d/17nWLvgRzV5IL5Ri0lXh3QW3f-xRnwChd/edit?gid=397360371#gid=397360371" # <--- 請貼上你的試算表連結

st.set_page_config(page_title="英國代購庫存管理", layout="wide")
st.title("🇬🇧 英國代購庫存管理系統 (安全整合版)")

# ==========================================
# 2. 權限驗證與側邊欄
# ==========================================
st.sidebar.header("🔐 權限驗證")
user_password = st.sidebar.text_input("輸入操作密碼", type="password")

if user_password == ADMIN_PASSWORD:
    st.sidebar.success("✅ 認證成功：已開啟編輯權限")
    is_admin = True
    menu = ["查看目前庫存", "新增商品庫存", "售出商品"]
else:
    if user_password != "":
        st.sidebar.error("❌ 密碼錯誤")
    is_admin = False
    st.sidebar.info("🔒 目前為檢視模式")
    menu = ["查看目前庫存"]

choice = st.sidebar.selectbox("功能選單", menu)

# ==========================================
# 3. 資料讀取邏輯 (Google Sheets)
# ==========================================
# 將網址轉換為 CSV 下載格式以便讀取
if "/edit" in SHEET_URL:
    csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
    if "gid=" in SHEET_URL:
        gid = SHEET_URL.split("gid=")[1].split("#")[0]
        csv_url += f"&gid={gid}"
else:
    csv_url = SHEET_URL

@st.cache_data(ttl=60) # 每 60 秒快取一次，避免頻繁抓取
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"讀取失敗：請確認試算表已開啟『知道連結的任何人都能編輯』權限。")
        return pd.DataFrame()

df = load_data(csv_url)

# ==========================================
# 4. 各項功能實作
# ==========================================

if choice == "查看目前庫存":
    st.write("### 📦 目前雲端庫存清單")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # 下載功能
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載目前庫存報表 (CSV)", data=csv_data, file_name="inventory.csv", mime="text/csv")
    else:
        st.warning("目前暫無資料或讀取失敗。")

elif choice == "新增商品庫存" and is_admin:
    st.write("### ➕ 新增商品至 Google 表格")
    st.info("💡 由於網頁安全限制，請點擊下方連結直接在表格中輸入，完成後重新整理此網頁即可。")
    st.markdown(f"👉 [點我開啟 Google 試算表直接編輯]({SHEET_URL})")
    
    with st.expander("快速計算小工具"):
        name = st.text_input("商品名稱")
        gbp = st.number_input("英鎊原價 (£)", min_value=0.0, step=0.1)
        rate = 42 # 匯率設定
        twd = gbp * rate
        st.write(f"💰 自動換算台幣 (匯率 {rate}): **${twd:,.0f}**")

elif choice == "售出商品" and is_admin:
    st.write("### 🤝 登記售出")
    if not df.empty and "商品名稱" in df.columns:
        selected_item = st.selectbox("選擇已售出的商品", df["商品名稱"].tolist())
        st.info(f"請至 Google 表格中手動扣除「{selected_item}」的庫存數量。")
        st.markdown(f"👉 [前往表格更新庫存]({SHEET_URL})")
    else:
        st.error("無法讀取商品清單，請確認試算表內容。")

# ==========================================
# 5. 頁尾提醒
# ==========================================
st.divider()
st.caption("備註：本系統與 Google Sheets 即時同步。若修改了表格，請重新整理網頁以更新顯示。")
