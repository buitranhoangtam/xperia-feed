import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMG_DIR = r"D:\ANTIGRAVITY\xperia-releases-tmp\whatsnew\images"
os.makedirs(IMG_DIR, exist_ok=True)

def draw_petrolimex_banner():
    # 1080x608 banner for petrolimex
    w, h = 1080, 608
    im = Image.new("RGBA", (w, h), (18, 24, 38, 255))
    d = ImageDraw.Draw(im)
    
    # Background gradient
    for y in range(h):
        r = int(10 + (y / h) * 20)
        g = int(35 + (y / h) * 45)
        b = int(75 + (y / h) * 65)
        d.line([(0, y), (w, y)], fill=(r, g, b))
        
    # Petrolimex Station Canopy & Architecture
    # Canopy roof
    d.polygon([(0, 180), (w, 150), (w, 240), (0, 260)], fill=(0, 68, 148, 255))
    # Orange stripe on canopy
    d.polygon([(0, 240), (w, 220), (w, 250), (0, 265)], fill=(243, 112, 33, 255))
    
    # Canopy pillars
    d.rectangle([220, 250, 260, 520], fill=(70, 80, 95, 255))
    d.rectangle([820, 235, 860, 520], fill=(70, 80, 95, 255))
    
    # Fuel Dispensers (Pumps)
    # Pump 1 (Left)
    d.rectangle([340, 310, 480, 520], fill=(240, 243, 248, 255), outline=(0, 68, 148, 255), width=4)
    d.rectangle([350, 320, 470, 380], fill=(0, 68, 148, 255)) # blue header
    d.rectangle([360, 390, 460, 440], fill=(20, 25, 30, 255)) # digital price display
    d.rectangle([370, 455, 410, 510], fill=(0, 160, 75, 255)) # E5 Green nozzle
    d.rectangle([420, 455, 450, 510], fill=(230, 40, 40, 255)) # RON 95 Red nozzle
    
    # Pump 2 (Right)
    d.rectangle([600, 310, 740, 520], fill=(240, 243, 248, 255), outline=(0, 68, 148, 255), width=4)
    d.rectangle([610, 320, 730, 380], fill=(0, 68, 148, 255))
    d.rectangle([620, 390, 720, 440], fill=(20, 25, 30, 255))
    d.rectangle([630, 455, 670, 510], fill=(230, 40, 40, 255))
    d.rectangle([680, 455, 710, 510], fill=(240, 180, 20, 255)) # Diesel nozzle
    
    # Station Ground
    d.polygon([(0, 500), (w, 480), (w, h), (0, h)], fill=(45, 50, 60, 255))
    # Lane markings
    d.polygon([(490, 510), (590, 510), (620, h), (460, h)], fill=(240, 240, 240, 180))
    
    # Floating Price HUD Card on Top Left
    hud_x, hud_y = 60, 40
    d.rounded_rectangle([hud_x, hud_y, hud_x + 520, hud_y + 110], radius=16, fill=(0, 0, 0, 190), outline=(243, 112, 33, 255), width=2)
    
    # Petrolimex Brand badge
    d.ellipse([hud_x + 20, hud_y + 20, hud_x + 80, hud_y + 80], fill=(0, 68, 148, 255), outline=(255, 255, 255, 255), width=2)
    d.ellipse([hud_x + 55, hud_y + 25, hud_x + 75, hud_y + 45], fill=(243, 112, 33, 255))
    
    # Text badge
    try:
        f_bold = ImageFont.truetype("arialbd.ttf", 26)
        f_price = ImageFont.truetype("arialbd.ttf", 20)
        f_sub = ImageFont.truetype("arial.ttf", 16)
    except:
        f_bold = ImageFont.load_default()
        f_price = f_bold
        f_sub = f_bold
        
    d.text((hud_x + 100, hud_y + 20), "GIÁ XĂNG DẦU HÔM NAY", font=f_bold, fill=(255, 255, 255, 255))
    d.text((hud_x + 100, hud_y + 55), "RON 95-V: 27.520 đ  |  E5 RON 92: 26.670 đ", font=f_price, fill=(243, 112, 33, 255))
    d.text((hud_x + 100, hud_y + 82), "Petrolimex Live Feed • Cập nhật tự động 30 phút", font=f_sub, fill=(180, 200, 220, 255))
    
    im.save(os.path.join(IMG_DIR, "petrolimex_banner.png"))
    print("[+] Saved petrolimex_banner.png")

def draw_realistic_phone(filename, model_name, subtitle, bg_color, phone_color, cam_style="triple"):
    w, h = 1080, 608
    im = Image.new("RGBA", (w, h), bg_color)
    d = ImageDraw.Draw(im)
    
    # Studio lighting radial glow
    for r in range(350, 0, -10):
        alpha = int((350 - r) / 350 * 50)
        d.ellipse([650 - r, 304 - r, 650 + r, 304 + r], fill=(255, 255, 255, alpha))
        
    # Phone Body (Xperia tall 21:9 format)
    # Centered at x=680, y=304, width=220, height=480
    px, py, pw, ph = 580, 64, 220, 480
    
    # Shadow
    d.rounded_rectangle([px + 12, py + 16, px + pw + 12, py + ph + 16], radius=24, fill=(0, 0, 0, 70))
    # Phone Frame
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=24, fill=phone_color, outline=(220, 225, 235, 200), width=3)
    # Screen Glass
    sx, sy, sw, sh = px + 10, py + 12, pw - 20, ph - 24
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=16, fill=(10, 14, 22, 255))
    
    # Screen Wallpaper art (Sony Flow)
    d.ellipse([sx - 20, sy + 50, sx + sw + 50, sy + 250], fill=(40, 80, 160, 180))
    d.ellipse([sx + 30, sy + 150, sx + sw + 80, sy + 380], fill=(160, 40, 100, 160))
    d.ellipse([sx + 10, sy + 260, sx + sw - 10, sy + 430], fill=(240, 140, 40, 160))
    
    # Camera Island on back reflection (perspective angle phone next to it)
    bx, by, bw, bh = px + 140, py + 30, 180, 440
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=22, fill=(phone_color[0]-15, phone_color[1]-15, phone_color[2]-15, 240), outline=(255, 255, 255, 80), width=2)
    # Camera strip
    cx, cy, cw, ch = bx + 24, by + 30, 40, 150
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=20, fill=(20, 22, 25, 255), outline=(100, 105, 115, 255), width=2)
    # 3 Lenses
    for i in range(3):
        ly = cy + 18 + i * 42
        d.ellipse([cx + 6, ly, cx + 34, ly + 28], fill=(5, 5, 10, 255), outline=(60, 130, 220, 200), width=2)
        d.ellipse([cx + 12, ly + 6, cx + 28, ly + 22], fill=(15, 20, 40, 255))
        d.ellipse([cx + 14, ly + 8, cx + 20, ly + 14], fill=(255, 255, 255, 180)) # lens glare
    # ZEISS T* Red Logo
    d.ellipse([cx + 16, cy + 130, cx + 24, cy + 138], fill=(220, 30, 30, 255))
    
    # Left typography banner
    try:
        f_sony = ImageFont.truetype("arialbd.ttf", 22)
        f_title = ImageFont.truetype("arialbd.ttf", 52)
        f_sub = ImageFont.truetype("arial.ttf", 24)
        f_badge = ImageFont.truetype("arialbd.ttf", 18)
    except:
        f_sony = ImageFont.load_default()
        f_title = f_sony
        f_sub = f_sony
        f_badge = f_sony
        
    d.text((80, 130), "SONY XPERIA", font=f_sony, fill=(160, 175, 195, 255))
    d.text((80, 170), model_name, font=f_title, fill=(255, 255, 255, 255))
    d.text((80, 245), subtitle, font=f_sub, fill=(200, 215, 235, 255))
    
    # Specs Pill Badge
    d.rounded_rectangle([80, 310, 320, 355], radius=12, fill=(40, 50, 70, 220), outline=(80, 110, 160, 255), width=1)
    d.text((95, 322), "Snapdragon 8 Gen 3 / Elite", font=f_badge, fill=(255, 255, 255, 255))
    
    d.rounded_rectangle([80, 370, 290, 415], radius=12, fill=(40, 50, 70, 220), outline=(80, 110, 160, 255), width=1)
    d.text((95, 382), "ZEISS T* Triple Camera", font=f_badge, fill=(255, 180, 50, 255))
    
    im.save(os.path.join(IMG_DIR, filename))
    print(f"[+] Saved {filename}")

def draw_realistic_headphones(filename, model_name, subtitle):
    w, h = 1080, 608
    im = Image.new("RGBA", (w, h), (22, 24, 28, 255))
    d = ImageDraw.Draw(im)
    
    # Background subtle radial spotlight
    for r in range(350, 0, -10):
        alpha = int((350 - r) / 350 * 45)
        d.ellipse([700 - r, 304 - r, 700 + r, 304 + r], fill=(255, 255, 255, alpha))
        
    # Headband
    hx, hy = 700, 300
    d.arc([hx - 150, hy - 180, hx + 150, hy + 120], start=190, end=350, fill=(45, 48, 54, 255), width=32)
    # Headband soft cushion
    d.arc([hx - 145, hy - 175, hx + 145, hy + 115], start=205, end=335, fill=(30, 32, 36, 255), width=24)
    
    # Left Ear Cup
    d.ellipse([hx - 190, hy - 20, hx - 90, hy + 140], fill=(36, 38, 44, 255), outline=(60, 64, 72, 255), width=3)
    d.ellipse([hx - 180, hy - 10, hx - 100, hy + 130], fill=(24, 26, 30, 255))
    # Right Ear Cup
    d.ellipse([hx + 90, hy - 20, hx + 190, hy + 140], fill=(36, 38, 44, 255), outline=(60, 64, 72, 255), width=3)
    d.ellipse([hx + 100, hy - 10, hx + 180, hy + 130], fill=(24, 26, 30, 255))
    
    # Gold Sony Logo on cup hinge
    d.text((hx - 155, hy - 45), "SONY", fill=(212, 175, 55, 255))
    d.text((hx + 125, hy - 45), "SONY", fill=(212, 175, 55, 255))
    
    # Typography
    try:
        f_sony = ImageFont.truetype("arialbd.ttf", 22)
        f_title = ImageFont.truetype("arialbd.ttf", 50)
        f_sub = ImageFont.truetype("arial.ttf", 24)
        f_badge = ImageFont.truetype("arialbd.ttf", 18)
    except:
        f_sony = ImageFont.load_default()
        f_title = f_sony
        f_sub = f_sony
        f_badge = f_sony
        
    d.text((80, 130), "SONY AUDIO HI-RES", font=f_sony, fill=(212, 175, 55, 255))
    d.text((80, 170), model_name, font=f_title, fill=(255, 255, 255, 255))
    d.text((80, 245), subtitle, font=f_sub, fill=(200, 215, 235, 255))
    
    # Badges
    d.rounded_rectangle([80, 310, 310, 355], radius=12, fill=(40, 44, 52, 220), outline=(212, 175, 55, 200), width=1)
    d.text((95, 322), "Industry Leading Noise Canceling", font=f_badge, fill=(255, 255, 255, 255))
    
    d.rounded_rectangle([80, 370, 270, 415], radius=12, fill=(40, 44, 52, 220), outline=(80, 120, 200, 200), width=1)
    d.text((95, 382), "LDAC • 360 Reality Audio", font=f_badge, fill=(100, 180, 255, 255))
    
    im.save(os.path.join(IMG_DIR, filename))
    print(f"[+] Saved {filename}")

if __name__ == "__main__":
    draw_petrolimex_banner()
    draw_realistic_phone("xperia_1_vii.png", "Xperia 1 VII", "Đỉnh cao nhiếp ảnh & màn hình 4K HDR", (20, 24, 32, 255), (38, 42, 50, 255))
    draw_realistic_phone("xperia_10_vi.png", "Xperia 10 VI", "Pin siêu bền 2 ngày & thiết kế siêu nhẹ", (25, 35, 45, 255), (75, 115, 140, 255))
    draw_realistic_phone("xperia_pro_i.png", "Xperia PRO-I", "Cảm biến 1.0-inch Exmor RS chuyên nghiệp", (24, 20, 22, 255), (45, 38, 40, 255))
    draw_realistic_phone("xperia_5_v.png", "Xperia 5 V", "Flagship nhỏ gọn thế hệ mới", (30, 26, 36, 255), (90, 50, 75, 255))
    draw_realistic_headphones("sony_wh1000xm5.png", "WH-1000XM5", "Chống ồn đỉnh cao với chip kép QN1 & V1")
    draw_realistic_headphones("sony_wf1000xm5.png", "WF-1000XM5", "Tai nghe True Wireless Hi-Res chuẩn phòng thu")
