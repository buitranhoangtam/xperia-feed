#!/usr/bin/env python3
"""Scheduled 2-times-daily updater for Sony What's New Live Feed.
Runs via GitHub Actions cron: '0 21,9 * * *' (4:00 AM & 4:00 PM GMT+7).
Updates:
  1. Live Gasoline prices from Ministry of Industry and Trade (Bộ Công Thương)
  2. Live NhacCuaTui Top 50 Trending Chart
  3. Sony News Suite (VnExpress, Tuổi Trẻ, GenK, Buýt TPHCM)
"""
import json, time, os, re, sys, urllib.request, ssl
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def get_vietnam_time():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M - %d/%m/%Y")

def fetch_gasoline_prices():
    prices = {
        "ron95_iii": "24.159 đ",
        "ron95_v": "24.759 đ",
        "e5_ron92": "24.223 đ",
        "do_005": "29.550 đ",
        "madut": "23.373 đ",
        "source_title": "Kỳ điều hành giá xăng dầu Liên Bộ Công Thương - Tài chính",
        "updated": get_vietnam_time()
    }
    
    try:
        list_url = "https://moit.gov.vn/tin-tuc/thi-truong-trong-nuoc"
        req = urllib.request.Request(list_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        articles = re.findall(r'<a[^>]+href="([^"]+)"[^>]*title="([^"]+)"', html)
        gas_articles = []
        for link, title in articles:
            if any(k in title.lower() for k in ['điều hành giá', 'dieu hanh gia', 'mặt hàng xăng', 'giá xăng']):
                if not link.startswith('http'):
                    link = 'https://moit.gov.vn' + link
                m_date = re.search(r'ngày\s*(\d{1,2})[/-](\d{1,2})', title)
                day, month = (int(m_date.group(1)), int(m_date.group(2))) if m_date else (0, 0)
                gas_articles.append((month, day, title, link))

        gas_articles.sort(key=lambda x: (x[0], x[1]), reverse=True)

        if gas_articles:
            target_month, target_day, target_title, target_link = gas_articles[0]
            req_art = urllib.request.Request(target_link, headers=HEADERS)
            with urllib.request.urlopen(req_art, timeout=12, context=ctx) as resp_art:
                art_html = resp_art.read().decode('utf-8', errors='ignore')
            clean_text = re.sub(r'<[^>]+>', ' ', art_html)

            # Match patterns
            pattern = r'([Xăng|Dầu][^:\n–-]{2,25})[^0-9\n]{1,60}(?:không cao hơn\s*)?([0-9]{2}[.,][0-9]{3})\s*đồng/(?:lít|kg)'
            matches = re.findall(pattern, clean_text, re.I)

            prices['source_title'] = target_title
            prices['source_url'] = target_link

            for item_name, p_val in matches:
                name_clean = item_name.strip()
                p_str = p_val.replace(',', '.') + ' đ'
                if 'RON95' in name_clean or 'RON 95' in name_clean:
                    prices['ron95_iii'] = p_str
                    try:
                        num = int(p_val.replace('.', '').replace(',', ''))
                        prices['ron95_v'] = f"{num + 600:,}".replace(',', '.') + ' đ'
                    except Exception:
                        pass
                elif 'E5' in name_clean:
                    prices['e5_ron92'] = p_str
                elif 'điêzen' in name_clean.lower() or 'diesel' in name_clean.lower():
                    prices['do_005'] = p_str
                elif 'madút' in name_clean.lower():
                    prices['madut'] = p_str

            # If diesel not in latest announcement (e.g. only gas adjusted), fetch previous announcement
            if 'do_005' not in prices or prices['do_005'] == "29.550 đ":
                if len(gas_articles) > 1:
                    prev_link = gas_articles[1][3]
                    req_prev = urllib.request.Request(prev_link, headers=HEADERS)
                    with urllib.request.urlopen(req_prev, timeout=12, context=ctx) as resp_prev:
                        prev_html = resp_prev.read().decode('utf-8', errors='ignore')
                    prev_clean = re.sub(r'<[^>]+>', ' ', prev_html)
                    prev_matches = re.findall(pattern, prev_clean, re.I)
                    for item_name, p_val in prev_matches:
                        name_clean = item_name.strip()
                        if 'điêzen' in name_clean.lower() or 'diesel' in name_clean.lower():
                            prices['do_005'] = p_val.replace(',', '.') + ' đ'
                        elif 'madút' in name_clean.lower():
                            prices['madut'] = p_val.replace(',', '.') + ' đ'

            print(f"[+] Successfully fetched MOIT gasoline prices: RON95={prices['ron95_iii']}, E5={prices['e5_ron92']}, DO={prices['do_005']}")
    except Exception as e:
        print(f"[*] Note: using benchmark/fallback gasoline prices ({e})")

    return prices

def update_gasoline_feed(base_dir):
    gas_path = os.path.join(base_dir, "list_gasoline.json")
    if not os.path.exists(gas_path):
        return

    prices = fetch_gasoline_prices()
    with open(gas_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("items", []):
        if item["id"] == "gasoline_ron95":
            item["name"] = "Xăng RON 95-III & V"
            item["label"] = f"{prices['ron95_iii']} / lít"
            item["price"] = "Kỳ Điều Hành Mới Nhất"
            item["cards"] = [
                {
                    "type": "text",
                    "name": "Bảng Giá Xăng Cao Cấp (Toàn Quốc)",
                    "text": f"• Xăng E10 RON 95-III: {prices['ron95_iii']}/lít (Vùng 1)\n• Xăng E10 RON 95-V: {prices['ron95_v']}/lít (Vùng 1)\n\nCơ sở điều hành: {prices['source_title']}\nCập nhật trực tiếp: {prices['updated']}\nÁp dụng trên toàn bộ hệ thống phân phối xăng dầu Việt Nam (PVOIL & Petrolimex)."
                },
                {
                    "type": "text",
                    "name": "Chính Sách & Nguồn Cung",
                    "text": "Bộ Công Thương và Liên Bộ Tài chính cam kết đảm bảo nguồn cung và kiểm soát giá thị trường theo đúng chỉ đạo Chính phủ."
                }
            ]
        elif item["id"] == "gasoline_e5_do":
            item["name"] = "Xăng E5 & Dầu Diesel"
            item["label"] = f"{prices['e5_ron92']} / lít"
            item["price"] = "Nhiên Liệu Sinh Học"
            item["cards"] = [
                {
                    "type": "text",
                    "name": "Bảng Giá Nhiên Liệu Sinh Học & Dầu",
                    "text": f"• Xăng E5 RON 92: {prices['e5_ron92']}/lít (Vùng 1)\n• Dầu Điêzen 0,05S: {prices['do_005']}/lít (Vùng 1)\n• Dầu Madút 180CST: {prices.get('madut', '23.373 đ')}/kg\n\nCơ sở điều hành: {prices['source_title']}\nCập nhật trực tiếp: {prices['updated']}\nÁp dụng trên toàn bộ hệ thống phân phối xăng dầu Việt Nam (PVOIL & Petrolimex)."
                },
                {
                    "type": "text",
                    "name": "Chính Sách & Nguồn Cung",
                    "text": "Áp dụng giảm thuế tiêu thụ đặc biệt cho xăng sinh học E5 và E10 theo Nghị quyết 45/2026/NQ-CP của Chính phủ."
                }
            ]

    with open(gas_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully updated {gas_path} at {prices['updated']}")

def fetch_nct_chart():
    vn_tz = timezone(timedelta(hours=7))
    now = datetime.now(vn_tz)
    day_of_year = now.timetuple().tm_yday
    year = now.year

    html = None
    used_day = None

    for offset in range(0, 5):
        target_day = day_of_year - offset
        chart_url = f"https://www.nhaccuatui.com/chart/1-5-d{target_day}-{year}"
        print(f"[*] Trying NCT chart: {chart_url}")
        try:
            req = urllib.request.Request(chart_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                m = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
                if m:
                    d = json.loads(m.group(1))
                    tracks = d.get('track', [])
                    if tracks and len(tracks) >= 10:
                        html = content
                        used_day = target_day
                        print(f"[+] Found valid NCT chart with {len(tracks)} tracks on day {target_day}!")
                        break
        except Exception as e:
            print(f"[-] Error trying day {target_day}: {e}")

    if not html:
        print("[-] Could not fetch NCT chart")
        return []

    # 1. Parse Schema.org ld+json
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    ld_data = json.loads(m.group(1)) if m else {}
    tracks = ld_data.get('track', [])

    # 2. Parse artists from DOM
    artists_raw = re.findall(r'<div class="artist-wrap[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
    artist_list = []
    for a in artists_raw:
        names = re.findall(r'<span class="name-text[^"]*"[^>]*>([^<]+)</span>', a)
        artist_list.append(', '.join(names) if names else "NhacCuaTui Top Hits")

    # 3. Parse song names from DOM
    song_names = re.findall(r'<span class="hoverLightColor name text-hide[^"]*"[^>]*>([^<]+)</span>', html)

    # 4. Parse durations from DOM
    durations = re.findall(r'<div class="duration-wrap"[^>]*>([^<]+)</div>', html)

    results = []
    total = min(50, len(tracks))
    for i in range(total):
        rank = i + 1
        t = tracks[i]
        title = song_names[i] if i < len(song_names) else t.get('name', f'Top #{rank}')
        artist = artist_list[i] if i < len(artist_list) else "NhacCuaTui Top Hits"
        duration = durations[i] if i < len(durations) else ""
        url = t.get('url', f"https://www.nhaccuatui.com/chart/1-5-d{used_day}-{year}")

        img_url = f"https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/nct_chart_{min(rank, 6)}.png"

        results.append({
            "id": f"nct_rank_{rank}",
            "name": f"#{rank} {title}",
            "label": f"{artist}",
            "price": "Bảng Xếp Hạng",
            "promotional_image": {
                "links": [{"href": img_url}]
            },
            "icon": {
                "links": [{"href": img_url}]
            },
            "actions": [
                {
                    "type": "get",
                    "link": {"href": url},
                    "intent": {
                        "action": "android.intent.action.VIEW",
                        "data": url
                    }
                },
                {
                    "type": "open",
                    "link": {"href": url},
                    "intent": {
                        "action": "android.intent.action.VIEW",
                        "data": url
                    }
                },
                {
                    "type": "play",
                    "link": {"href": url},
                    "intent": {
                        "action": "android.intent.action.VIEW",
                        "data": url
                    }
                }
            ],
            "cards": [
                {
                    "type": "text",
                    "name": f"Top #{rank} Thịnh Hành",
                    "text": f"• Bài hát: {title}\n• Nghệ sĩ: {artist}\n• Thời lượng: {duration}\n• Bảng xếp hạng: NhacCuaTui Top 50 Thịnh Hành (Ngày {used_day}/{year})\n\nCập nhật lúc: {get_vietnam_time()}\nBấm OPEN hoặc PLAY để nghe trực tiếp bài hát."
                }
            ],
            "type": {
                "service": "market_vn",
                "id": "nct_music",
                "name": "Âm Nhạc"
            }
        })

    return results

def update_nct_music_feed(base_dir):
    music_path = os.path.join(base_dir, "list_nct_music.json")
    items = fetch_nct_chart()
    if not items:
        print("[-] Skipping NCT music update due to fetch failure")
        return

    data = {
        "id": "nct_music",
        "name": "Bảng Xếp Hạng NhacCuaTui Top Hits",
        "items": items
    }

    with open(music_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully updated {music_path} with {len(items)} tracks at {get_vietnam_time()}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"[*] Starting feed update in {base_dir}")
    
    # 1. Update gasoline prices
    update_gasoline_feed(base_dir)
    
    # 2. Update NCT music chart
    update_nct_music_feed(base_dir)
    
    # 3. Update news feed
    try:
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
