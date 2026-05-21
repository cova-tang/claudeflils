# ============================================================
# 文件1：模拟商品数据
# 作用：生成10件假衣服数据，等真实数据来了直接替换
# ============================================================

import json
import os

# 模拟商品数据（10件衣服）
MOCK_PRODUCTS = [
    {
        "product_id": "P001",
        "name": "轻量冲锋衣",
        "category": "外套",
        "gender": "unisex",
        "season": ["秋", "冬"],
        "scene": ["户外", "登山", "旅行"],
        "color": "军绿色",
        "price": 599,
        "tags": ["防风", "防水", "轻量", "户外"],
        "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=512"
    },
    {
        "product_id": "P002",
        "name": "宽松休闲卫衣",
        "category": "上衣",
        "gender": "female",
        "season": ["春", "秋"],
        "scene": ["日常", "通勤", "居家"],
        "color": "米白色",
        "price": 299,
        "tags": ["宽松", "舒适", "百搭", "休闲"],
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=512"
    },
    {
        "product_id": "P003",
        "name": "修身西装外套",
        "category": "外套",
        "gender": "male",
        "season": ["春", "秋"],
        "scene": ["商务", "通勤", "正式场合"],
        "color": "深蓝色",
        "price": 899,
        "tags": ["正式", "商务", "修身", "职场"],
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=512"
    },
    {
        "product_id": "P004",
        "name": "高腰牛仔裤",
        "category": "裤子",
        "gender": "female",
        "season": ["春", "夏", "秋"],
        "scene": ["日常", "休闲", "约会"],
        "color": "浅蓝色",
        "price": 399,
        "tags": ["高腰", "显腿长", "百搭", "牛仔"],
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=512"
    },
    {
        "product_id": "P005",
        "name": "棉麻连衣裙",
        "category": "裙子",
        "gender": "female",
        "season": ["夏"],
        "scene": ["日常", "度假", "约会"],
        "color": "白色",
        "price": 459,
        "tags": ["清新", "透气", "度假", "文艺"],
        "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=512"
    },
    {
        "product_id": "P006",
        "name": "羽绒服",
        "category": "外套",
        "gender": "unisex",
        "season": ["冬"],
        "scene": ["日常", "户外", "旅行"],
        "color": "黑色",
        "price": 1299,
        "tags": ["保暖", "防寒", "轻便", "冬季必备"],
        "image_url": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=512"
    },
    {
        "product_id": "P007",
        "name": "直筒休闲裤",
        "category": "裤子",
        "gender": "male",
        "season": ["春", "夏", "秋"],
        "scene": ["日常", "通勤", "休闲"],
        "color": "卡其色",
        "price": 349,
        "tags": ["百搭", "休闲", "直筒", "舒适"],
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=512"
    },
    {
        "product_id": "P008",
        "name": "针织毛衣",
        "category": "上衣",
        "gender": "female",
        "season": ["秋", "冬"],
        "scene": ["日常", "约会", "通勤"],
        "color": "驼色",
        "price": 519,
        "tags": ["温柔", "针织", "保暖", "秋冬"],
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=512"
    },
    {
        "product_id": "P009",
        "name": "运动套装",
        "category": "套装",
        "gender": "unisex",
        "season": ["春", "夏", "秋"],
        "scene": ["运动", "健身", "日常"],
        "color": "黑灰色",
        "price": 699,
        "tags": ["运动", "透气", "弹力", "健身"],
        "image_url": "https://images.unsplash.com/photo-1483721310020-03333e577078?w=512"
    },
    {
        "product_id": "P010",
        "name": "风衣",
        "category": "外套",
        "gender": "female",
        "season": ["春", "秋"],
        "scene": ["通勤", "约会", "日常"],
        "color": "米色",
        "price": 799,
        "tags": ["优雅", "百搭", "经典", "气质"],
        "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=512"
    }
]

def save_mock_data():
    """保存模拟数据到本地JSON文件"""
    os.makedirs("data", exist_ok=True)
    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(MOCK_PRODUCTS, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(MOCK_PRODUCTS)} 件商品数据到 data/products.json")

if __name__ == "__main__":
    save_mock_data()
    print("\n示例商品：")
    for p in MOCK_PRODUCTS[:3]:
        print(f"  - {p['product_id']}: {p['name']} ({p['color']}, ¥{p['price']})")
