import urllib.request
import xml.etree.ElementTree as ET
import re, json, os, io, html, sys
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_FEED_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_FEED_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_vietnam_time():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M - %d/%m/%Y")

def save_optimized_png(raw_bytes, out_path, size=(480, 270)):
    try:
        im = Image.open(io.BytesIO(raw_bytes))
        im = im.convert("RGB")
        im = im.resize(size, Image.Resampling.LANCZOS)
        # Quantize to 256 colors (PNG-8) for ~50KB size and lightning-fast loading
        im_quant = im.quantize(colors=256, method=Image.Resampling.LANCZOS)
        im_quant.save(out_path, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"[-] Image optimize error: {e}")
        return False

def create_bus_banner(title, out_path, size=(480, 270)):
    """Create a beautiful transport banner for Buyt TPHCM if no photo is available."""
    im = Image.new("RGB", size, color=(16, 88, 160)) # Nice bus blue
    draw = ImageDraw.Draw(im)
    # Draw header bar
    draw.rectangle([0, 0, size[0], 48], fill=(10, 60, 120))
    # Draw decorative accents
    draw.rectangle([0, size[1]-12, size[0], size[1]], fill=(255, 152, 0))
    # Save quantized
    im_quant = im.quantize(colors=128)
    im_quant.save(out_path, "PNG", optimize=True)
    return True

def download_and_save_image(img_url, out_path):
    try:
        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        return save_optimized_png(data, out_path)
    except Exception as e:
        print(f"[-] Failed downloading {img_url}: {e}")
        return False

def fetch_rss_feed(feed_url, source_name, default_category, max_count=12):
    items = []
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_xml = resp.read()
        root = ET.fromstring(raw_xml)
        for item in root.findall('./channel/item'):
            title = item.find('title').text or ''
            link = item.find('link').text or ''
            desc = item.find('description').text or ''
            
            # Extract image
            img_url = None
            img_m = re.search(r'src=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']', desc, re.I)
            if img_m:
                img_url = img_m.group(1)
            else:
                enc = item.find('enclosure')
                if enc is not None and 'url' in enc.attrib:
                    img_url = enc.attrib['url']

            clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
            clean_title = html.unescape(title).strip()
            
            if clean_title and link:
                items.append({
                    "title": clean_title,
                    "link": link.strip(),
                    "desc": clean_desc,
                    "img_url": img_url,
                    "source": source_name,
                    "category": default_category
                })
            if len(items) >= max_count:
                break
    except Exception as e:
        print(f"[-] Error fetching {source_name} ({feed_url}): {e}")
    return items

def fetch_buyttphcm():
    items = []
    try:
        req = urllib.request.Request("http://buyttphcm.com.vn/Home/TinTuc", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_html = resp.read().decode('utf-8', errors='ignore')

        matches = re.findall(r'href=["\'](?:https?://buyttphcm\.com\.vn)?(/Home/ArtMID/\d+/ArticleID/\d+/[^"\']+)["\'][^>]*>(.*?)</a>', raw_html, re.DOTALL)
        seen = set()
        for link, title_raw in matches:
            clean_title = re.sub(r'<[^>]+>', '', title_raw).strip()
            clean_title = clean_title.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&amp;', '&').replace('&ocirc;', 'ô').replace('&ecirc;', 'ê')
            full_link = "https://buyttphcm.com.vn" + link
            if full_link in seen or len(clean_title) < 18:
                continue
            seen.add(full_link)
            items.append({
                "title": clean_title,
                "link": full_link,
                "desc": f"Thông báo hoạt động và điều chỉnh giao thông xe buýt TP.HCM: {clean_title}",
                "img_url": None,
                "source": "Buýt TPHCM",
                "category": "Giao Thông Đô Thị"
            })
            if len(items) >= 8:
                break
    except Exception as e:
        print(f"[-] Error fetching Buýt TPHCM: {e}")
    return items

def build_interleaved_list():
    print("--- 1. Fetching all news sources ---")
    vne_tech = fetch_rss_feed("https://vnexpress.net/rss/so-hoa.rss", "VnExpress", "Công Nghệ", max_count=8)
    vne_news = fetch_rss_feed("https://vnexpress.net/rss/tin-moi-nhat.rss", "VnExpress", "Thời Sự", max_count=8)
    
    tt_news = fetch_rss_feed("https://tuoitre.vn/rss/tin-moi-nhat.rss", "Tuổi Trẻ", "Thời Sự", max_count=10)
    tt_tech = fetch_rss_feed("https://tuoitre.vn/rss/nhip-song-so.rss", "Tuổi Trẻ", "Nhịp Sống Số", max_count=6)
    
    genk_tech = fetch_rss_feed("https://genk.vn/rss/home.rss", "GenK", "Công Nghệ & AI", max_count=12)
    
    bus_news = fetch_buyttphcm()

    print(f"  VnExpress: {len(vne_tech) + len(vne_news)}")
    print(f"  Tuổi Trẻ: {len(tt_news) + len(tt_tech)}")
    print(f"  GenK: {len(genk_tech)}")
    print(f"  Buýt TPHCM: {len(bus_news)}")

    # Interleave to create top 6 for landing page:
    # 1. Tuổi Trẻ Thời Sự
    # 2. GenK Công Nghệ
    # 3. VnExpress Thời Sự
    # 4. Buýt TPHCM
    # 5. VnExpress Công Nghệ
    # 6. Tuổi Trẻ Nhịp Sống Số
    ordered = []
    
    pools = [tt_news, genk_tech, vne_news, bus_news, vne_tech, tt_tech]
    
    # Pick round-robin until 48 items
    seen_links = set()
    max_total = 48
    round_idx = 0
    while len(ordered) < max_total and any(pools):
        added_in_round = False
        for p in pools:
            if p:
                item = p.pop(0)
                if item['link'] not in seen_links:
                    seen_links.add(item['link'])
                    ordered.append(item)
                    added_in_round = True
                    if len(ordered) >= max_total:
                        break
        if not added_in_round:
            break
            
    print(f"--- 2. Total interleaved items: {len(ordered)} ---")
    return ordered

def process_and_save(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    items_raw = build_interleaved_list()
    final_items = []

    print("--- 3. Processing images with PNG-8 Quantization & jsDelivr CDN ---")
    for idx, item in enumerate(items_raw):
        item_num = idx + 1
        img_filename = f"news_{item_num}.png"
        img_local_path = os.path.join(images_dir, img_filename)
        
        # Download and optimize
        success = False
        if item['img_url']:
            success = download_and_save_image(item['img_url'], img_local_path)
        
        if not success:
            # Fallback bus or default graphic
            create_bus_banner(item['title'], img_local_path)

        # Primary CDN: jsDelivr (Edge-cached worldwide with VN & SG PoPs)
        cdn_url = f"https://cdn.jsdelivr.net/gh/buitranhoangtam/xperia-feed@main/whatsnew/images/{img_filename}"
        raw_url = f"https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{img_filename}"

        link = item['link']
        title = item['title']
        source = item['source']
        category = item['category']
        clean_desc = item['desc']

        item_id = f"news_item_{item_num}"
        final_items.append({
            "id": item_id,
            "name": title,
            "label": f"{source} • {category}",
            "price": "Bản Tin Mới",
            "promotional_image": {
                "links": [
                    {"href": cdn_url},
                    {"href": raw_url}
                ]
            },
            "icon": {
                "links": [
                    {"href": cdn_url},
                    {"href": raw_url}
                ]
            },
            "actions": [
                {
                    "type": "get",
                    "link": {"href": f"entrance://webview/{link}"},
                    "intent": {
                        "action": "android.intent.action.VIEW",
                        "target-class": "com.sonymobile.entrance.news.XperiaNewsReaderActivity",
                        "data": f"entrance://webview/{link}"
                    }
                },
                {
                    "type": "open",
                    "link": {"href": f"entrance://webview/{link}"},
                    "intent": {
                        "action": "android.intent.action.VIEW",
                        "target-class": "com.sonymobile.entrance.news.XperiaNewsReaderActivity",
                        "data": f"entrance://webview/{link}"
                    }
                }
            ],
            "cards": [
                {
                    "type": "text",
                    "name": title,
                    "text": f"{clean_desc}\n\nNguồn: {source} ({category})\nCập nhật lúc: {get_vietnam_time()}\n\nBấm nút OPEN để đọc trực tiếp bài viết trên trình đọc Sony News Suite."
                }
            ],
            "type": {
                "service": "market_vn",
                "id": "vnexpress",
                "name": "Tin Tức"
            }
        })
        if item_num % 10 == 0 or item_num == len(items_raw):
            print(f"  Processed {item_num}/{len(items_raw)} items...")

    # Write list_vnexpress.json
    out_list_path = os.path.join(base_dir, "list_vnexpress.json")
    with open(out_list_path, "w", encoding="utf-8") as f:
        json.dump({
            "id": "vnexpress",
            "name": "Sony News Suite",
            "items": final_items
        }, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {len(final_items)} items to {out_list_path}")

    # Also update aggregator_v3.json to rename group to "Sony News Suite"
    agg_path = os.path.join(base_dir, "aggregator_v3.json")
    with open(agg_path, "r", encoding="utf-8") as f:
        agg = json.load(f)

    for c in agg.get("cards", []):
        if c.get("id") == "card_vnexpress_news":
            c["name"] = "Sony News Suite"
            print("[+] Updated card_vnexpress_news name to 'Sony News Suite' in aggregator_v3.json")

    with open(agg_path, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)

    # Copy list_vnexpress.json to aggregator_v2 if present
    print("--- 4. Build completed successfully! ---")

def generate_feeds(base_dir):
    process_and_save(base_dir)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generate_feeds(base_dir)
