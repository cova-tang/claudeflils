# ============================================================
# Validation Layer — AI输出验证层
# 作用：确保AI返回的JSON合法，不会让系统崩溃
# 使用：每次AI输出后调用 validate_intent() 或 validate_rerank()
# ============================================================

import json

# ── 标准枚举值（唯一的真理来源）────────────────────────────────

ALLOWED_OCCASIONS = {
    "Everyday / Casual", "Work / Office", "Business Formal",
    "Date Night", "Going Out / Party", "Vacation / Resort",
    "Outdoor / Active", "Gym / Workout", "Brunch",
    "Wedding Guest", "Festival", "Loungewear / Home"
}

ALLOWED_STYLE_TAGS = {
    "Quiet Luxury", "Old Money", "Minimalist", "Streetwear",
    "Boho", "Y2K", "Feminine", "Romantic", "Classic", "Trendy",
    "Effortless", "Chic", "Edgy", "Sophisticated", "Laid-back",
    "Versatile", "Statement Piece", "Wardrobe Staple"
}

ALLOWED_SEASONS = {"Spring", "Summer", "Fall", "Winter"}

ALLOWED_PRICE_SENSITIVITY = {"budget", "mid", "premium", "luxury", "unknown"}

ALLOWED_GENDERS = {"female", "male", "unisex", "unknown"}


# ══════════════════════════════════════════════════════════════
# 验证：意图解析结果
# ══════════════════════════════════════════════════════════════

def validate_intent(raw_output: str) -> dict:
    """
    验证并修复意图解析的AI输出
    返回：合法的intent字典，或抛出异常
    """
    # 第一步：解析JSON
    intent = safe_parse_json(raw_output)
    if not intent:
        raise ValueError(f"AI返回了非法JSON: {raw_output[:100]}")

    errors = []
    warnings = []

    # 第二步：验证 occasion
    occasions = intent.get("occasion", [])
    if not isinstance(occasions, list):
        errors.append("occasion 必须是数组")
    else:
        invalid = [o for o in occasions if o not in ALLOWED_OCCASIONS]
        if invalid:
            warnings.append(f"occasion 含非法值，已移除: {invalid}")
            intent["occasion"] = [o for o in occasions if o in ALLOWED_OCCASIONS]

    # 第三步：验证 season
    seasons = intent.get("season", [])
    if not isinstance(seasons, list):
        errors.append("season 必须是数组")
    else:
        invalid = [s for s in seasons if s not in ALLOWED_SEASONS]
        if invalid:
            warnings.append(f"season 含非法值，已移除: {invalid}")
            intent["season"] = [s for s in seasons if s in ALLOWED_SEASONS]

    # 第四步：验证 style_tags
    tags = intent.get("style_tags", [])
    if not isinstance(tags, list):
        errors.append("style_tags 必须是数组")
    else:
        invalid = [t for t in tags if t not in ALLOWED_STYLE_TAGS]
        if invalid:
            warnings.append(f"style_tags 含非法值，已移除: {invalid}")
            intent["style_tags"] = [t for t in tags if t in ALLOWED_STYLE_TAGS]

    # 第五步：验证 price_sensitivity
    price = intent.get("price_sensitivity", "unknown")
    if price not in ALLOWED_PRICE_SENSITIVITY:
        warnings.append(f"price_sensitivity 非法值 '{price}'，已重置为 unknown")
        intent["price_sensitivity"] = "unknown"

    # 第六步：验证 gender
    gender = intent.get("gender", "unknown")
    if gender not in ALLOWED_GENDERS:
        warnings.append(f"gender 非法值 '{gender}'，已重置为 unknown")
        intent["gender"] = "unknown"

    # 第七步：确保必要字段存在
    intent.setdefault("occasion", [])
    intent.setdefault("season", [])
    intent.setdefault("style_tags", [])
    intent.setdefault("exclude", [])
    intent.setdefault("price_sensitivity", "unknown")
    intent.setdefault("gender", "unknown")

    # 有错误直接抛出
    if errors:
        raise ValueError(f"意图解析验证失败: {errors}")

    # 有警告只打印，不中断流程
    for w in warnings:
        print(f"⚠️  [Validation Warning] {w}")

    return intent


# ══════════════════════════════════════════════════════════════
# 验证：精排推荐结果
# ══════════════════════════════════════════════════════════════

def validate_rerank(raw_output: str, candidate_product_ids: list) -> dict:
    """
    验证精排推荐的AI输出
    candidate_product_ids: 召回阶段返回的商品ID列表（AI只能从这里选）
    """
    result = safe_parse_json(raw_output)
    if not result:
        raise ValueError(f"精排AI返回了非法JSON: {raw_output[:100]}")

    errors = []
    warnings = []

    # 验证 selected_ids
    selected = result.get("selected_ids", [])
    if not isinstance(selected, list):
        errors.append("selected_ids 必须是数组")
    elif len(selected) == 0:
        errors.append("selected_ids 不能为空")
    else:
        # 关键检查：AI不能推荐候选列表之外的商品
        invalid_ids = [pid for pid in selected if pid not in candidate_product_ids]
        if invalid_ids:
            warnings.append(f"AI推荐了候选列表之外的商品ID，已移除: {invalid_ids}")
            result["selected_ids"] = [pid for pid in selected
                                       if pid in candidate_product_ids]

        # 检查推荐数量是否合理
        if len(result["selected_ids"]) > 5:
            warnings.append("推荐商品超过5件，截取前5件")
            result["selected_ids"] = result["selected_ids"][:5]

    # 验证 recommendations 结构
    recs = result.get("recommendations", [])
    if not isinstance(recs, list):
        errors.append("recommendations 必须是数组")
    else:
        valid_recs = []
        for i, rec in enumerate(recs):
            if not isinstance(rec, dict):
                warnings.append(f"recommendations[{i}] 格式错误，已跳过")
                continue
            if "product_id" not in rec:
                warnings.append(f"recommendations[{i}] 缺少 product_id，已跳过")
                continue
            # 确保reason和styling_tip存在
            rec.setdefault("reason", "")
            rec.setdefault("styling_tip", "")
            valid_recs.append(rec)
        result["recommendations"] = valid_recs

    # 确保outfit_summary存在
    result.setdefault("outfit_summary", "")

    if errors:
        raise ValueError(f"精排验证失败: {errors}")

    for w in warnings:
        print(f"⚠️  [Validation Warning] {w}")

    return result


# ══════════════════════════════════════════════════════════════
# 工具函数：安全解析JSON
# ══════════════════════════════════════════════════════════════

def safe_parse_json(text: str) -> dict:
    """
    容错解析：处理AI可能输出的各种非标准格式
    """
    if not text:
        return {}

    text = text.strip()

    # 情况一：有 ```json 标记
    if "```json" in text:
        try:
            text = text.split("```json")[1].split("```")[0].strip()
        except IndexError:
            pass

    # 情况二：有 ``` 标记但没有json
    elif "```" in text:
        try:
            text = text.split("```")[1].split("```")[0].strip()
        except IndexError:
            pass

    # 情况三：前后有多余文字，找到第一个{和最后一个}
    if not text.startswith(("{", "[")):
        start = text.find("{")
        if start == -1:
            start = text.find("[")
        end = max(text.rfind("}"), text.rfind("]")) + 1
        if start != -1 and end > start:
            text = text[start:end]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return {}


# ══════════════════════════════════════════════════════════════
# 测试
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== 测试1：正常输入 ===")
    good_input = '''{"occasion": ["Going Out / Party"], "season": ["Summer"],
                    "style_tags": ["Chic", "Sophisticated"],
                    "exclude": [], "price_sensitivity": "premium",
                    "gender": "female"}'''
    result = validate_intent(good_input)
    print(f"✅ 通过: {result}\n")

    print("=== 测试2：非法occasion值 ===")
    bad_occasion = '''{"occasion": ["Party", "Going Out / Party"],
                       "season": [], "style_tags": ["Chic"],
                       "exclude": [], "price_sensitivity": "mid",
                       "gender": "female"}'''
    result = validate_intent(bad_occasion)
    print(f"✅ 修复后: occasion={result['occasion']}\n")

    print("=== 测试3：AI返回了候选列表外的商品 ===")
    bad_rerank = '''{"selected_ids": ["P001", "P999"],
                     "recommendations": [
                       {"product_id": "P001", "reason": "Great choice",
                        "styling_tip": "Pair with jeans"},
                       {"product_id": "P999", "reason": "Hallucinated product",
                        "styling_tip": "Does not exist"}
                     ],
                     "outfit_summary": "A chic look"}'''
    candidates = ["P001", "P002", "P003", "P004", "P005"]
    result = validate_rerank(bad_rerank, candidates)
    print(f"✅ 修复后: selected_ids={result['selected_ids']}\n")

    print("=== 测试4：AI返回了带```的格式 ===")
    messy_json = """Sure! Here's the result:
```json
{"occasion": ["Brunch"], "season": [], "style_tags": ["Effortless"],
 "exclude": ["heels"], "price_sensitivity": "mid", "gender": "female"}
```
Hope this helps!"""
    result = validate_intent(messy_json)
    print(f"✅ 清理后: {result}\n")

    print("所有测试通过 ✅")
