import json
from pathlib import Path

BASE = Path('D:/ANTIGRAVITY/xperia-releases-tmp/whatsnew')

# Update list_smartphones.json
with open(BASE / 'list_smartphones.json', 'r', encoding='utf-8') as f:
    phones = json.load(f)

for item in phones['items']:
    iid = item['id']
    # Change image to realistic png
    item['promotional_image'] = {
        'links': [
            {
                'href': f'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{iid}.png',
                'size': {'less_than': 1080}
            }
        ]
    }
    # Update action to play with intent
    item['actions'] = [
        {
            'type': 'play',
            'intent': {
                'action': 'android.intent.action.VIEW',
                'data': 'https://www.sony.com.vn/smartphones'
            }
        }
    ]
    # Add detailed cards
    if iid == 'xperia_1_vii':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Thông Số Kỹ Thuật Flagship',
                'text': '• Chip xử lý: Qualcomm Snapdragon 8 Elite / Gen 3\n• Màn hình: 6.5 inch 4K HDR OLED 120Hz Bravia\n• Cụm Camera: Ống kính quang học ZEISS T* zoom quang liên tục 85-170mm\n• Âm thanh: Loa stereo kép mặt trước, hỗ trợ Hi-Res Audio'
            },
            {
                'type': 'text',
                'name': 'Trải Nghiệm Đẳng Cấp Sony',
                'text': 'Kế thừa công nghệ lấy nét theo ánh mắt từ dòng máy ảnh Alpha chuyên nghiệp, hỗ trợ quay video 4K HDR 120fps trên mọi ống kính.'
            }
        ]
    elif iid == 'xperia_10_vi':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Thông Số Xperia 10 VI',
                'text': '• Thiết kế: Siêu nhẹ 164g, chống nước chuẩn IP65/68\n• Pin: Dung lượng 5000mAh thời lượng 2 ngày\n• Màn hình: 6.1 inch OLED tỷ lệ 21:9 chuẩn điện ảnh\n• Camera: 48MP OIS với công nghệ zoom cảm biến quang 2X'
            },
            {
                'type': 'text',
                'name': 'Âm Thanh và Độ Bền',
                'text': 'Hỗ trợ jack 3.5mm và âm thanh Hi-Res Audio Wireless, kính cường lực Corning Gorilla Glass Victus.'
            }
        ]
    elif iid == 'xperia_pro_i':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Nhiếp Ảnh Chuyên Nghiệp',
                'text': '• Cảm biến: 1.0-inch Exmor RS mang từ máy ảnh RX100 VII\n• Khẩu độ kép: F2.0 / F4.0 linh hoạt kiểm soát độ sâu trường ảnh\n• Lớp phủ quang học ZEISS Tessar T*'
            }
        ]
    elif iid == 'xperia_5_v':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Flagship Nhỏ Gọn Thế Hệ Mới',
                'text': '• Cảm biến Exmor T cho di động thế hệ mới\n• Pin 5000mAh tối ưu thời lượng vượt trội\n• Màn hình OLED 120Hz siêu sáng'
            }
        ]

with open(BASE / 'list_smartphones.json', 'w', encoding='utf-8') as f:
    json.dump(phones, f, ensure_ascii=False, indent=2)

# Update list_audio.json
with open(BASE / 'list_audio.json', 'r', encoding='utf-8') as f:
    audio = json.load(f)

for item in audio['items']:
    iid = item['id']
    if iid == 'sony_wh1000xm5':
        fname = 'sony_wh1000xm5.png'
        cards = [
            {
                'type': 'text',
                'name': 'Đặc Điểm Nổi Bật',
                'text': '• Công nghệ chống ồn đỉnh cao Auto NC Optimizer\n• Bộ xử lý kép: Chip QN1 và chip V1 tích hợp\n• Thời lượng pin: 30 giờ (bật NC), sạc nhanh 3 phút nghe 3 giờ\n• Codec cao cấp: LDAC, DSEE Extreme, 360 Reality Audio'
            }
        ]
    else:
        fname = 'sony_wf1000xm5.png'
        cards = [
            {
                'type': 'text',
                'name': 'Âm Thanh Chuẩn Phòng Thu',
                'text': '• Củ loa Dynamic Driver X tái tạo âm bass sâu và dải cao tách bạch\n• Chip V2 và chip chống ồn QN2e\n• Micro chống ồn cảm biến dẫn truyền xương'
            }
        ]
    item['promotional_image'] = {
        'links': [
            {
                'href': f'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/{fname}',
                'size': {'less_than': 1080}
            }
        ]
    }
    item['actions'] = [
        {
            'type': 'play',
            'intent': {
                'action': 'android.intent.action.VIEW',
                'data': 'https://www.sony.com.vn/headphones'
            }
        }
    ]
    item['cards'] = cards

with open(BASE / 'list_audio.json', 'w', encoding='utf-8') as f:
    json.dump(audio, f, ensure_ascii=False, indent=2)

print('[+] Successfully updated list_smartphones.json and list_audio.json!')
