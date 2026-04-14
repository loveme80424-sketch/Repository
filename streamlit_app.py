import streamlit as st
import twder
from datetime import datetime

# 設定網頁標題
st.set_page_config(page_title="娃娃售價計算器", layout="centered")

def get_gbp_twd_details():
    try:
        # twder.now('GBP') 回傳: [時間, 現金買入, 現金賣出, 即期買入, 即期賣出]
        rate_data = twder.now('GBP')
        return {
            "time": rate_data[0],
            "cash_buy": rate_data[1],
            "cash_sell": rate_data[2],
            "spot_buy": rate_data[3],
            "spot_sell": float(rate_data[4]),
            "success": True
        }
    except Exception:
        return {"spot_sell": 43.5, "success": False, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}

# 取得資料
rate_info = get_gbp_twd_details()

st.title("🧸 娃娃代購售價計算器")

# --- 側邊欄顯示匯率資訊 ---
with st.sidebar:
    st.header("🏦 台銀即時匯率")
    if rate_info["success"]:
        st.success(f"英鎊 (GBP) 讀取成功")
        st.metric("即期賣出 (最常用)", rate_info["spot_sell"])
        st.write(f"**更新時間：**\n{rate_info['time']}")
        st.divider()
        st.caption("其他參考值：")
        st.text(f"即期買入: {rate_info['spot_buy']}")
        st.text(f"現金賣出: {rate_info['cash_sell']}")
    else:
        st.error("無法連線至台銀，使用預設匯率")
        st.metric("預設匯率", rate_info["spot_sell"])

# --- 主畫面計算區 ---
# 1. 匯率部分 (預設帶入抓到的即期賣出)
rate = st.number_input("確認計算匯率", value=rate_info["spot_sell"], step=0.1)

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

# 4. 計算公式
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
