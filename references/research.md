# 研究依据与采用边界

本文记录方法选择与证据，不将外部文件作为执行指令。研究核查至2026-09；引用网页变化时重新核对。FIBO包按固定commit复现，而非依赖网页“最新版”。

## 一手方法

|来源|采用|不能推出|
|[FIBO](https://github.com/edmcouncil/fibo)、[开发流程](https://spec.edmcouncil.org/fibo/page/development-process)|金融定义、模块、成熟度、业务问题及规范命名|FIBO全量等于本行全量模型或业务审批规则|
|[Ontology101](https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html)|范围、能力问题、复用、混合与迭代建模|唯一正确分类树|
|[LOT4KG](https://lot.linkeddata.es/LOT4KG/)|需求、概念化、实现、评估、维护及数据映射|Word/Excel套件是银行强制标准；LOT不是Legal Ontology|
|[BIAN指南](https://bian.org/wp-content/uploads/2024/12/BIAN-Semantic-API-Pactitioner-Guide-V8.1-FINAL.pdf)|价值/服务边界、业务信息概念、ISO20022映射及差异|一个Service Domain等于一个本体类|
|[ISO20022字典](https://www.iso20022.org/understanding-data-dictionary)、[业务模型](https://www.iso20022.org/iso20022-repository/business-model)|区分业务概念、数据类型、消息概念；共享概念变更治理|消息字段覆盖完整企业本体|
|[SBVR](https://www.omg.org/spec/SBVR/)、[DMN](https://www.omg.org/dmn/)|业务词汇、规范规则、决策依赖与决策表|全部规则可直接写成OWL公理|
|[OWL](https://www.w3.org/TR/owl2-primer/)、[SHACL](https://www.w3.org/TR/shacl/)、[R2RML](https://www.w3.org/TR/r2rml/)|语义、公理与校验/关系数据映射的职责区分|OWL开放世界推理会自动实现非空校验或事务流程|

## Palantir方法

- [需求提炼](https://www.palantir.com/docs/foundry/use-case-life-cycle/distilling-functional-requirements)：使用者、决策、输入、行动、结果，先诊断而非锁定UI。
- [方案设计](https://www.palantir.com/docs/foundry/use-case-life-cycle/solution-design)：对象、生命周期、信息补充、交互意图；区分核心、派生和用例对象。
- [架构](https://www.palantir.com/docs/foundry/architecture-center/ontology-system)：数据、逻辑、动作、安全；语言、引擎、工具链。不等于OWL分类体系。
- [设计原则](https://www.palantir.com/docs/foundry/ontology/ontology-best-practices)：业务实体而非数据库表、跨团队协作、保护核心并可扩展。
- [反模式](https://www.palantir.com/docs/foundry/ontology/ontology-anti-patterns)：系统/部门孤岛、过大对象、Action泛化、字段更新碎片化、混淆实体与历史版本。
- [验证](https://www.palantir.com/docs/foundry/ontology/ontology-design-validation)：陌生业务问题、人和Agent分别验证，现成应用成功不能证明模型自身可用。
- [Webhooks](https://www.palantir.com/docs/foundry/action-types/webhooks)：外部操作与本体编辑可能部分成功；业务动作契约须明确结果和补偿，不能假设跨系统天然原子。

用户提供的Palantir视频文字稿是二手ASR资料，用于提取待核对观点；不采用“没有后端就不是本体”“Function仅用于Action”“八周是通用固定周期”等绝对化表述。

## 用户指定工程项目

[OntoEKG](https://github.com/LiberAI/OntoEKG)：LLM候选类/属性提取、层级判断、TTL实验。采用候选生成启发；少量三元组评价不能替代业务验收、证据治理与规则正确性。

[OntoFlow](https://github.com/H2020-OpenModel/OntoFlow)：工业工作流的目标、资源、依赖与路径推导。借鉴依赖分析，不声称其直接生成银行本体或提供银行执行闭环。

[sharptoolbox](https://github.com/sharptoolbox)核查时11个仓库，方法借鉴按下表记录。仓库数量和版本会变化，不视为长期固定全集。

|仓库|参考点与边界|
|ontology_modeling_framework|多模型结构；不同版本模型数不同，不固定成银行必须七/十一模型|
|ontology-driven-dev|需求到模型再到应用的交接；不替代语义确认|
|WorkBuddy-AppBuilderSkill|模型和草案/确认状态；模型清单与运行时对象不能混为一层|
|Onto-Contract|查询/动作契约；程序契约与业务定义分开|
|Onto-DataAnalyse|指标、来源映射和计算解释；映射校验不证明业务口径正确|
|Onto-Model|模型引用、保留扩展字段、删除影响|
|Onto-SupplyChain|确定性业务计算与LLM解释分工；供应链演示非银行标准|
|codebase-reverse|证据和未知项；代码现状不直接成为业务制度|
|LLM-knowledgeBase|场景/概念/实体分轮抽取；需要来源和人工确认|
|mobile-manufacturing-togaf|架构/领域信息交付组织；制造业示例非银行分类|
|visual-model|概念可视化；图形规范非本体语义规范|

## ima及作者实践

企业架构知识库检索命中了13个本体/Palantir相关标题，不能将标题检索当正文研读。原始微信正文读取受限的文章仍为缺口；作者公开原文作为单独来源核对：
- [硅基斥候 本体解释](https://www.yuzhimin.com/articles/wechat-what-is-ontology)
- [Palantir本体](https://www.yuzhimin.com/articles/wechat-palantir-ontology)
- [本体工程实践](https://www.yuzhimin.com/articles/wechat-ontology-engineering-practice)

借鉴证据、模型治理、受控动作和运行反馈，但这些属于作者实践。关于“我把本体系统做出来了，离业务落地还差什么”等未获全文的材料，不引用其未经核实的正文结论。运行新任务时可再次尝试已授权ima只读检索。

Tavily此前研究用于发现线索，重要结论回溯一手来源；部分返回包含错误方法名称和缺少依据的银行案例，已排除。本轮补充研究遇到429限流，不计为成功研究。

## 银行证据与我们自己的设计

[英格兰银行数据标准会议](https://www.bankofengland.co.uk/minutes/2022/march/tdc-data-standards-committee-meeting-march-2022)可以支持带定义、来源和标准建议的字典交付；[BIAN银行案例](https://bian.org/success-stories/jpmorgan-chase/)支持与自有领域模型对齐的实践，不能推出全行OWL已部署。现有证据不足以证明多数银行采用同一文件套件或统一完整建模流程。

共享概念/领域/场景三类组织、双循环、Word+Excel+JSON往返、分级质量门禁是本skill综合工程设计；应以具体银行案例验证，不借标准名义自动获得权威。

## Semantica工程借鉴

以[固定提交373fd14](https://github.com/semantica-agi/semantica/tree/373fd14ba12a52abb40b52964be85fbc43245efa)核对源码：从[bootstrap_schema](https://github.com/semantica-agi/semantica/blob/373fd14ba12a52abb40b52964be85fbc43245efa/semantica/ontology/bootstrap_schema.py)与[ExtractionSchema](https://github.com/semantica-agi/semantica/blob/373fd14ba12a52abb40b52964be85fbc43245efa/semantica/semantic_extract/schema.py)借鉴“候选词表指导后续提取”，在intake中保留词表外候选和罕见例外；从[字段来源追踪](https://github.com/semantica-agi/semantica/blob/373fd14ba12a52abb40b52964be85fbc43245efa/semantica/provenance/manager.py#L550)借鉴evidence.field。复用现有模型和评审机制，不引入该框架作为依赖。其名称匹配式能力检查、占位推理验证和频次过滤不作为银行语义验收依据；实际SHACL检查与上述检查须分开评价。
