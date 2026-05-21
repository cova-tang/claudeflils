# AI时尚推荐系统 — 项目决策备忘录
# 用途：放入Claude Projects的Files，补充Instructions无法覆盖的细节
# 更新日期：2026-05-21

---

## 一、关键技术决策和原因

### 为什么选GCP而不是AWS
- 已确定使用Gemini模型，Gemini原生在GCP，调用延迟比跨平台低30-50%
- AWS企业账号审批被卡（个人账号申请Bedrock被拒），GCP注册即用
- 面向美国用户，GCP美国区节点够用
- 注意：AWS Bedrock上现在已有OpenAI GPT OSS系列模型（新发现），
  但我们架构已确定用Gemini Embedding，换GPT会带来跨平台复杂度，不值得

### 为什么选Gemini而不是Claude做精排
- 千万级请求下Claude Sonnet 4费用是Gemini Flash-Lite的35倍
- Claude Haiku 4.5是最便宜的Claude，仍比Flash-Lite贵10倍
- 老板要求：最低成本达到合理效果，token cost控制不好随时烧没
- 通过Prompt Engineering可以把Flash-Lite效果调到接近Claude的85-90%
- 后期用LoRA微调进一步缩小差距

### 为什么用FashionCLIP而不是一直用Gemini Embedding
- FashionCLIP在时尚垂直领域专门训练，理解"Quiet Luxury"等美学词更准
- 本地跑，完全免费，阶段二替换后Embedding费用降为零
- 已验证：4条查询全部命中，美学风格分类完全正确
- Gemini Embedding 2图文匹配评分93.4分，FashionCLIP在时尚垂直领域更强

### 为什么用Content-Based而不是协同过滤
- 冷启动天然解决（不依赖用户历史行为）
- 新商品上架即可被推荐（不需要等积累数据）
- 现在没有用户数据，协同过滤根本跑不起来

### 为什么选Vertex AI Vector Search而不是Pinecone
- GCP全家桶，同一账号，账单一张，不用到处登录
- 和Gemini原生无缝集成，延迟更低
- MVP阶段按量计费，比Pinecone固定月费$70-120更便宜
- 出问题只需找一个平台排查

---

## 二、三阶段模型演进路线（核心）

### 阶段一：GCP全托管（现在 → MVP上线）
目标：快速跑通，2个月内出Demo

Embedding层：Gemini Embedding 2
  - 全托管，一行代码调用
  - 图文匹配评分93.4分（优于Nova Embedding的84.0分）
  - 3072维向量，精度高
  - 价格：$0.20/百万tokens（文字），$0.45/百万tokens（图片）

精排LLM：Gemini 2.5 Flash-Lite
  - 价格：输入$0.10/百万，输出$0.40/百万
  - 50万用户×20套/天：月费约$12,000
  - Prompt Engineering调优后效果接近Claude的85-90%

向量库：Vertex AI Vector Search
  - GCP原生，和Gemini无缝集成
  - 按量计费，5000件商品建库约$0.06（忽略不计）

用户偏好数据库：Firestore
  - 存储用户黑名单、点击记录、推荐日志

月费估算（50万用户）：
  每天1套/人：约$600
  每天20套/人：约$12,000

### 阶段二：半脱离GCP（MVP上线3-6个月后）
目标：成本降50-70%，效果提升

Embedding层：FashionCLIP（本地部署）替换Gemini Embedding
  - 开源免费，本地跑，Embedding费用降为零
  - 时尚垂直领域效果更好
  - 需要一台服务器（Cloud Run或自建）
  - 模型已在本地验证跑通（fashionclip_local.py）

精排LLM：继续用Gemini 2.5 Flash-Lite
  - 这阶段重点是Prompt Engineering深度调优
  - 积累用户数据后准备L3微调

向量库：迁移到自建Qdrant
  - 开源免费，替换Vertex AI Vector Search
  - 节省向量库费用

月费估算（50万用户×20套）：约$3,000（省75%）

### 阶段三：基本脱离GCP（规模化后，日请求量>5万）
目标：极致省钱，完全掌控数据

Embedding层：FashionCLIP（继续）
  - 可升级到SigLIP（谷歌新版，性能优于FashionCLIP）
  - 完全本地，零API费用

精排LLM：轻量开源模型 + LoRA微调
  候选模型（按优先级）：
  1. Qwen2-7B（阿里开源，中英文都强，8-12G显存）
  2. MiniMax（便宜，老板提到过）
  3. Gemini Flash-Lite继续用（如果LoRA效果不理想）

  LoRA微调时机：
  - 积累1000条用户反馈后启动L3（每周离线微调，GPU费用约$20-50/次）
  - 积累1万条偏好对比数据后考虑L4（类RLHF）

向量库：FAISS（本地内存）
  - 完全本地，零成本
  - 需要GPU服务器：RTX 3060/4060（8-12G显存），月租约$200-400

月固定成本：$500-2000（不随请求量涨价）

---

## 三、各模型价格对照表（精排LLM）

| 模型 | 输入/百万tokens | 输出/百万tokens | 50万用户×20套月费 |
|------|--------------|--------------|----------------|
| Gemini Flash-Lite | $0.10 | $0.40 | ~$12,000 |
| Gemini Flash | $0.30 | $2.50 | ~$37,000 |
| Gemini Pro | $1.25 | $10.00 | ~$50,000 |
| GPT-5 nano | $0.05 | $0.40 | ~$10,000 |
| GPT-4o mini | $0.15 | $0.60 | ~$18,000 |
| Claude Haiku 4.5 | $1.00 | $5.00 | ~$120,000 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | ~$430,000 |

结论：Gemini Flash-Lite是GCP生态里最优选择，GPT-5 nano略便宜但需跨平台。

---

## 四、Harness Engineering计划

### 是什么
给AI模型套"缰绳"，用自动化测试框架系统评估和控制输出质量。
解决问题：换模型或改Prompt时，不靠人肉测试，5分钟知道效果好不好。

### 实施时机
- 现在MVP期：不做，先跑通流程
- 第二阶段调优Prompt时：建20-50条测试用例
- 第三阶段换便宜模型时：全力用Harness对比效果

### 自动评分标准（未来实现）
occasion是否合法：+20分
price在范围内：+20分
排除了用户不喜欢的：+20分
风格标签对了：+20分
返回合法JSON：+20分
总分<80分报警

---

## 五、踩过的坑（避免重复犯错）

### Python文件名不能以数字开头
之前文件叫 01_mock_data.py，导致 from 01_mock_data import 报错。
解决：文件名改为 mock_data.py, local_recommend.py 等。

### ASOS不允许爬虫
robots.txt限制，图片URL无法直接抓取。
解决：爬取 asos.com/us（美国站），价格直接是美元，不涉及汇率。
注意：ASOS图片URL格式需要工程师单独处理。

### FashionCLIP返回对象不是张量
get_text_features() 返回 BaseModelOutputWithPooling 对象，
直接调用 .norm() 会报 AttributeError。
解决：
  output = model.get_text_features(**inputs)
  embedding = output if isinstance(output, torch.Tensor) else output.pooler_output

### AWS Bedrock个人账号无法使用（已绕过）
报错：ValidationException，需要企业客户验证。
结论：转GCP，不再依赖AWS Bedrock。
注意：AWS账号现在能进模型目录（已看到GPT OSS系列），但架构已确定GCP。

### Gemini Flash-Lite可能输出非标准JSON
有时会在JSON前后加多余文字或```标记。
解决：validation_layer.py里的 safe_parse_json() 函数已处理所有情况。

### CLIP相似度分数天然偏低
FashionCLIP的相似度分数在0.2左右属于强匹配，不是0.8才叫好。
不要因为分数看起来低就以为效果差，这是正常现象。

---

## 六、Prompt测试结果存档

### 意图解析 Prompt v1.0
测试日期：2026-05-18
总测试：21条，通过：20/21，准确率95%
失败案例：
  输入："My dress code says smart casual but also cocktail attire"
  问题：cocktail attire 被映射到 Work/Office，应该是 Wedding Guest
  修复计划：v1.1加入规则 "cocktail attire → Wedding Guest 或 Going Out/Party"

通过的特殊场景：
  ✅ 法语输入（Je veux quelque chose de chic pour une soirée）
  ✅ 单字母输入（k）
  ✅ 含emoji（idk just something cute ig 🤷‍♀️）
  ✅ 美国文化梗（Something that says I have a 401k）
  ✅ 男性用户（I'm a guy, need something for girlfriend's family dinner）
  ✅ 多排除条件（no blazers, nothing black, work outfit）
  ✅ 法语输入（Je veux quelque chose de chic pour une soirée）
  ✅ Coachella（正确识别Festival + Spring季节）
  ✅ baby shower花园派对（正确映射Brunch + Feminine/Romantic/Boho）

### 精排推荐 Prompt v1.0
测试日期：2026-05-18
总测试：5条，通过：5/5，100%
推荐语质量：接近专业时尚顾问水平
特点：正确排除了不符合场合的商品（Y2K风衣不适合rooftop party premium）

### FashionCLIP实验结果
测试日期：2026-05-18
实验一（文字→图片匹配）：4/4命中，全部正确
实验二（搭配相似度）：西装外套↔直筒裤 0.482，冲锋衣↔连衣裙 0.307（符合预期）
实验三（美学风格分类）：
  西装外套 → Quiet Luxury Minimalist ✅
  连衣裙 → Boho Romantic Feminine ✅
  冲锋衣 → Outdoor Athletic Sporty ✅
  运动套装 → Outdoor Athletic Sporty ✅

---

## 七、数据规范关键点

### 工程师爬取时需要注意
1. category/occasion/style_tags 必须用标准枚举值，不能自造新词
2. color_family 不在网页上，工程师用代码映射
3. source_type 根据URL自动判断，不需要从网页找
4. style_tags/aesthetic/trend_tags 网页没有，交给AI自动标注脚本处理
5. 价格必须是美元（爬asos.com/us，不是asos.com）
6. 工程师只需爬基础字段，AI自动标注补全风格字段

### color_family映射规则（工程师代码实现）
black/white/grey/beige/camel → Neutral
red/orange/yellow → Warm
blue/green/purple → Cool
pink/lavender/mint → Pastel
brown/khaki/olive → Earth
neon/multi/stripe → Bold

### AI自动标注流程
工程师交付基础字段数据后：
1. 跑 auto_tag_product() 函数（在 bedrock_recommend.py 里）
2. Gemini自动为每件商品打 style_tags/aesthetic/trend_tags
3. 验证层校验标签合法性
4. 入库

---

## 八、费用关键数字

### 50万用户场景（老板最关心）
每天1套/人：月费约$600（Flash-Lite）
每天20套/人：月费约$12,000（Flash-Lite）
对比Flash：月费约$37,000（贵约3倍）
对比Pro：月费约$50,000（贵约4倍）

### 省钱三策略（可降低40-70%）
1. Prompt缓存：节省30-50% LLM输入费，立即可用
2. 模型路由：简单查询用Lite，复杂查询用Flash，节省20-40%
3. FashionCLIP替换Embedding：节省全部Embedding费（阶段二）

### Batch API折扣
非实时任务用Batch API，Flash-Lite打五折（$0.05/$0.20）

### 单次请求成本
一个用户搜一次：约$0.00024（不到两厘钱人民币）

---

## 九、工程师对接说明

### 接口约定（API联调时用）
输入：{ user_id: string, user_input: string, image_url?: string }
输出：{
  selected_ids: string[],
  recommendations: [{product_id, reason, styling_tip}],
  outfit_summary: string
}

### 数据库表（Firestore，第一天就要建）
user_events: user_id, product_id, event_type, dwell_seconds,
             recommendation_id, timestamp
recommendation_logs: recommendation_id, user_id, user_input,
                     returned_ids, model_used, latency_ms, timestamp

### 冷启动接口
新用户（user_events为空）：调用 get_cold_start_recommendations(gender)
老用户：走正常推荐流程

### 新商品曝光规则
上架7天内算新品，强制插入召回结果第3位
同一用户同一新品最多曝光3次

---

## 十、下一步行动清单

### GCP账号到位后（立即执行）
第1天：开通Vertex AI API，创建Cloud Storage存储桶
第2天：上传商品数据，创建Vertex AI Vector Search索引
第3天：跑通文字搜图，验证意图解析Prompt效果
第1周：完整推荐流程端到端跑通，输出API接口
第2周：和前端同事联调，建立Firestore反馈数据收集

### 数据积累后的里程碑
积累1000条用户反馈：启动L3微调排序模型
积累1万条偏好对比：考虑L4 LoRA微调精排LLM
日请求量>5万：评估迁移到阶段二（FashionCLIP替换Embedding）
日请求量>10万：评估迁移到阶段三（自建向量库+轻量LLM）

### Prompt迭代计划
意图解析v1.1：修复cocktail attire映射问题
意图解析v1.2：增加更多美国slang和TikTok梗覆盖
精排v1.1：加入Few-shot示例（提升30-40%效果）
精排v2.0：接入LoRA微调后的专属模型
