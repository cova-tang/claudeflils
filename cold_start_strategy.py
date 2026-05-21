# ============================================================
# 冷启动策略
# 解决两个经典问题：
#   1. 新用户第一次进来推什么（没有历史行为）
#   2. 新商品怎么获得曝光（没人点过）
# ============================================================

from mock_data import MOCK_PRODUCTS
import random

# ── 冷启动配置 ──────────────────────────────────────────────
COLD_START_CONFIG = {
    # 新用户默认推荐数量
    "default_count": 6,

    # 新用户默认场合（最安全的起点）
    "default_occasions": ["Everyday / Casual", "Brunch"],

    # 新用户默认风格（最百搭的标签）
    "default_style_tags": ["Versatile", "Effortless", "Wardrobe Staple"],

    # 新商品定义：上架多少天内算新品
    "new_product_days": 7,

    # 新商品强制曝光位置（0=第一位，2=第三位）
    "new_product_inject_position": 2,
}


# ══════════════════════════════════════════════════════════════
# 策略一：新用户冷启动
# 没有历史行为时，推"热门+基础款"组合
# ══════════════════════════════════════════════════════════════

def get_cold_start_recommendations(gender: str = "female",
                                   count: int = 6) -> list:
    """
    新用户第一次进来时的默认推荐
    策略：按 rating × review_count 排序，取热门基础款
    确保覆盖主要品类：Tops / Bottoms / Dresses / Outerwear

    参数：
        gender: 用户性别（如果知道的话）
        count:  推荐数量
    """
    # 第一步：按性别过滤
    candidates = [
        p for p in MOCK_PRODUCTS
        if p["gender"] == gender or p["gender"] == "unisex"
    ]

    # 第二步：按热度排序（rating × log(review_count+1)）
    import math
    def hotness(p):
        rating = p.get("rating", 3.0)
        reviews = p.get("review_count", 0)
        return rating * math.log(reviews + 1)

    candidates.sort(key=hotness, reverse=True)

    # 第三步：确保品类多样性，每个品类至少选1件
    result = []
    seen_categories = set()
    priority_categories = ["Tops", "Bottoms", "Dresses", "Outerwear"]

    # 先从优先品类里各取一件
    for category in priority_categories:
        for p in candidates:
            if p["category"] == category and category not in seen_categories:
                result.append(p)
                seen_categories.add(category)
                break

    # 再用热门款补满
    for p in candidates:
        if len(result) >= count:
            break
        if p not in result:
            result.append(p)

    print(f"🆕 冷启动推荐：{len(result)} 件商品（新用户，性别={gender}）")
    for p in result:
        print(f"   {p['product_id']}: {p['name']} ({p['category']})")

    return result[:count]


# ══════════════════════════════════════════════════════════════
# 策略二：新商品曝光机制
# 新上架商品强制插入召回结果，防止永远没有曝光
# ══════════════════════════════════════════════════════════════

def inject_new_products(recall_results: list,
                        all_products: list,
                        inject_position: int = 2) -> list:
    """
    在正常召回结果里强制插入1件新品，给新商品曝光机会

    参数：
        recall_results:  正常召回的商品列表
        all_products:    全量商品库
        inject_position: 插入位置（建议第3位，即index=2）

    说明：
        - 新品定义：is_new_arrival=True 或 上架7天内
        - 如果没有新品，直接返回原始召回结果
        - 同一用户同一新品最多曝光3次，超过不再插入
    """
    # 找出新品（这里用 is_new_arrival 字段模拟，实际用上架时间判断）
    new_arrivals = [
        p for p in all_products
        if p.get("is_new_arrival", False)
        and p not in recall_results  # 不重复
    ]

    if not new_arrivals:
        return recall_results  # 没有新品，直接返回

    # 随机选一件新品插入（避免总是同一件）
    new_product = random.choice(new_arrivals)

    # 在指定位置插入
    result = recall_results.copy()
    insert_at = min(inject_position, len(result))
    result.insert(insert_at, new_product)

    print(f"🆕 新品曝光：{new_product['product_id']} ({new_product['name']}) 插入第{insert_at+1}位")

    return result


# ══════════════════════════════════════════════════════════════
# 策略三：判断是否需要冷启动
# ══════════════════════════════════════════════════════════════

def is_cold_start_user(user_id: str, user_events: list = None) -> bool:
    """
    判断用户是否需要冷启动
    冷启动条件：没有任何历史行为数据

    参数：
        user_id:     用户ID
        user_events: 该用户的历史行为列表（从Firestore读取）
    """
    if user_events is None or len(user_events) == 0:
        print(f"👤 用户 {user_id} 是新用户，启用冷启动策略")
        return True

    print(f"👤 用户 {user_id} 有 {len(user_events)} 条历史行为，使用个性化推荐")
    return False


# ══════════════════════════════════════════════════════════════
# 完整冷启动流程示例
# ══════════════════════════════════════════════════════════════

def recommend_with_cold_start(user_id: str,
                               user_input: str = None,
                               user_events: list = None,
                               gender: str = "female") -> list:
    """
    带冷启动的完整推荐入口
    - 新用户：用冷启动策略
    - 老用户：用正常向量检索（接GCP后实现）
    """
    if is_cold_start_user(user_id, user_events):
        # 新用户：直接返回热门推荐
        return get_cold_start_recommendations(gender=gender)
    else:
        # 老用户：走正常推荐流程（GCP账号到了接入）
        print("→ 走正常推荐流程（向量检索 + 精排）")
        return []  # 占位，后期接GCP实现


# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("测试1：新用户冷启动（女性）")
    print("=" * 55)
    recs = get_cold_start_recommendations(gender="female", count=4)
    print(f"返回 {len(recs)} 件商品\n")

    print("=" * 55)
    print("测试2：新用户冷启动（男性）")
    print("=" * 55)
    recs = get_cold_start_recommendations(gender="male", count=4)
    print(f"返回 {len(recs)} 件商品\n")

    print("=" * 55)
    print("测试3：判断新老用户")
    print("=" * 55)
    recommend_with_cold_start("user_new_001", user_events=[])
    recommend_with_cold_start("user_old_001", user_events=[
        {"event_type": "click", "product_id": "P001"}
    ])
