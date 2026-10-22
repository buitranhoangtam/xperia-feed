import json
from pathlib import Path

BASE = Path('D:/ANTIGRAVITY/xperia-releases-tmp/whatsnew')

# 1. Update list_gasoline.json: Remove the technical "Cơ chế cập nhật tự động" card
with open(BASE / 'list_gasoline.json', 'r', encoding='utf-8') as f:
    gas = json.load(f)

for item in gas.get('items', []):
    if item['id'] == 'gasoline_ron95':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Bảng Giá Xăng Cao Cấp Petrolimex',
                'text': '• Xăng E10 RON 95-V: 27.520 đ/lít (Vùng 1) | 28.070 đ/lít (Vùng 2)\n• Xăng E10 RON 95-III: 26.720 đ/lít (Vùng 1) | 27.250 đ/lít (Vùng 2)\n\nÁp dụng trên toàn quốc theo kỳ điều hành mới nhất của Liên Bộ Công Thương - Tài chính.'
            }
        ]
    elif item['id'] == 'gasoline_e5_do':
        item['cards'] = [
            {
                'type': 'text',
                'name': 'Bảng Giá Nhiên Liệu Sinh Học & Dầu',
                'text': '• Xăng E5 RON 92-II: 26.670 đ/lít (Vùng 1) | 27.200 đ/lít (Vùng 2)\n• Dầu DO 0,05S-II: 28.800 đ/lít (Vùng 1) | 29.370 đ/lít (Vùng 2)\n• Dầu DO 0,001S-V: 30.200 đ/lít (Vùng 1) | 30.800 đ/lít (Vùng 2)\n• Dầu Hỏa: 30.410 đ/lít\n\nÁp dụng tại toàn bộ hệ thống phân phối Petrolimex Việt Nam.'
            }
        ]

with open(BASE / 'list_gasoline.json', 'w', encoding='utf-8') as f:
    json.dump(gas, f, ensure_ascii=False, indent=2)

# 2. Update list_smartphones.json: Modern Xperia 1 VIII lineup
phones = {
    'id': 'smartphones',
    'name': 'Điện thoại thông minh Xperia',
    'items': [
        {
            'id': 'xperia_1_viii',
            'name': 'Xperia 1 VIII',
            'label': 'Flagship Mới Nhất',
            'price': 'Snapdragon 8 Elite',
            'promotional_image': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_1_viii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'icon': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_1_viii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'actions': [
                {
                    'type': 'get',
                    'link': {'href': 'https://www.sony.com.vn/smartphones'},
                    'intent': {
                        'action': 'android.intent.action.VIEW',
                        'data': 'https://www.sony.com.vn/smartphones'
                    }
                },
                {
                    'type': 'open',
                    'link': {'href': 'https://www.sony.com.vn/smartphones'},
                    'intent': {
                        'action': 'android.intent.action.VIEW',
                        'data': 'https://www.sony.com.vn/smartphones'
                    }
                }
            ],
            'cards': [
                {
                    'type': 'text',
                    'name': 'Đỉnh Cao Nhiếp Ảnh Sony Alpha',
                    'text': '• Chip xử lý: Snapdragon 8 Elite NPU thế hệ mới\n• Màn hình: 6.5 inch 4K HDR OLED 120Hz Bravia tỷ lệ điện ảnh\n• Camera: Ống kính quang học ZEISS T* zoom quang liên tục\n• Cảm biến: Exmor T 2 lớp bóng bán dẫn thu sáng gấp đôi'
                }
            ],
            'type': {
                'service': 'sony_vn',
                'id': 'smartphones',
                'name': 'Điện thoại thông minh'
            }
        },
        {
            'id': 'xperia_10_vii',
            'name': 'Xperia 10 VII',
            'label': 'Pin 2 Ngày Bền Bỉ',
            'price': 'Siêu nhẹ 164g',
            'promotional_image': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_10_vii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'icon': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_10_vii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'actions': [
                {
                    'type': 'get',
                    'link': {'href': 'https://www.sony.com.vn/smartphones'},
                    'intent': {
                        'action': 'android.intent.action.VIEW',
                        'data': 'https://www.sony.com.vn/smartphones'
                    }
                }
            ],
            'cards': [
                {
                    'type': 'text',
                    'name': 'Thông Số Xperia 10 VII',
                    'text': '• Pin: Dung lượng lớn 5000mAh thời lượng 2 ngày\n• Màn hình: OLED sắc nét bảo vệ mắt\n• Kháng nước bụi: Tiêu chuẩn IP65/IP68 đỉnh cao\n• Âm thanh: Jack tai nghe 3.5mm và Hi-Res Audio'
                }
            ],
            'type': {
                'service': 'sony_vn',
                'id': 'smartphones',
                'name': 'Điện thoại thông minh'
            }
        },
        {
            'id': 'xperia_pro_ii',
            'name': 'Xperia PRO-II',
            'label': 'Cảm Biến 1.0-inch',
            'price': 'Nhiếp Ảnh Chuyên Nghiệp',
            'promotional_image': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_pro_ii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'icon': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_pro_ii.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'actions': [
                {
                    'type': 'get',
                    'link': {'href': 'https://www.sony.com.vn/smartphones'},
                    'intent': {
                        'action': 'android.intent.action.VIEW',
                        'data': 'https://www.sony.com.vn/smartphones'
                    }
                }
            ],
            'cards': [
                {
                    'type': 'text',
                    'name': 'Ống Kính Máy Ảnh Chuyên Nghiệp',
                    'text': '• Cảm biến 1.0-inch Exmor RS với khẩu độ kép F2.0/F4.0\n• Bộ xử lý hình ảnh BIONZ X for mobile chuyên dụng\n• Quay video 4K HDR 120 khung hình/giây'
                }
            ],
            'type': {
                'service': 'sony_vn',
                'id': 'smartphones',
                'name': 'Điện thoại thông minh'
            }
        },
        {
            'id': 'xperia_5_vi',
            'name': 'Xperia 5 VI',
            'label': 'Flagship Nhỏ Gọn',
            'price': 'Hiệu Năng Toàn Diện',
            'promotional_image': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_5_vi.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'icon': {
                'links': [
                    {
                        'href': 'https://raw.githubusercontent.com/buitranhoangtam/xperia-feed/main/whatsnew/images/xperia_5_vi.png',
                        'size': {'less_than': 1080}
                    }
                ]
            },
            'actions': [
                {
                    'type': 'get',
                    'link': {'href': 'https://www.sony.com.vn/smartphones'},
                    'intent': {
                        'action': 'android.intent.action.VIEW',
                        'data': 'https://www.sony.com.vn/smartphones'
                    }
                }
            ],
            'cards': [
                {
                    'type': 'text',
                    'name': 'Sức Mạnh Trong Lòng Bàn Tay',
                    'text': '• Thiết kế công thái học vừa vặn bàn tay\n• Cảm biến Exmor T cao cấp\n• Loa âm thanh nổi mặt trước sống động'
                }
            ],
            'type': {
                'service': 'sony_vn',
                'id': 'smartphones',
                'name': 'Điện thoại thông minh'
            }
        }
    ]
}

with open(BASE / 'list_smartphones.json', 'w', encoding='utf-8') as f:
    json.dump(phones, f, ensure_ascii=False, indent=2)

print('[+] Successfully updated list_gasoline.json and list_smartphones.json (Xperia 1 VIII)!')
