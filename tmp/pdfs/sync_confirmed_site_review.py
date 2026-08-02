"""Apply only the answers confirmed in the independent, no-PDF-answer review."""
import json
from pathlib import Path

updates = {
2: ("A", """【题干关键词】
• 从 S3 读取通信、提取模板中的一段、调用 Bedrock 审查、将结果写回同一 S3 桶。
• 目标是确定性的数据流，且希望使用托管、低代码的编排。

【判断逻辑】
• A：Bedrock Flows 的 S3 retrieval/storage 节点分别处理读取和写回；表达式可提取模板片段；Prompt/Agent 节点把片段交给模型。因此一个 Flow 即覆盖四个步骤。

【为什么不是其他选项】
A. 正确选项。
B. Step Functions 可以实现，但需要自己定义 S3 服务集成、解析和模型任务；相对 Flows 不是最低代码量。
C. 代理适合需要自主工具选择的场景；本题只是固定读、解析、审查、写回流程，代理增加不必要的不确定性。
D. 三个 Lambda 将确定性工作拆散为自定义代码，运维和错误处理更多。

【最终结论】A 用 Flows 原生的 S3、表达式和模型节点直接实现固定审查流程，最符合低代码要求。"""),
29: ("B", """【题干关键词】
• 要保护视频档案和模型输入输出、限制不同部门可调用的模型，并审计“谁在何时访问什么”。
• 需要同时覆盖私网、最小权限、数据级审计和异常告警。

【判断逻辑】
• B：ABAC 将部门属性映射到权限；VPC endpoint 保证私有 Bedrock 调用；ModelId 与 GuardrailIdentifier 条件限制模型与护栏；CloudTrail Lake、S3 data events 和 KMS events 提供审计证据。

【为什么不是其他选项】
A. 有私网和内容控制，但 agent trace 不是 S3/KMS/视频档案访问的完整审计机制，且未实现部门级模型授权。
B. 正确选项。
C. 端点策略、Config 和 S3 日志不足以精确约束 ModelId/GuardrailIdentifier，也没有全面的跨服务审计查询。
D. Macie 与 Insights 有助发现异常，但缺少调用前的 ABAC、模型和护栏强制控制。

【最终结论】B 同时把网络隔离、细粒度模型访问和可查询审计落实在正确的 AWS 控制面上。"""),
35: ("C", """【题干关键词】
• 推荐必须来自真实产品目录、避免无关/不存在商品；大多数请求唯一，且要减少响应时间。

【判断逻辑】
• C：Knowledge Bases 的 RAG 先从产品目录检索事实，再让模型基于检索结果回答；optimized latency 配置直接改善交互时延。

【为什么不是其他选项】
A. 护栏和推理检查不能把模型回答约束到实时产品目录，也不能解决目录外商品。
B. 提示约束和流式传输只能改善表达和感知延迟，不能提供目录事实依据。
C. 正确选项。
D. 自建 OpenSearch 校验和缓存可行，但需要自建检索、校验与缓存逻辑；对大多数唯一请求，缓存收益有限。

【最终结论】C 用托管 RAG 解决事实和相关性根因，并用优化时延配置改善响应。"""),
36: ("C+D", """【题干关键词】
• 组织级集中治理：调用必须带集中护栏，且只能调用批准模型；还要将护栏部署到全部账户。

【判断逻辑】
• C：SCP 对没有指定集中 guardrail identifier 的调用显式拒绝；权限边界把每位员工可调用的模型限制在批准集合。
• D：CloudFormation StackSets 将配置好阻断策略的 Guardrail 一致部署到组织账户。

【为什么不是其他选项】
A. 权限边界可辅助限制，但“批准护栏”没有通过集中部署的资源和显式 SCP 拒绝形成完整闭环。
B. 仅要求任意 guardrail identifier，不能保证使用的是组织部署的指定护栏。
C. 正确选项。
D. 正确选项。
E. 掩码策略不等于阻止特定主题和专有信息进入模型。

【最终结论】C 负责强制调用边界，D 负责集中部署实际护栏，两者共同满足组织级治理。"""),
38: ("A", """【题干关键词】
• 临床、保险、预约和理赔是不同领域；需数千并发、可增加新能力、且回复必须专业准确。

【判断逻辑】
• A：supervisor agent 负责自然语言意图分类和路由，collaborator agent 负责领域任务；每个协作者使用隔离知识库和 RAG，减少跨部门数据串用。

【为什么不是其他选项】
A. 正确选项。
B. 每部门再建 supervisor 且手动交接，扩展和运营复杂度高。
C. 单个通用 agent 依赖规则路由，难以随领域和自然语言变化扩展。
D. 多个 supervisor 并行回答同一问题且共用知识库，会造成重复调用、冲突和数据隔离不足。

【最终结论】A 是可扩展的 supervisor-collaborator 多代理模式，并以独立知识库保障领域准确性。"""),
39: ("C", """【题干关键词】
• 推荐不能包含目录外商品、要相关且低延迟；请求大多唯一，不能依赖缓存命中。

【判断逻辑】
• C：Bedrock Knowledge Bases RAG 用目录数据 grounding 推荐内容，optimized latency 降低调用时延。

【为什么不是其他选项】
A. 护栏和预置吞吐不提供产品目录检索事实。
B. 提示工程不保证只产生在售商品；流式仅改善感知延迟。
C. 正确选项。
D. 自建搜索校验与缓存需要额外系统；缓存对唯一交互价值不高。

【最终结论】C 同时处理“目录外幻觉”和时延，是最直接的托管方案。"""),
40: ("D", """【题干关键词】
• 少于 100 万份文件；按文本语义和元数据查找相似摘要；要求最少运维。

【判断逻辑】
• D：Titan Embeddings 提供受管嵌入，Aurora PostgreSQL Serverless + pgvector 同时容纳向量和关系型元数据，并按负载自动伸缩。

【为什么不是其他选项】
A. OpenSearch Service 可做向量检索，但题目没有需要其搜索集群能力，运维开销通常高于 Aurora Serverless。
B. 主题抽取不能替代文本向量相似性，且缺关键词时召回会受限。
C. 自行托管 sentence-transformer 增加模型端点和维护工作。
D. 正确选项。

【最终结论】D 以受管嵌入和 Serverless 向量数据库满足中等规模语义检索和元数据查询。"""),
41: ("C", """【题干关键词】
• 50-200 页技术文档超过上下文窗口；需减少截断和不一致回答。

【判断逻辑】
• C：语义分块在自然意义边界切分，RetrieveAndGenerate 只动态取与查询相关的块，避免把整份长文档硬塞入上下文。

【为什么不是其他选项】
A. 先顺序拼接多个固定块直到接近上限，仍可能超窗并把大量无关内容送入模型。
B. 分层分块可行，但此题的核心是长文档主题边界和直接按相关块生成；语义分块更直接。
C. 正确选项。
D. 等长分段会割裂语义；应用层汇总也增加定制代码。

【最终结论】C 通过语义分块和检索式生成从根源避免上下文超限。"""),
43: ("B", """【题干关键词】
• 2,000 万餐厅、2 亿评论、复杂自然语言、500ms、小时更新和峰值弹性。

【判断逻辑】
• B：OpenSearch Service 的向量索引/k-NN 适合大规模低延迟语义搜索；同一嵌入模型处理文档和查询，支持持续索引更新。

【为什么不是其他选项】
A. 关键词规则不能充分理解复杂自然语言语义。
B. 正确选项。
C. 保留 PostgreSQL 和自建 Lambda 检索会增加开发与大规模扩展压力。
D. Knowledge Base 更偏 RAG 文档问答；自定义摄取下不如 OpenSearch 向量搜索直接适配超大餐厅/评论检索。

【最终结论】B 是在规模、语义质量、低延迟和最少开发之间最合适的组合。"""),
49: ("B+D", """【题干关键词】
• 仅从 eu-central-1 使用 Nova Pro 的 EU 地理 CRI；SCP 不能破坏数据驻留，同时必须放通 inference profile 的全部目的区域。

【判断逻辑】
• B：允许精确的 eu.amazon.nova-pro inference profile。
• D：验证角色及 SCP 对该 profile 全部 EU 服务区域的 InvokeModel 权限；缺任一目的区域会造成 CRI 的显式拒绝。

【为什么不是其他选项】
A. AdministratorAccess 不能覆盖 SCP 显式 Deny。
B. 正确选项。
C. 单独启用 eu-west-3 的模型访问不能解决对 inference profile 的 SCP/角色授权。
D. 正确选项。
E. 放开全部 eu-* profile 过宽，违背精确访问控制。

【最终结论】B 精确授权 profile，D 确保它的所有 EU 目的区域可用，既能 CRI 又不放宽治理。"""),
51: ("A+B+D", """【题干关键词】
• 扫描件结构化提取、推理前 PII 脱敏、低置信度同区人审、区域驻留和审计。

【判断逻辑】
• A：Textract 提取，A2I 将低置信度页面交给同区域人工审核。
• B：Lambda 在推理前编辑 PII，Guardrails 保护输出，区域 IAM 角色限制数据访问。
• D：S3 按申请人区域保存原件并以对象标签保留审计属性。

【为什么不是其他选项】
A. 正确选项。
B. 正确选项。
C. Kendra/OpenSearch 不是扫描文档字段提取和 PII 脱敏方案。
D. 正确选项。
E. 数据质量和编排有用，但未直接解决同区低置信人审、PII 或区域存储的核心缺口。
F. Clarify 不用于评估 Bedrock 生成决定，且题干未要求公平性报告。

【最终结论】A+B+D 分别覆盖提取人审、PII/模型安全和区域化存储审计。"""),
56: ("B", """【题干关键词】
• 识别活跃/闲置订阅、季度 power users、培训团队，以及每用户接受的 Amazon Q 代码行。

【判断逻辑】
• B：Amazon Q Developer 管理员仪表盘和 per-user activity report 已提供采用和用户活动指标，包括接受的代码行；无需自行采集并构建数据管道。

【为什么不是其他选项】
A. 聚合使用仪表盘不足以定位具体用户和团队。
B. 正确选项。
C. 自建 S3/QuickSight 能实现，但与原生管理报告相比运维更多。
D. CloudTrail 记录 API 活动，不提供接受建议代码行等产品使用指标。

【最终结论】B 已原生覆盖用户级采用指标，是最低运维选择。"""),
60: ("B", """【题干关键词】
• Step Functions 状态数据超过 256KB；须保留顺序 ReAct 工作流和可观察性，且减少运维。

【判断逻辑】
• B：Step Functions 的 Bedrock 优化集成可用 S3 URI 作为大输入/输出位置，ResultPath/ResultSelector 只在状态间传递引用。

【为什么不是其他选项】
A. DynamoDB 存引用可行，但还需 Map 读取和数据模型设计，复杂度更高。
B. 正确选项。
C. 压缩/解压 Lambda 增加 CPU、错误点和调试负担，且结果仍可能超限。
D. 拆分状态机再用 EventBridge 协调，破坏原有线性可观测性并增加组件。

【最终结论】B 用 S3 外置大载荷、在状态内只传 URI，是官方集成的最小开销模式。"""),
63: ("A", """【题干关键词】
• 阻断复杂 prompt injection、记录每次安全干预、支持跨区域故障转移。

【判断逻辑】
• A：Guardrails 可配置 prompt-attack filter；guardrail profile 支持跨区域 guardrail inference；CloudWatch Logs/自定义指标可记录干预事件。

【为什么不是其他选项】
A. 正确选项。
B. WAF 可做外围过滤，但没有跨区域 guardrail inference，CloudTrail 也不提供每次干预细节。
C. 自建 Comprehend 分类器和 API Gateway 校验不如 Guardrails 的 prompt-attack 能力直接，且没有跨区域方案。
D. 不存在“复制 guardrail 到跨区域以实现故障转移”的等价托管能力；也未针对 prompt attack 配置正确过滤器。

【最终结论】A 是唯一同时覆盖 prompt attack、干预日志和 guardrail 跨区域推理的方案。"""),
66: ("A+B", """【题干关键词】
• Lambda 调 Bedrock Agent Runtime 得到 400 授权错误；访问 OpenSearch Serverless 得到 403；还需按模式扩展集合/索引权限。

【判断逻辑】
• A：Lambda 角色需要 Bedrock 调用权限和 aoss:APIAccessAll 的 IAM 权限。
• B：OpenSearch Serverless 的 data access policy 使用 pattern resource rules，对集合和索引真正授予数据面访问。

【为什么不是其他选项】
A. 正确选项。
B. 正确选项。
C. 网络端点不授予数据访问权限，不能单独解决 403。
D. OpenSearch Serverless 使用 IAM 和 data access policy，不需要保存数据库口令。
E. es:ESHttp* 属于托管 OpenSearch domain 模式，不适用于 Serverless data access control。

【最终结论】A 解决 IAM 调用门槛，B 解决 Serverless 数据面授权，二者缺一不可。"""),
73: ("A", """【题干关键词】
• 必须有来源引用、从公司数据检索、解释建议依据、低于 3 秒且最低运维。

【判断逻辑】
• A：Knowledge Bases 提供托管 RAG 和 source attribution；Claude Messages API 生成带检索上下文的建议，S3 可保存审计材料。

【为什么不是其他选项】
A. 正确选项。
B. 扩展思维可解释推理，但没有公司数据检索和可验证来源归因。
C. 自建 SageMaker、Lambda、RDS 既增加运维，也拆散了检索和引用链路。
D. 自定义检索追踪和思维链不等于内建来源归因，且额外开发更多。

【最终结论】A 以托管 RAG 的来源归因直接满足可解释和引用要求。"""),
78: ("D", """【题干关键词】
• 所有内容到达 FM 前完成攻击性内容、PII 和不当建议征求的过滤，同时保持低延迟。

【判断逻辑】
• D：prompt safety classification 与 PII detection/redaction 并行，toxicity detection 覆盖冒犯内容；并行路径降低前处理总时延，且 PII 明确编辑。

【为什么不是其他选项】
A. 只检测 PII 不编辑，不能保护隐私。
B. 自定义 FM 分类器和“通过后才查 PII”增加运维且会遗漏被前级过滤的隐私处理。
C. 串行执行并把标记内容再送 EventBridge 人审，不符合所有预处理快速完成的目标。
D. 正确选项。

【最终结论】D 用并行、编辑式的预处理同时覆盖三类风险和延迟要求。"""),
92: ("D", """【题干关键词】
• S3 新数据文件触发持续训练和重新部署；已有 SageMaker 基础设施；需要可靠的端到端 MLOps。

【判断逻辑】
• D：Standard Step Functions 可接收上传触发后的处理、按状态顺序启动 SageMaker Pipeline，并保存长时间训练/部署的可观察状态。

【为什么不是其他选项】
A. Glue ETL 和实时 endpoint 调用不构成训练/部署流水线。
B. Webhook、Lambda、EventBridge 多余且把训练编排分散；没有清晰的失败/顺序控制。
C. Express workflow 和 Autopilot 不适合承载完整、可审计的持续训练部署流程。
D. 正确选项。

【最终结论】D 用 Standard 工作流编排触发、训练和 Pipeline 部署，最符合持续 MLOps。"""),
103: ("B", """【题干关键词】
• 欧洲/北美低延迟、欧洲数据留在 EU、区域配额尖峰时弹性、最低运营复杂度。

【判断逻辑】
• B：EU 和 US 地理 CRI profiles 在相应地理边界内自动选取可用区域、提高吞吐并吸收突发；分别 API Gateway 入口保持就近访问。

【为什么不是其他选项】
A. 自建路由和告警不能自动吸收模型区域配额尖峰。
B. 正确选项。
C. 自建 Lambda 重试/跨区选路，既更复杂也容易误跨驻留边界。
D. 多区预置吞吐和应用级故障转移成本、复杂度高，且需自行防止跨地域切换。

【最终结论】B 把地域驻留、韧性和低运维交给 Bedrock 的地理 CRI profile。"""),
105: ("C+D", """【题干关键词】
• 多应用、多模型的 token 实时可见性、阈值告警，以及面向不同利益相关者的仪表盘。

【判断逻辑】
• C：CloudWatch 原生 Bedrock token/invocation metrics 加自定义仪表盘和告警，满足实时监控与报警。
• D：Bedrock 的 zero-ETL 到 Managed Grafana 提供跨模型趋势与多受众仪表盘，免自建日志管道。

【为什么不是其他选项】
A. QuickSight 适合分析报表，但不是 CloudWatch 原生实时告警的最直接路径。
B. Logs Insights 查询适合排障归因，需维护查询且不如指标告警直接。
C. 正确选项。
D. 正确选项。
E. EventBridge、Firehose、OpenSearch 组成自建数据管道，明显增加运维。

【最终结论】C 覆盖实时指标与告警，D 覆盖托管多受众可视化，是最低运维组合。"""),
107: ("B", """【题干关键词】
• 欧洲/北美低延迟、EU 驻留、区域限额突发、最少自定义故障转移。

【判断逻辑】
• B：地理 CRI inference profile 在 EU 或 US 边界内自动路由到可用区域，扩大吞吐而不需要应用自行跨区选路。

【为什么不是其他选项】
A. 自建路由只能监测，不能获得 profile 的自动容量分配。
B. 正确选项。
C. 自建重试和智能路由运维复杂，且更容易出现驻留配置错误。
D. 多区预置吞吐和代码故障转移成本高，仍需自行控制地域边界。

【最终结论】B 是同时满足地理驻留、弹性和低复杂度的原生路径。"""),
109: ("A", """【题干关键词】
• AppSync 同步 Lambda resolver 在复杂 RAG 问题上超时；要改善用户体验而保留 GraphQL/Amplify 架构。

【判断逻辑】
• A：Amplify AI Kit 支持在现有 Amplify/AppSync 客户端模式中处理流式 AI 响应与渲染，直接降低等待首段结果的时间。

【为什么不是其他选项】
A. 正确选项。
B. 延长同步 Lambda 超时只延后失败，不能降低用户等待。
C. SQS 轮询把交互改为异步队列，会进一步增加实时问答延迟。
D. 改为 InvokeModelWithResponseStream 丢掉 RetrieveAndGenerate 的知识库检索，并引入 API Gateway WebSocket 平行架构。

【最终结论】A 在保留现有 Amplify/AppSync 体系的前提下引入流式体验，改动最小。"""),
112: ("B+D", """【题干关键词】
• S3 新 MP3 文件触发；先转写，再以 JSON 输出摘要和情感；尽量少写自定义代码。

【判断逻辑】
• B：Step Functions 直接编排 Transcribe、等待完成和 Bedrock 模型调用，可要求 JSON 结构化输出。
• D：S3 Object Created 经 EventBridge 触发状态机，形成事件驱动入口。

【为什么不是其他选项】
A. Lambda 处理文本不是必要步骤，增加代码和运维。
B. 正确选项。
C. Lambda 仅为创建 prompt，也是不必要的自定义层。
D. 正确选项。
E. 直接 S3 通知到 Step Functions 的描述缺少 EventBridge/支持的事件路由配置；D 是标准解耦入口。

【最终结论】B+D 以托管事件和服务集成完成音频到结构化分析的完整流程。"""),
118: ("D", """【题干关键词】
• 关联技术指标与外部业务指标；技术劣化时自动通知；要求全面统一视图。

【判断逻辑】
• D：业务指标导入 CloudWatch 后，单一 CloudWatch dashboard 展示两类指标；异常检测与 composite alarm 可在相关运营异常时通过 SNS 通知。

【为什么不是其他选项】
A. 复合告警可组合指标，但没有异常检测，对基线变化的识别较弱。
B. Grafana 可视化强，但引入 Lambda 自动修复并非题干需求，额外增加运维。
C. 指标流到 S3 再 QuickSight 有分析价值，但实时告警链路更长、组件更多。
D. 正确选项。

【最终结论】D 用 CloudWatch 的统一指标、异常检测和复合告警最直接关联业务与技术结果。"""),
}

path = Path('data/solutions.json')
solutions = json.loads(path.read_text(encoding='utf-8'))
by_id = {item['id']: item for item in solutions}
if set(updates) - set(by_id):
    raise ValueError('Missing solution IDs')
for question_id, (answer, explanation) in updates.items():
    by_id[question_id]['answer'] = answer
    by_id[question_id]['explanationZh'] = explanation
    by_id[question_id]['needsConfirmation'] = False
path.write_text(json.dumps(solutions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Updated {len(updates)} confirmed site answers: {sorted(updates)}')
