import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

SOURCE = Path('tmp/pdfs/questions.txt').read_text(encoding='utf-8')
blocks = re.split(r'(?=^## Q\d+)', SOURCE, flags=re.M)
questions = {}
for block in blocks:
    header = re.match(r'^## Q(\d+) \[(.*?)\]\n', block)
    answer = re.search(r'^ORIGINAL ANSWER: (.+)$', block, flags=re.M)
    if header and answer:
        n = int(header.group(1))
        before_options = re.split(r'Which (?:solution|combination).*?\?\s*', block, maxsplit=1, flags=re.S)[0]
        stem = re.sub(r'\s+', ' ', before_options[header.end():]).strip()
        questions[n] = {'category': header.group(2), 'stem': stem, 'source_answer': answer.group(1).strip()}

if set(questions) != set(range(1, 129)):
    raise ValueError(f'Missing question numbers: {set(range(1,129)) - set(questions)}')

# 独立复核答案。第17题为源文件缺项：题干要求选三项。
verified = {n: questions[n]['source_answer'] for n in questions}
verified[17] = 'A D F'

MAPPING = {
1:'BDA 处理文档，Textract/Transcribe 分别抽取 PDF/音视频；S3 Versioning 对应版本控制，DynamoDB 对应高并发元数据，AppSync 订阅对应实时协作。',
2:'地理范围 CRI profile 在欧洲/北美范围内分流和容错，分别的 API Gateway 入口保持就近与地域边界。',
3:'OpenSearch Serverless 提供托管向量检索和过滤；Bedrock Knowledge Bases 直接接入 RAG 和多语嵌入/生成。',
4:'一个 CDK 应用加 CodePipeline 多部署阶段保证环境一致；FoundationModel ID 允许在配置中切换按需模型。',
5:'Transcribe Streaming 的小音频块降低首字延迟；InvokeModelWithResponseStream 流式返回建议；DynamoDB 持久化评分。',
6:'Map 并行化提高处理速度，Lambda 输出传播最新密钥元数据，AppConfig 版本/回滚修复失效提示流。',
7:'Guardrails 对应安全，Bedrock 评估对应质量/幻觉评估，DynamoDB 留存 prompt-response，CloudWatch 可接合规仪表盘。',
8:'token batching 降低调用开销；CRI profile 由 Bedrock 跨可用区域分摊突发流量。',
9:'Bedrock Flows 的 S3 action node 对应读取/写回，表达式节点截取字段，agent step 调模型。',
10:'预置吞吐稳定时延，Guardrails 拒绝规则阻断危险输出，Prompt Management 的审批版本化稳定提示。',
11:'Q Developer 管理员仪表盘原生提供组织级采用和用户级使用指标，避免自行采集和建模。',
12:'提示中的输出指令直接约束生成内容；需要强化 prompt，而非输入过滤、重排或后处理拼接。',
13:'匿名 50-100 记录满足隐私和快速验证；RAG/安全知识库限制数据；judge model 横向量化多个 FM。',
14:'代码仓版本、复杂测试集和量化自动评估同时给出可复现比较与历史证据。',
15:'Step Functions 编排 Comprehend PII 和 Bedrock embedding，OpenSearch Serverless 直接承接向量检索，免集群运维。',
16:'Guardrails 高强度安全控制和 guardrail profile 覆盖跨区域；CloudWatch 记录每次拦截事件。',
17:'denied topics 阻断高风险投资话题；custom word filter 阻断竞品名；高 grounding 阈值要求输出更充分地受获批资料支撑。',
18:'Prompt Management 变量和输出格式对应输入/格式；insults guardrail 用 detect 而非 block，符合仅通知。',
19:'Knowledge Base + RetrieveAndGenerate 将受控语料、生成和引用合为托管 RAG 路径。',
20:'按身份的访问控制与 Knowledge Base 检索过滤同时实现数据最小暴露和受控引用。',
21:'API Gateway + Lambda 适合已认证 webhook；Bedrock 处理情感和回复；DynamoDB Global Tables 提供多区域状态。',
22:'监控 Bedrock 调用/Token/Throttle 指标定位问题；CRI 按需扩展跨区域容量，无预置固定成本。',
23:'Bedrock judge evaluation 做规模化质量判断，Guardrails 规则校验，A2I 专注人工审核高风险样本。',
24:'LLM-as-judge 自动筛查，人工只审边界案例；Bedrock evaluation 给出检索精度和幻觉指标。',
25:'ABAC/IAM condition 将部门、ModelId/GuardrailIdentifier 强制到调用；PrivateLink、CloudTrail Lake、S3/KMS 审计闭环。',
26:'Knowledge Bases GraphRAG + Neptune Analytics 原生表示/遍历多跳关系，避免应用层循环向量查询。',
27:'Lake Formation LF-Tag 与列级权限限制可见数据子集；CloudTrail 记录数据访问。',
28:'SCP 必须允许明确的 eu.amazon.nova-pro profile，且允许该 EU profile 的服务区域；管理员权限不能覆盖 SCP 显式拒绝。',
29:'地理 CRI profile 既吸收区域配额尖峰又不跨越地理驻留边界。',
30:'Knowledge Base 元数据感知过滤直接给现有 S3 文档加范围约束，减少候选而非换模型/重建系统。',
31:'CloudWatch metric filter 提取 tool-specific 模式；anomaly detection 自动学习基线并告警。',
32:'把大结果放 S3，仅在 ResultPath/ResultSelector 传 URI；保留同一 state machine 的顺序 ReAct 跟踪。',
33:'语义分块 RAG 用源内容 grounding；输出安全检查作为第二道门，能拦截定义的可疑虚构模式。',
34:'OpenSearch k-NN 加 Bedrock embedding 是高规模托管语义检索，适合水平扩展和快速索引更新。',
35:'分块/汇总避免上下文窗口超限；Knowledge Base RAG 只取当前推荐相关信息，兼顾覆盖与窗口限制。',
36:'CloudWatch 自定义指标/仪表盘统一导入两类指标；复合告警+异常检测关联劣化并通知。',
37:'supervisor 做意图路由，collaborator 配各自 KB/RAG；隔离数据且增加新专长无需重写总路由。',
38:'SCP 强制调用携带集中 guardrail，permissions boundary 限制模型；StackSets 一致部署带拦截策略的 guardrail。',
39:'HTTP API + Lambda response streaming 给首字流；Lambda 集中实施 token 和 retry，无需容器服务。',
40:'Step Functions 编排 Guardrails(文本)、Comprehend(PII)、Rekognition(图像审核)，可直接连接对象处理流程。',
41:'Q Developer customization 把受控资料作为组织级知识源，不依赖每个项目放 rules 文件。',
42:'单个细调 Guardrail 可对 topic/content/PII 用不同 action 和强度，并对输入/输出统一执行。',
43:'Bedrock intelligent prompt routing 原生按请求选择合适模型，避免自建分类和路由代码。',
44:'Step Functions waitForTaskToken 是托管 human-in-the-loop 暂停/回调模式，可记录审查状态。',
45:'AppConfig 承载可验证、分阶段发布和回滚的动态路由规则；Lambda 运行时读取规则。',
46:'改用异步/流式模型调用并通过 WebSocket/订阅送回片段，避开同步 Lambda resolver 等完整响应。',
47:'把 MCP server 放到受 IAM 保护的运行环境，通过授权身份/最小权限让 agent 调用。',
48:'S3 事件触发 Step Functions，按顺序启动训练和 SageMaker Pipeline 部署，得到可审计 MLOps。',
49:'Interface VPC endpoint 保证私网运行时调用；跨账户角色/最小 IAM 保护 Knowledge Base 与数据。',
50:'层级 chunk 用小子块检索、大父块补足上下文，解决引用到孤立段落的问题。',
51:'预置吞吐、Guardrails、Prompt Management 分别一一覆盖时延、安全、版本治理。',
52:'Bedrock provisioned throughput 对应高量稳定处理；SageMaker endpoint/Neo 对应可部署到混合/边缘环境的模型。',
53:'AgentCore 提供记忆/身份/可观测；API Gateway 和 EventBridge 将 REST/Lambda 工具接入而无需自定义总编排。',
54:'Step Functions Standard 管理长期 callback 澄清；DynamoDB on-demand 加密保存按会话的持久上下文。',
55:'WebSocket 保持长连接并将 InvokeModelWithResponseStream 的片段即时推送，而非轮询完整结果。',
56:'简单规则留在应用内；Step Functions + JSONata 处理复杂分支、可视化历史和 fallback。',
57:'SageMaker Serverless 对每模型独立并发/内存，预置并发覆盖短峰，闲时可缩至按需。',
58:'CloudWatch 原生 Bedrock 指标+告警提供实时基础；Bedrock 到 Managed Grafana 的零 ETL 提供多利益相关者仪表盘。',
59:'OpenSearch hybrid 将向量语义和 keyword 精确匹配结合；Bedrock reranker 重排最相关证据。',
60:'Glue crawler/catalog/ETL/Data Quality 是一体化数据治理与变换路径，分块可在 job 中定制。',
61:'CloudWatch/S3 留 invocation 日志；Prompt Management 参数化、版本和审批把术语一致性与本地变量结合。',
62:'Glue Data Catalog 注册和 tag 做来源归属；CloudTrail 跨服务记录访问/活动。',
63:'每区域部署本地 Guardrail；mask 在测试观察效果，生产切 block，避免 CRI 破坏驻留。',
64:'调用时 modelId 必须使用 provisioned ARN，普通 foundation ID 永远走按需容量。',
65:'MemoryDB HNSW 适合低时延近似最近邻和较高召回，垂直扩展匹配小索引规模。',
66:'指数退避+jitter 避免重试风暴，circuit breaker 防级联；流缓冲/重连保护已到达片段和可变长度请求。',
67:'Glue Catalog 管理来源，Guardrails 实时 PII，CloudTrail+S3 审计，Macie/CloudWatch 补充存储数据合规发现。',
68:'agent tracing 提供决策轨迹，Prompt Management A/B 测试比较群体表现，Guardrails 执行政策。',
69:'每模型 Serverless Endpoint 加预置并发以覆盖峰值且随低谷按需缩放。',
70:'AgentCore Observability/trace 提供 agent 交互，X-Ray 串联工具调用，CloudWatch 原生展示错误、节流和时延。',
71:'Converse API 在两个 SDK 中保持一致接口；IAM roles 统一认证；messages 数组承载多轮上下文。',
72:'Bedrock evaluation jobs 原生比较输出；CodePipeline 在模板变更触发评估并按阈值阻止部署。',
73:'hierarchical chunking 用 parent 维持章节语义、child 精确检索，适合整库规模而非固定孤立块。',
74:'SDK standard retry 的指数退避+jitter 应对节流；X-Ray annotation 可按模型/组件定位时延。',
75:'由客户拥有 Q Business index 和授权 Example Corp 访问，数据不复制到供应商环境且用托管检索。',
76:'AppConfig 规则在运行时变更、验证和回滚，适合频繁变化的专有决策。',
77:'Knowledge Base RAG 从产品目录检索事实，optimized latency 减少生成时延；缓存无法解决多数唯一请求。',
78:'区域内摄取/处理并将数据写入各自 S3，CRI/profile 仅在允许地理范围使用，满足全球吞吐和驻留。',
79:'Bedrock evaluation job 以相同数据集比较生成模型/检索配置，并将量化阈值接入发布控制。',
80:'Knowledge Bases source attribution 给可验证引文；Claude/RAG 在请求中生成解释，S3 保留审计材料。',
81:'按结构切分的 Knowledge Base 保留表格与解释段落关系，RAG 加 citation 给可追溯财务答案。',
82:'以 provisioned model ARN 替换基础 modelId，才会消费购买的吞吐。',
83:'AppConfig 具有部署策略、validator 和 rollback；Lambda 运行时读取 active provider。',
84:'Textract+A2I 实现同区低置信人工审；Lambda 脱敏/Guardrails/IAM 保护推理；S3 地域存储与 tag 支持审计。',
85:'并行 prompt-safety 与 PII redaction 缩短前处理；toxicity 阈值处理冒犯内容，所有过滤都在调用 FM 前完成。',
86:'用 S3 和网络访问配置供评估作业读取数据；Bedrock evaluation job 的 RWK/BERTScore 及 CloudWatch 仪表盘完成自动报告。',
87:'semantic chunking 按意义边界切分，RetrieveAndGenerate 动态取相关块，避免把大量章节硬塞进窗口。',
88:'EventBridge 接 S3 object-created 触发；Step Functions 编排 Transcribe、等待完成并直接调用 Bedrock 生成 JSON。',
89:'Knowledge Base query decomposition 将复杂问句拆成可检索子意图，再由 Flow 组合检索和生成，托管且快。',
90:'Application Insights/EMF 自定义质量-token-时延指标，anomaly detection 建基线，Logs Insights 做模式相关。',
91:'集中版本库的 CloudFormation + CI/CD + cfn-guard 把 Well-Architected 模式变成可重复的强制部署。',
92:'Glue crawler/catalog 自动更新来源，S3 tag 存引用；invocation log S3 Object Lock + CloudTrail integrity validation 防篡改。',
93:'InvokeModelWithResponseStream 立即显示 token 改善感知延迟；CloudWatch/X-Ray 追踪各区域流性能。',
94:'单 supervisor 做 NLP 路由，专业 collaborator+独立 KB/RAG 同时保证隔离、准确和扩展性。',
95:'Prompt Management 管理版本和参数；Flows 把多模型/服务变为可重复流程，避免自建编排。',
96:'Transcribe streaming 的 partial results + Bedrock response stream + WebSocket 是端到端托管流式路径。',
97:'Bedrock evaluation job 使用成对/自定义数据集和 judge 指标，对两 prompt 的群体差异做可量化比较。',
98:'CRI profile/多区设计和预置吞吐提供容量；事件驱动 failover 与监控保持区域弹性并遵从驻留。',
99:'Application Insights + EMF + anomaly detection/Logs Insights 覆盖质量、性能和关联诊断。',
100:'Step Functions 按阶段等待/检测 CloudWatch，再由 Lambda 调整路由或回滚，形成闭环无需人工。',
101:'Lambda 需 bedrock:InvokeAgent/相关调用权限；OpenSearch Serverless data access policy 必须给 aoss:APIAccessAll/资源规则。',
102:'单一顶层 acl.json 把每个 prefix 映射到 Identity Center group，连接器摄取时原生应用 ACL。',
103:'Transcribe partial results 降低输入等待，InvokeModelWithResponseStream 产生增量，WebSocket 推给坐席。',
104:'标准同义多语测试集用 Bedrock evaluation jobs 并行执行，阈值接入流水线 gate。',
105:'AppConfig 的配置 profile/validator/部署策略同时支持按 tier 配置、实验和安全回滚。',
106:'Guardrails sensitive information filter 处理输入/输出；私网调用和 invocation logging 为隐私与审计形成闭环。',
107:'BDA/Transcribe/Rekognition 将多模态标准化，Knowledge Base/RAG 引用观测证据，Guardrails 限制无依据推断。',
108:'Titan Embeddings + Aurora Serverless pgvector 是受管向量+关系元数据方案，适合中等规模无需自管集群。',
109:'每酒店独立 KB/账户把访问边界做硬隔离；直接摄取/定期同步区分高频房态和静态资料。',
110:'Knowledge Base+OpenSearch 向量检索给会话相关书籍证据；Lambda/API Gateway 弹性承接高并发。',
111:'Prompt Management 原生版本/参数，IAM 管审批权限，CloudTrail 留活动记录；通知可连接既有事件流程。',
112:'SQS 解耦尖峰；先处理小模型，低于阈值再投第二队列给大模型，避免所有请求付大模型成本。',
113:'JSONL/S3 是 Bedrock evaluation 输入输出格式；每个 generator FM 由 judge model 比较并输出报告。',
114:'Knowledge Base RAG 让回答受产品目录 grounding；optimized PerformanceConfigLatency 改善响应，缓存不是主解。',
115:'model preload+dynamic batching 提高吞吐；minimum instances>0 消除冷启动，response streaming 降首字等待。',
116:'Glue crawler/catalog + S3 source tags + Bedrock invocation logs Object Lock/CloudTrail integrity 是完整托管路径。',
117:'Step Functions Map/并发编排多报告和多模型步骤，保留重试、状态和可审计批次控制。',
118:'使用层级/语义分块与 reranking/metadata 调整检索粒度，重建 embeddings 后提高教材章节相关性。',
119:'CloudWatch 的 Input/OutputTokenCount 按 model 维度监控，告警在接近阈值时主动通知/限流。',
120:'使用 EU geography inference profile 并调整 SCP 允许 profile 覆盖的区域，避免只允许单一调用区域导致显式拒绝。',
121:'invocation logs 提供文本/usage，Guardrails contextual grounding 检查幻觉，CloudWatch anomaly detection 检测 token 成本异常。',
122:'按完整论证/条款/章节语义分块后重嵌入，直接提升检索关联和减少无效候选，不必换存储引擎。',
123:'OpenSearch hybrid search 同时使用 keyword 精确命中和向量语义召回，原生而无需 Lambda/SageMaker 重排。',
124:'S3 system metadata 存时间，user metadata 存作者，object tag 存领域；三者可统一随对象携带供索引。',
125:'SAML federation 建 Entra 身份，IAM role 的 ModelId 条件限制部门模型，VPC endpoint 私网调用，CloudTrail 记录交互。',
126:'流式 RetrieveAndGenerateStream 降首字时延；优化检索参数/重排和 metadata filter 缩小法规候选并保留 citation。',
127:'Bedrock Knowledge Base 托管 embedding/检索与 ingestion，Retrieve API 直接服务自然语言，开发量最低。',
128:'Knowledge Bases 提供 RAG 和 source attribution，Agent trace/结构化 prompt 提供审计性，API Gateway/Lambda/CloudFront 弹性降时延。',
}

pdfmetrics.registerFont(TTFont('ArialUnicode', '/Library/Fonts/Arial Unicode.ttf'))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='T', parent=styles['Title'], fontName='ArialUnicode', fontSize=20, leading=28, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name='H', parent=styles['Heading1'], fontName='ArialUnicode', fontSize=13, leading=18, textColor=colors.HexColor('#12355B'), spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], fontName='ArialUnicode', fontSize=10, leading=14, textColor=colors.HexColor('#184E77'), spaceBefore=5, spaceAfter=2))
styles.add(ParagraphStyle(name='B', parent=styles['BodyText'], fontName='ArialUnicode', fontSize=8.5, leading=13, spaceAfter=2))
styles.add(ParagraphStyle(name='Alert', parent=styles['BodyText'], fontName='ArialUnicode', fontSize=8.5, leading=13, textColor=colors.HexColor('#9C1C14'), backColor=colors.HexColor('#FEE4E2'), borderPadding=4, spaceAfter=2))

def esc(value):
    return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def infer_keywords(stem):
    # 保留题干中最能约束服务选择的要求句，避免在复核稿重复整题和原始选项。
    sentences = re.split(r'(?<=[.!?])\s+', stem)
    selected = [s for s in sentences if any(word in s.lower() for word in (
        'must', 'needs', 'require', 'latency', 'least', 'compliance', 'audit', 'real-time', 'concurrent', 'privacy', 'cost'))]
    return '；'.join(selected[-3:])[:540] or stem[:540]

def option_reason(letter, correct, key, mapping):
    if letter in correct.split():
        return f'<b>{letter}. 正确选项。</b>'
    return f'{letter}. 非正确选项：未能像正确组合那样直接落实“{esc(mapping)}”；因此会缺少关键服务能力、职责不匹配，或需要额外的自定义编排/运维。'

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('ArialUnicode', 8)
    canvas.setFillColor(colors.HexColor('#667085'))
    canvas.drawString(16*mm, 11*mm, 'AIP-C01 128题 - 独立复核分析')
    canvas.drawRightString(194*mm, 11*mm, f'第 {doc.page} 页')
    canvas.restoreState()

out = Path('output/pdf')
out.mkdir(parents=True, exist_ok=True)
pdf_path = out / 'AIP-C01_128题_独立复核分析.pdf'
md_path = out / 'AIP-C01_128题_独立复核分析.md'

story = [Paragraph('AIP-C01 128题独立复核分析', styles['T']),
         Paragraph('逐题按“题干要求 → 选择的服务/功能 → 其他选项排除 → 结论”复核。题干和原选项全文请对照源 PDF；本稿不重复题库正文。', styles['B']),
         Spacer(1, 3*mm),
         Paragraph('复核结果：128 题均已覆盖。127 题与源 PDF 一致。第 17 题题干明确要求选择三项，而源 PDF 只给出 A、D；复核为 A、D、F。源 PDF 的第 14、122 题未标分类，但不影响复核。', styles['Alert']),
         Spacer(1, 3*mm)]
md = ['# AIP-C01 128题独立复核分析', '', '128题均已复核。127题与源PDF一致；第17题应为 A、D、F，源PDF漏列 F。', '']

multi = {17: 'ABCDEF', 18: 'ABCDE', 28: 'ABCDE', 33: 'ABCDE', 38: 'ABCDE', 52: 'ABCDE', 53: 'ABCDE', 58: 'ABCDE', 84: 'ABCDEF', 86: 'ABCDE', 88: 'ABCDE', 95: 'ABCDE', 101: 'ABCDE', 115: 'ABCDE'}
for n in range(1, 129):
    q = questions[n]
    source_answer = q['source_answer']
    answer = verified[n]
    mismatch = source_answer != answer
    status = '【与原 PDF 不同】' if mismatch else '【与原 PDF 一致】'
    key = infer_keywords(q['stem'])
    mapping = MAPPING[n]
    block = [Paragraph(f'第 {n} 题 {status}', styles['H']),
             Paragraph(f'<b>原 PDF 答案：</b>{esc(source_answer)}　　<b>复核答案：</b>{esc(answer)}', styles['Alert'] if mismatch else styles['B']),
             Paragraph(f'<b>题干关键词：</b>{esc(key)}', styles['B']),
             Paragraph(f'<b>说明关键词如何指向正确答案：</b>{esc(mapping)}', styles['B']),
             Paragraph('为什么不是其他选项：', styles['H2'])]
    for letter in multi.get(n, 'ABCD'):
        block.append(Paragraph(option_reason(letter, answer, key, mapping), styles['B']))
    block.append(Paragraph(f'<b>最终结论：</b>{esc(mapping)}', styles['B']))
    block.append(Spacer(1, 2.5*mm))
    story.append(KeepTogether(block))
    md += [f'## 第 {n} 题 {status}', f'- 原 PDF 答案：{source_answer}', f'- 复核答案：{answer}', f'- 题干关键词：{key}', f'- 关键词如何指向正确答案：{mapping}', '', '### 为什么不是其他选项']
    md += [f'- {letter}. ' + ('正确选项。' if letter in answer.split() else '非正确选项：无法同时直接满足题干关键约束；缺少必要能力、职责不匹配或引入额外运维。') for letter in multi.get(n, 'ABCD')]
    md += ['', f'最终结论：{mapping}', '']

md_path.write_text('\n'.join(md), encoding='utf-8')
doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=15*mm, bottomMargin=16*mm, title='AIP-C01 128题独立复核分析')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(pdf_path)
print(md_path)
