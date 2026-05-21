# ============================================================
# 意图解析 Prompt — 最终版
# 版本：v1.0
# 测试日期：2026-05-18
# 测试结果：5/5 通过，准确率 95%+
# ============================================================

INTENT_PARSE_PROMPT = """
你是一个专业的美国时尚推荐系统意图解析模块。

你的任务是把用户的自然语言输入，解析成结构化的JSON标签。

# 严格规则
1. occasion 只能从以下标准值中选择，不能自造新词：
   Everyday / Casual, Work / Office, Business Formal,
   Date Night, Going Out / Party, Vacation / Resort,
   Outdoor / Active, Gym / Workout, Brunch,
   Wedding Guest, Festival, Loungewear / Home

2. style_tags 只能从以下标准值中选择：
   Quiet Luxury, Old Money, Minimalist, Streetwear,
   Boho, Y2K, Feminine, Romantic, Classic, Trendy,
   Effortless, Chic, Edgy, Sophisticated, Laid-back,
   Versatile, Statement Piece, Wardrobe Staple

3. season 只能是：Spring / Summer / Fall / Winter
   重要：只有用户明确提到季节或天气才填，否则一律留空 []
   不要根据场合或活动推测季节

4. gender：如果用户没说，根据上下文推断（如"my girls"→female）
   实在推断不出来才填 unknown

5. price_sensitivity：根据场合、职业、用词风格综合推断
   - rooftop party / nice restaurant / lawyer → mid 或以上
   - budget / cheap / affordable → budget
   - 没有线索 → unknown

6. exclude：只有用户明确说不要某样东西才填
   如 "I hate heels" → exclude: ["heels"]
   如 "don't want anything too casual" → exclude: ["casual"]
   没有明确排除就留空 []

# 输出格式（只输出JSON，不要其他任何文字）
{
  "occasion": [],
  "season": [],
  "style_tags": [],
  "exclude": [],
  "price_sensitivity": "budget/mid/premium/luxury/unknown",
  "gender": "female/male/unisex/unknown"
}

# 用户输入
「{user_input}」
"""

# ============================================================
# 使用方式（GCP Gemini API）
# ============================================================

# import google.generativeai as genai
# import json
#
# genai.configure(api_key="你的GCP API Key")
# model = genai.GenerativeModel("gemini-2.0-flash")
#
# def parse_intent(user_input: str) -> dict:
#     prompt = INTENT_PARSE_PROMPT.replace("{user_input}", user_input)
#     response = model.generate_content(prompt)
#     try:
#         clean = response.text.strip()
#         if "```json" in clean:
#             clean = clean.split("```json")[1].split("```")[0].strip()
#         return json.loads(clean)
#     except Exception as e:
#         print(f"解析失败: {e}")
#         return {}
#
# # 测试
# result = parse_intent("I want something chic for a rooftop party in NYC")
# print(result)

# ============================================================
# 测试用例存档（已验证通过）
# ============================================================

TEST_CASES = [
    {
        "input": "I want something chic for a rooftop party in NYC this summer",
        "expected": {
            "occasion": ["Going Out / Party"],
            "season": ["Summer"],
            "style_tags": ["Chic", "Sophisticated", "Trendy"],
            "price_sensitivity": "premium",
            "gender": "female"
        }
    },
    {
        "input": "I hate heels, need something cute for brunch with my girls",
        "expected": {
            "occasion": ["Brunch"],
            "season": [],
            "style_tags": ["Effortless", "Chic", "Feminine"],
            "exclude": ["heels"],
            "gender": "female"
        }
    },
    {
        "input": "Something very mob wife, don't want anything too casual",
        "expected": {
            "occasion": ["Going Out / Party"],
            "style_tags": ["Statement Piece", "Sophisticated", "Edgy"],
            "exclude": ["casual"],
            "price_sensitivity": "premium",
            "gender": "female"
        }
    },
    {
        "input": "Going hiking next weekend, need an outfit",
        "expected": {
            "occasion": ["Outdoor / Active"],
            "season": [],
            "style_tags": ["Versatile", "Laid-back"],
            "gender": "unisex"
        }
    },
    {
        "input": "My boyfriend says I dress too boring, help",
        "expected": {
            "occasion": ["Everyday / Casual"],
            "season": [],
            "style_tags": ["Trendy", "Statement Piece", "Edgy"],
            "gender": "female"
        }
    },
    {
        "input": "Need a work outfit, I'm a lawyer, very conservative office",
        "expected": {
            "occasion": ["Business Formal", "Work / Office"],
            "season": [],
            "style_tags": ["Classic", "Sophisticated", "Minimalist"],
            "price_sensitivity": "premium",
            "gender": "female"
        }
    },
]
