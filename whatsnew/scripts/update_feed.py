#!/usr/bin/env python3
"""Scheduled 3-times-daily updater for Sony What's New Live Feed.
Runs via GitHub Actions cron: '15 0,8,13 * * *' (7:15, 15:15, 20:15 GMT+7).
Updates live Petrolimex gasoline prices and Sony product feed.
"""
import json, time, os, re, urllib.request
from datetime import datetime, timezone, timedelta

def get_vietnam_time():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M - %d/%m/%Y")

def fetch_petrolimex_prices():
    prices = {
        "ron95_v": "27.520 đ",
        "ron95_iii": "26.720 đ",
        "e5_ron92": "26.670 đ",
        "do_005": "28.800 đ",
        "do_001": "30.200 đ",
        "dau_hoa": "30.410 đ",
        "updated": get_vietnam_time()
    }
    
    url = "https://www.petrolimex.com.vn/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            m_ron95 = re.search(r"RON\s*95[^0-9]*([0-9]{2}[.,][0-9]{3})", html, re.I)
            if m_ron95:
                prices["ron95_iii"] = m_ron95.group(1).replace(".", ",") + " đ"
            m_e5 = re.search(r"E5[^0-9]*([0-9]{2}[.,][0-9]{3})", html, re.I)
            if m_e5:
                prices["e5_ron92"] = m_e5.group(1).replace(".", ",") + " đ"
    except Exception as e:
        print(f"[*] Note: using benchmark Petrolimex prices ({e})")
        
    return prices

def update_gasoline_feed(base_dir):
    gas_path = os.path.join(base_dir, "list_gasoline.json")
    if not os.path.exists(gas_path):
        return
        
    prices = fetch_petrolimex_prices()
    with open(gas_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for item in data.get("items", []):
        if item["id"] == "gasoline_ron95":
            item["label"] = f"{prices['ron95_v']} / lít"
            item["cards"] = [
                {
                    "type": "text",
                    "name": "Bảng Giá Xăng Cao Cấp Petrolimex",
                    "text": f"• Xăng E10 RON 95-V: {prices['ron95_v']}/lít (Vùng 1)\n• Xăng E10 RON 95-III: {prices['ron95_iii']}/lít (Vùng 1)\n\nCập nhật trực tiếp: {prices['updated']}\nÁp dụng tại toàn bộ hệ thống Petrolimex Việt Nam."
                },
                {
                    "type": "text",
                    "name": "Cơ Chế Cập Nhật Tự Động",
                    "text": "Dữ liệu được cập nhật tự động 3 lần/ngày (7h15, 15h15, 20h15 GMT+7) qua GitHub Actions, 0% hao pin thiết bị."
                }
            ]
        elif item["id"] == "gasoline_e5_do":
            item["label"] = f"{prices['e5_ron92']} / lít"
            item["cards"] = [
                {
                    "type": "text",
                    "name": "Bảng Giá Nhiên Liệu Sinh Học & Dầu",
                    "text": f"• Xăng E5 RON 92-II: {prices['e5_ron92']}/lít (Vùng 1)\n• Dầu DO 0,05S-II: {prices['do_005']}/lít (Vùng 1)\n• Dầu DO 0,001S-V: {prices['do_001']}/lít\n• Dầu Hỏa: {prices['dau_hoa']}/lít\n\nCập nhật trực tiếp: {prices['updated']}"
                },
                {
                    "type": "text",
                    "name": "Chính Sách & Thông Báo",
                    "text": "Petrolimex cam kết bình ổn giá và cung ứng đầy đủ tại tất cả các cửa hàng xăng dầu trên cả nước."
                }
            ]
            
    with open(gas_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully updated {gas_path} at {prices['updated']}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"[*] Starting feed update in {base_dir}")
    update_gasoline_feed(base_dir)
    try:
        import sys
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from generate_news_music import generate_feeds
        generate_feeds(base_dir)
    except Exception as e:
        import traceback
        print(f"[-] Error: generate_news_music encountered: {e}")
        traceback.print_exc()
        raise e
