import streamlit as st
import yfinance as yf

# 設定網頁標題
st.set_page_config(page_title="娃娃售價計算器", layout="centered")

def get_gbp_twd_rate():
    try:
        ticker = yf.Ticker("GBPTWD=X")
        data = ticker.history(period="1d")
        return round(data['Close'].iloc[-1], 2)
    except:
        return 42.7  # 抓取失敗時的預設值

st.title("🧸 娃娃代購售價計算器")

# 1. 匯率部分
live_rate = get_gbp_twd_rate()
rate = st.number_input("英鎊匯率", value=live_rate, step=0.1, help="自動抓取最新匯率，也可手動修改")

# 2. 輸入原價
gbp_price = st.number_input("英鎊售價 (GBP)", min_value=0.0, value=10.0, step=0.5)

# 3. 選擇尺寸
size = st.selectbox(
    "娃娃尺寸 (國際運費選項)",
    ["迷你娃娃 (運費 40)", "小娃娃 (運費 200)", "大娃娃 (運費 350)"]
)

# 運費邏輯
shipping_map = {
    "迷你娃娃 (運費 40)": 0.5 * 80,
    "小娃娃 (運費 200)": 0.5 * 400,
    "大娃娃 (運費 350)": 0.5 * 700
}
intl_shipping = shipping_map[size]

# 4. 計算
base_twd = gbp_price * rate
tax = base_twd * 0.05
transport_fee = 80
total = base_twd + tax + transport_fee + intl_shipping

# 5. 顯示結果
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("建議總售價 (TWD)", f"{round(total)} 元")
with col2:
    st.write(f"**成本明細：**")
    st.caption(f"台幣原價：{base_twd:.1f} 元")
    st.caption(f"5% 營業稅：{tax:.1f} 元")
    st.caption(f"交通成本：{transport_fee} 元")
    st.caption(f"國際運費：{intl_shipping:.0f} 元")
