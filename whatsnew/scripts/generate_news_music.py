#!/usr/bin/env python3
"""Build and update VnExpress and NhacCuaTui feeds for Sony What's New.
Optimized for Sony FlixView 3D:
- Downloads and resizes images to standard Sony dimensions.
- Formatted as PNG (bypasses legacy libjpeguser JNI, 100% native Skia decode).
- Hosts images directly on GitHub raw repo.
- Fully compatible actions ('get', 'open', 'play') for one-click launch.
"""
import urllib.request
import xml.etree.ElementTree as ET
import re, json, os, io
from datetime import datetime, timezone, timedelta
from PIL import Image

def get_vietnam_time():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M - %d/%m/%Y")

def save_optimized_png(raw_bytes, out_path, size=(480, 270)):
    try:
        im = Image.open(io.BytesIO(raw_bytes))
        im = im.convert("RGB")
        im = im.resize(size, Image.Resampling.LANCZOS)
        im.save(out_path, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"[-] Image optimize error: {e}")
        return False

def fetch_vnexpress_news(images_dir):
    feeds = [
        ("https://vnexpress.net/rss/so-hoa.rss", "Công Nghệ"),
        ("https://vnexpress.net/rss/tin-moi-nhat.rss", "Thời Sự")
    ]
    items = []
    seen_links = set()
    idx = 1

    for url, category in feeds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for entry in root.findall('./channel/item')[:10]:
                title = entry.find('title').text
                link = entry.find('link').text
                if link in seen_links:
                    continue
                seen_links.add(link)
                desc = entry.find('description').text or ''
                img_m = re.search(r'src=["\']([^"\']+)["\']', desc)
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()

                img_filename = f"vne_news_{idx}.png"
                img_local_path = os.path.join(images_dir, img_filename)
                gh_img_url = f"https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{img_filename}"

                if img_m:
                    try:
                        img_req = urllib.request.Request(img_m.group(1), headers={'User-Agent': 'Mozilla/5.0'})
                        raw_img = urllib.request.urlopen(img_req, timeout=10).read()
                        save_optimized_png(raw_img, img_local_path, size=(480, 270))
                    except Exception as err:
                        print(f"[-] Failed downloading vne img {idx}: {err}")

                item_id = f"vne_{idx}"
                items.append({
                    "id": item_id,
                    "name": title,
                    "label": f"VnExpress • {category}",
                    "price": "Bản Tin Mới",
                    "promotional_image": {
                        "links": [{"href": gh_img_url}]
                    },
                    "icon": {
                        "links": [{"href": gh_img_url}]
                    },
                    "actions": [
                        {
                            "type": "get",
                            "link": {"href": link},
                            "intent": {
                                "action": "android.intent.action.VIEW",
                                "data": link
                            }
                        },
                        {
                            "type": "open",
                            "link": {"href": link},
                            "intent": {
                                "action": "android.intent.action.VIEW",
                                "data": link
                            }
                        }
                    ],
                    "cards": [
                        {
                            "type": "text",
                            "name": title,
                            "text": f"{clean_desc}\n\nNguồn: VnExpress ({category})\nCập nhật lúc: {get_vietnam_time()}\n\nBấm nút OPEN để mở bài viết gốc trên VnExpress."
                        }
                    ],
                    "type": {
                        "service": "market_vn",
                        "id": "vnexpress",
                        "name": "Tin Tức"
                    }
                })
                idx += 1
        except Exception as e:
            print(f"[-] Error fetching VnExpress {url}: {e}")

    return items[:20]

def fetch_nct_chart(images_dir):
    url = 'https://www.nhaccuatui.com/bai-hat/top-20.nhac-viet.html'
    items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

        tracks = []
        ld_match = re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        if ld_match:
            ld_data = json.loads(ld_match.group(1).strip())
            if ld_data.get("@type") == "MusicPlaylist":
                for t in ld_data.get("track", []):
                    tracks.append({
                        "title": t.get("name"),
                        "url": t.get("url")
                    })

        song_images = list(dict.fromkeys(re.findall(r'https://image-cdn\.nct\.vn/song/[^"]+?\.(?:jpg|png)', html)))

        for idx, t in enumerate(tracks[:6]):
            rank = idx + 1
            title = t.get("title", f"Bài hát #{rank}")
            song_url = t.get("url", "https://www.nhaccuatui.com")

            img_filename = f"nct_chart_{rank}.png"
            img_local_path = os.path.join(images_dir, img_filename)
            gh_img_url = f"https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{img_filename}"

            if idx < len(song_images):
                try:
                    img_req = urllib.request.Request(song_images[idx], headers={'User-Agent': 'Mozilla/5.0'})
                    raw_img = urllib.request.urlopen(img_req, timeout=10).read()
                    save_optimized_png(raw_img, img_local_path, size=(360, 360))
                except Exception as err:
                    print(f"[-] Failed downloading nct img {rank}: {err}")

            item_id = f"nct_rank_{rank}"
            items.append({
                "id": item_id,
                "name": f"#{rank} {title}",
                "label": "NhacCuaTui Top Hits",
                "price": "Bảng Xếp Hạng",
                "promotional_image": {
                    "links": [{"href": gh_img_url}]
                },
                "icon": {
                    "links": [{"href": gh_img_url}]
                },
                "actions": [
                    {
                        "type": "get",
                        "link": {"href": song_url},
                        "intent": {
                            "action": "android.intent.action.VIEW",
                            "data": song_url
                        }
                    },
                    {
                        "type": "open",
                        "link": {"href": song_url},
                        "intent": {
                            "action": "android.intent.action.VIEW",
                            "data": song_url
                        }
                    },
                    {
                        "type": "play",
                        "link": {"href": song_url},
                        "intent": {
                            "action": "android.intent.action.VIEW",
                            "data": song_url
                        }
                    }
                ],
                "cards": [
                    {
                        "type": "text",
                        "name": f"Top #{rank} Nhạc Thịnh Hành",
                        "text": f"Bài hát: {title}\nBảng xếp hạng: NhacCuaTui Top 20 Nhạc Việt\nCập nhật: {get_vietnam_time()}\n\nBấm nút OPEN ở góc trên để phát ngay bài hát trên trình phát."
                    }
                ],
                "type": {
                    "service": "market_vn",
                    "id": "nct_music",
                    "name": "Âm Nhạc"
                }
            })
    except Exception as e:
        print(f"[-] Error fetching NhacCuaTui: {e}")

    return items

def generate_feeds(base_dir):
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # 1. Update list_vnexpress.json
    vne_items = fetch_vnexpress_news(images_dir)
    if vne_items:
        vne_path = os.path.join(base_dir, "list_vnexpress.json")
        with open(vne_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": "vnexpress",
                "name": "Tin Nóng VnExpress (News Suite)",
                "items": vne_items
            }, f, ensure_ascii=False, indent=2)
        print(f"[+] Saved {len(vne_items)} items to {vne_path}")

    # 2. Update list_nct_music.json
    nct_items = fetch_nct_chart(images_dir)
    if nct_items:
        nct_path = os.path.join(base_dir, "list_nct_music.json")
        with open(nct_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": "nct_music",
                "name": "Bảng Xếp Hạng NhacCuaTui Top Hits",
                "items": nct_items
            }, f, ensure_ascii=False, indent=2)
        print(f"[+] Saved {len(nct_items)} items to {nct_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generate_feeds(base_dir)
