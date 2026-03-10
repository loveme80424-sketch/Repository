import streamlit as st
import pandas as pd
import datetime
import os

FILE_NAME = '英國代購庫存表.xlsx'


# 初始化 Excel 檔案
def init_excel():
    if not os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            pd.DataFrame(columns=['商品名稱', '目前庫存', '英鎊價格']).to_excel(writer, sheet_name='庫存', index=False)
            pd.DataFrame(columns=['日期', '類型', '商品名稱', '數量', '單價', '備註']).to_excel(writer,
                                                                                                sheet_name='紀錄',
                                                                                                index=False)


init_excel()

st.title("🇬🇧 英國代購庫存管理系統")

# --- 側邊欄：輸入區 ---
st.sidebar.header("新增資料")
item_name = st.sidebar.text_input("商品名稱")
qty = st.sidebar.number_input("數量", min_value=1, value=1)
price = st.sidebar.number_input("單價 (GB)", min_value=0, value=0)
action_type = st.sidebar.selectbox("動作類型", ["進貨", "銷貨"])
Remark_name = st.sidebar.text_input("備註")

if st.sidebar.button("確認提交"):
    # 讀取現有資料
    inv = pd.read_excel(FILE_NAME, sheet_name='庫存')
    hist = pd.read_excel(FILE_NAME, sheet_name='紀錄')

    # 更新紀錄
    new_record = {
        '日期': datetime.date.today().strftime("%Y-%m-%d"),
        '類型': action_type,
        '商品名稱': item_name,
        '數量': qty,
        '單價': price,
        '備註': Remark_name,
    }
    hist = pd.concat([hist, pd.DataFrame([new_record])], ignore_index=True)

    # 更新庫存邏輯
    if item_name in inv['商品名稱'].values:
        idx = inv[inv['商品名稱'] == item_name].index[0]
        if action_type == "進貨":
            inv.at[idx, '目前庫存'] += qty
        else:
            inv.at[idx, '目前庫存'] -= qty
    else:
        new_inv = {'商品名稱': item_name, '目前庫存': qty, '平均成本': price}
        inv = pd.concat([inv, pd.DataFrame([new_inv])], ignore_index=True)

    # 存檔
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
        inv.to_excel(writer, sheet_name='庫存', index=False)
        hist.to_excel(writer, sheet_name='紀錄', index=False)
    st.success(f"已完成 {item_name} 的 {action_type}！")

# --- 主畫面：顯示資料 ---
st.subheader("📦 目前庫存狀態")
current_inv = pd.read_excel(FILE_NAME, sheet_name='庫存')
st.dataframe(current_inv, use_container_width=True)

st.subheader("📜 最近交易紀錄")
current_hist = pd.read_excel(FILE_NAME, sheet_name='紀錄')
st.table(current_hist.tail(5))  # 顯示最後 5 筆
