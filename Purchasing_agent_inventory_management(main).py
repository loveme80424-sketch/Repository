import pandas as pd
import os

# 設定 Excel 檔名
FILE_NAME = "英國代購庫存表.xlsx"

# 檢查是否有舊檔案，有的話就讀取，沒有就建立空的
if os.path.exists(FILE_NAME):
    df = pd.read_excel(FILE_NAME)
else:
    # 建立初始欄位
    df = pd.DataFrame(columns=["商品名稱", "英鎊原價", "台幣售價", "庫存數量"])


def save_to_excel():
    df.to_excel(FILE_NAME, index=False)
    print(f"--- 💾 資料已更新至 {FILE_NAME} ---")


while True:
    print("\n=== 英國代購管理系統 ===")
    print("1. 新增商品庫存")
    print("2. 售出商品（減少庫存）")
    print("3. 查看目前所有庫存")
    print("4. 離開系統")

    choice = input("請輸入選項 (1-4): ")

    if choice == "1":
        name = input("輸入商品名稱: ")
        gbp = float(input("輸入英鎊原價: "))
        stock = int(input("輸入入庫數量: "))
        exchange_rate = 42  # 你可以改成目前的匯率
        twd = gbp * exchange_rate

        # 新增一筆資料
        new_data = pd.DataFrame([{"商品名稱": name, "英鎊原價": gbp, "台幣售價": twd, "庫存數量": stock}])
        df = pd.concat([df, new_data], ignore_index=True)
        save_to_excel()

    elif choice == "2":
        name = input("輸入售出的商品名稱: ")
        if name in df["商品名稱"].values:
            num = int(input("輸入售出數量: "))
            # 找到該商品並減去庫存
            idx = df[df["商品名稱"] == name].index[0]
            if df.at[idx, "庫存數量"] >= num:
                df.at[idx, "庫存數量"] -= num
                print(f"✅ {name} 售出 {num} 件，剩餘庫存: {df.at[idx, '庫存數量']}")
                save_to_excel()
            else:
                print("❌ 錯誤：庫存不足！")
        else:
            print("❌ 找不到該商品！")

    elif choice == "3":
        print("\n--- 目前庫存清單 ---")
        print(df)

    elif choice == "4":
        print("系統關閉，祝生意興隆！")
        break
    else:
        print("無效選項，請重新輸入。")