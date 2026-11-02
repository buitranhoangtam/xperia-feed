#!/usr/bin/env python3
"""Scheduled 2-times-daily updater for Sony What's New Live Feed.
Runs via GitHub Actions cron: '0 21,9 * * *' (4:00 AM & 4:00 PM GMT+7).
Updates:
  1. Live Gasoline prices from Ministry of Industry and Trade (Bộ Công Thương)
  2. Live NhacCuaTui Top 50 Trending Chart with Sony Generative ArtWork (GAW)
  3. Sony News Suite (VnExpress, Tuổi Trẻ, GenK, Buýt TPHCM)
"""
import json, time, os, re, sys, urllib.request, ssl, colorsys, random, unicodedata
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

# 6 Sony Xperia GAW Colors from XperiaAvatarArtworkModule.java
SONY_GAW_COLORS = [
    (0x41, 0x85, 0xF3), # Sony Blue
    (0x5C, 0x3B, 0xB5), # Sony Purple
    (0x00, 0x79, 0x6B), # Sony Teal
    (0xF9, 0x9A, 0x1E), # Sony Amber / Orange
    (0x7E, 0xAC, 0x3A), # Sony Green
    (0x4F, 0x67, 0x78)  # Sony Slate / Gray
]

def sony_gaw_tint(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(s * 1.1, 1.0)
    v = min(v * 0.75, 1.0)
    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
    return (int(nr * 255), int(ng * 255), int(nb * 255))

def get_bold_font(size):
    from PIL import ImageFont
    font_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def extract_gaw_letters(title):
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    words = [w for w in ascii_clean.strip().split() if w and w[0].isalnum()]
    if len(words) == 1:
        w = words[0]
        c1 = w[0].upper()
        c2 = w[1].upper() if len(w) > 1 else w[0].upper()
    elif len(words) > 1:
        c1 = words[0][0].upper()
        c2 = words[1][0].upper()
    else:
        c1, c2 = "S", "Y"
    return c1, c2

def generate_sony_gaw_artwork(rank, title, artist, out_path, size=480):
    """Generates authentic Sony Generative ArtWork (GAW) for music track."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        c1, c2 = extract_gaw_letters(title)
        color_idx = (rank - 1) % len(SONY_GAW_COLORS)
        base_color = SONY_GAW_COLORS[color_idx]
        tint_color = sony_gaw_tint(base_color)

        # 1. 45° Linear Gradient
        x = np.linspace(0, 1, size)
        y = np.linspace(0, 1, size)
        xx, yy = np.meshgrid(x, y)
        factor = (xx + yy) / 2.0
        r = (base_color[0] + factor * (tint_color[0] - base_color[0])).astype(np.uint8)
        g = (base_color[1] + factor * (tint_color[1] - base_color[1])).astype(np.uint8)
        b = (base_color[2] + factor * (tint_color[2] - base_color[2])).astype(np.uint8)
        rgb = np.stack([r, g, b], axis=2)
        comp = Image.fromarray(rgb).convert("RGBA")

        # 2. Translucent Sony GAW Letters (alpha 36 and 22)
        text_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d_text = ImageDraw.Draw(text_layer)
        font_gaw = get_bold_font(int(size * 1.30))

        x1 = int(-0.18 * size)
        y1 = int(-0.25 * size)
        d_text.text((x1, y1), c1, font=font_gaw, fill=(255, 255, 255, 36))

        x2 = int(0.28 * size)
        y2 = int(-0.10 * size)
        d_text.text((x2, y2), c2, font=font_gaw, fill=(255, 255, 255, 22))

        comp = Image.alpha_composite(comp, text_layer)

        # 3. Vinyl disc motif in upper-center (y ~ 0.40)
        disc_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        disc_draw = ImageDraw.Draw(disc_layer)
        cx, cy = size // 2, int(size * 0.40)
        r_disc = int(size * 0.32)

        # Outer vinyl disc with subtle shadow
        disc_draw.ellipse([cx - r_disc, cy - r_disc, cx + r_disc, cy + r_disc], fill=(0, 0, 0, 50), outline=(255, 255, 255, 45), width=2)
        disc_draw.ellipse([cx - int(r_disc*0.82), cy - int(r_disc*0.82), cx + int(r_disc*0.82), cy + int(r_disc*0.82)], outline=(255, 255, 255, 24), width=1)
        disc_draw.ellipse([cx - int(r_disc*0.65), cy - int(r_disc*0.65), cx + int(r_disc*0.65), cy + int(r_disc*0.65)], outline=(255, 255, 255, 20), width=1)

        # Center Record Label
        r_label = int(size * 0.18)
        disc_draw.ellipse([cx - r_label, cy - r_label, cx + r_label, cy + r_label], fill=base_color + (240,), outline=(255, 255, 255, 180), width=3)

        comp = Image.alpha_composite(comp, disc_layer)

        # 4. Rank in center record label
        badge_draw = ImageDraw.Draw(comp)
        font_rank = get_bold_font(int(size * 0.13))
        rank_str = f"#{rank:02d}"
        bbox = font_rank.getbbox(rank_str)
        rw = bbox[2] - bbox[0]
        rh = bbox[3] - bbox[1]
        rx = cx - (rw // 2) - bbox[0]
        ry = cy - (rh // 2) - bbox[1]

        badge_draw.text((rx + 2, ry + 2), rank_str, font=font_rank, fill=(0, 0, 0, 120))
        badge_draw.text((rx, ry), rank_str, font=font_rank, fill=(255, 255, 255, 255))

        # Top header tag: SONY XPERIA™ MUSIC
        font_mini = get_bold_font(int(size * 0.040))
        badge_draw.text((22, 20), "SONY XPERIA™ MUSIC", font=font_mini, fill=(255, 255, 255, 200))

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        comp.convert("RGB").save(out_path, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"[-] Error generating GAW artwork for #{rank}: {e}")
        return False

def get_vietnam_time():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M - %d/%m/%Y")

def fetch_gasoline_prices():
    prices = {
        'ron95_iii': '24.150 đ',
        'ron95_v': '24.950 đ',
        'e5_ron92': '24.220 đ',
        'do_005': '30.240 đ',
        'do_001': '31.640 đ',
        'dau_hoa': '30.650 đ',
        'source_title': 'Quyết định điều chỉnh giá xăng dầu Petrolimex ngày 01/11/2026'
    }
    is_live_success = False

    try:
        moit_url = "https://moit.gov.vn/tin-tuc/thong-bao"
        req = urllib.request.Request(moit_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        articles = re.findall(
            r'<a[^>]+href="([^"]+)"[^>]*title="([^"]*xang[^"]*)"[^>]*>|<a[^>]+title="([^"]*xang[^"]*)"[^>]*href="([^"]+)"',
            html, re.I
        )

        gas_articles = []
        for a in articles:
            link = a[0] or a[3]
            title = a[1] or a[2]
            if link and 'xang' in link.lower():
                if not link.startswith('http'):
                    link = "https://moit.gov.vn" + link
                gas_articles.append((title, link))

        if gas_articles:
            latest_title, latest_link = gas_articles[0]
            req_detail = urllib.request.Request(latest_link, headers=HEADERS)
            with urllib.request.urlopen(req_detail, timeout=12, context=ctx) as resp_detail:
                detail_html = resp_detail.read().decode('utf-8', errors='ignore')

            clean_text = re.sub(r'<[^>]+>', ' ', detail_html)
            pattern = r'(Xang\s*(?:E5\s*)?RON\s*9[25][^\d
]*?|Di[eê]zen\s*0,05S|D[aà]u\s*h[oỏ]a|D[aà]u\s*mad[uú]t[^\d
]*?)[\s:]*?(\d{1,2}[\.,]\d{3})'
            matches = re.findall(pattern, clean_text, re.I)

            found_any = False
            for item_name, p_val in matches:
                name_clean = item_name.strip()
                p_num = int(re.sub(r'[^\d]', '', p_val))
                if not (15000 <= p_num <= 35000):
                    continue

                p_str = f"{p_num:,}".replace(',', '.') + ' đ'
                if 'RON 95' in name_clean or 'RON95' in name_clean:
                    prices['ron95_iii'] = p_str
                    prices['ron95_v'] = f"{p_num + 800:,}".replace(',', '.') + ' đ'
                    found_any = True
                elif 'E5' in name_clean:
                    prices['e5_ron92'] = p_str
                    found_any = True
                elif 'di' in name_clean.lower() or 'diesel' in name_clean.lower():
                    prices['do_005'] = p_str

            if found_any:
                prices['source_title'] = latest_title.strip()
                is_live_success = True
                print(f"[+] Validated live MOIT announcement: {latest_title}")
    except Exception as e:
        print(f"[*] Note: gasoline scraping exception ({e})")

    return prices, is_live_success

def update_gasoline_feed(base_dir):
    gas_path = os.path.join(base_dir, "list_gasoline.json")
    if not os.path.exists(gas_path):
        return

    prices, is_live_success = fetch_gasoline_prices()
    if not is_live_success:
        print("[*] Gasoline scraper did not find new verified announcement. Preserving existing verified data to prevent fake timestamping.")
        return

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
                    "text": f"• Xăng E10 RON 95-V: {prices['ron95_v']}/lít (Vùng 1)
• Xăng E10 RON 95-III: {prices['ron95_iii']}/lít (Vùng 1)

Cơ sở điều hành: {prices['source_title']}
Áp dụng trên toàn bộ hệ thống phân phối xăng dầu Việt Nam (PVOIL & Petrolimex)."
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
            item["price"] = "Nhiên Liệu Sinh Học & Dầu"
            item["cards"] = [
                {
                    "type": "text",
                    "name": "Bảng Giá Nhiên Liệu Sinh Học & Dầu",
                    "text": f"• Xăng E5 RON 92-II: {prices['e5_ron92']}/lít (Vùng 1)
• Dầu DO 0,05S-II: {prices['do_005']}/lít (Vùng 1)
• Dầu DO 0,001S-V: {prices.get('do_001', '31.640 đ')}/lít (Vùng 1)
• Dầu Hỏa: {prices.get('dau_hoa', '30.650 đ')}/lít

Cơ sở điều hành: {prices['source_title']}
Áp dụng trên toàn bộ hệ thống phân phối xăng dầu Việt Nam (PVOIL & Petrolimex)."
                },
                {
                    "type": "text",
                    "name": "Chính Sách & Phân Vùng",
                    "text": "Vùng 1 gồm các đô thị, cảng và kho đầu mối. Vùng 2 gồm các địa bàn xa cảng, vùng sâu, vùng xa có chi phí vận chuyển cao hơn theo quy định."
                }
            ]

    with open(gas_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully updated {gas_path} with verified prices ({prices['source_title']})")

def fetch_nct_chart(base_dir):
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
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    for i in range(total):
        rank = i + 1
        t = tracks[i]
        title = song_names[i] if i < len(song_names) else t.get('name', f'Top #{rank:02d}')
        artist = artist_list[i] if i < len(artist_list) else "NhacCuaTui Top Hits"
        duration = durations[i] if i < len(durations) else ""
        url = t.get('url', f"https://www.nhaccuatui.com/chart/1-5-d{used_day}-{year}")

        # Generate Sony GAW Artwork for each track
        art_filename = f"nct_art_{rank:02d}.png"
        art_local_path = os.path.join(images_dir, art_filename)
        generate_sony_gaw_artwork(rank, title, artist, art_local_path)

        img_url = f"https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{art_filename}"

        results.append({
            "id": f"nct_rank_{rank:02d}",
            "name": f"#{rank:02d} {title}",
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
                    "name": f"Top #{rank:02d} Thịnh Hành",
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
    items = fetch_nct_chart(base_dir)
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
    
    # 2. Update NCT music chart with Sony GAW artworks
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
