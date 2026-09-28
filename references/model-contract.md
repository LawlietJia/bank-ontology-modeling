# 统一业务模型契约

模型使用UTF-8 JSON，新任务schema_version为1.1，仍可读取1.0。模板见 `../assets/model-template.json`。它是内部交换和生成格式，不要求业务人员手写JSON，也不是OWL或某平台导入格式。新增信息单元/约束后使用1.1；旧项目可先保持原版本。

## 根结构

project：id、title、version、status(draft/baseline)、purpose、domains列表、application、owner。application用业务意图描述，只读语义/调查、规则决策或受控操作；混合场景说明各自边界。

sources：id、path、kind、version、sha256、blocks_path。来源kind可为制度、需求、数据字典、DDL、公开参考、访谈决定或synthetic。blocks_path可为相对model.json的路径；不将内部路径打包到对外可复用案例。

records：id、kind、name、definition、status、evidence、links、details。kind为concept/object/role/attribute/relation/event/state/rule/metric/decision/action/mapping/information_unit/constraint。status为candidate/reviewed/approved/deprecated。evidence为`[{"source_id":"S1","anchor":"P1"}]`；links为关联记录ID列表。新增细节可放details，保留未知扩展字段。

同一记录的定义、例外、时间或权限来自不同条款时，证据项可加`field`，例如`{"source_id":"S1","anchor":"P8","field":"details.exceptions"}`。field只定位本记录的name、definition或details下一个完整字段（如details.specification整体），不定位数组下标或嵌套子项；未加field仍表示记录级证据，旧模型无需迁移。重要且来源不同的字段优先细化，不机械拆分每个字段。删除或重命名字段时同步调整证据。字段定位不表示来源必然支持该值，仍需语义核对；建模建议和未知项不能借附一条来源变成原文事实。

questions：id、question、blocking布尔、status(open/resolved)、affects列表、resolution。未决问题的影响范围应具体到记录。

tests：id、question、expected、record_ids列表、result(not_run/pass/fail)、evidence。question承载能力问题，record_ids关联所用模型记录；缺关联时提示补充或在evidence说明整体检查范围。result仅允许这三个值；pass缺验证记录时草案警告、基线拒绝。evidence可用文本或含文本的对象/列表；空白、嵌套空值、纯布尔或数值不算记录。区分结构测试、样本走查、独立Agent测试和人工业务验收，不把预期答案当作实际运行证据。摘要由tests派生，不维护第二份能力问题清单。

decisions：id、status、affects列表、rationale、approved_by、approved_at。业务批准记录来自明确的业务评审或授权；AI不能虚构批准人和日期。一个决定可覆盖一组记录，认可的是对应模型语义，不代表任何修订后的验收自动通过。验收口径修订及模型含义变化的处理见 [维护回归](validation.md#维护回归)。

## 类型最低内容

|类型|details最低内容|
|object|identity身份与粒度；补充domain、classification、owner|
|attribute|owner_id、datatype；按需要补充allowed_values、unit、currency、time_basis|
|relation|subject、object、cardinality；明确方向、成立条件、时间与关系对象|
|rule|condition、expression、exceptions、unknown_handling、positive_case、negative_case|
|metric|expression、scope、unit、time_basis；币种、分母为零和缺失值另行说明|
|event|subject、trigger、time_basis；区分发生、生效和获知时间|
|decision|inputs、outputs、actor；补充规则/模型依赖与解释|
|action|actor、authorization、preconditions、effects、failure、success、idempotency；补充inputs、outputs、状态和审计|
|mapping|target、transformation、coverage；来源字段或external_iri、reference_version、alignment|
|information_unit|content、unit_type、statement_nature、representation；evidence保留来源；例外与引用使用类型化ID列表|
|constraint|constraint_type、target_ids、specification、condition、exceptions、unknown_handling、positive_case、negative_case|

subject/object/owner_id/target/state_from/state_to/decision_id和links按记录ID解析。动作引用受影响对象、规则等可用links，文本描述不能替代需要机器校验的ID。

## 发布语义

1.1类/实例/属性元数据、约束规格及类型化依赖见 [语义记录](semantic-records.md)。新增内容仍在records中，复用证据、批准和版本机制。子类及属性集可从parent_ids和domain_ids/owner_id反向生成，避免维护两份矛盾列表。

草案可含假设和缺口，结构错误必须修复。基线要求：在用记录已确认；每条有证据或批准决定；有带人员和日期的批准记录；关键问题关闭；测试通过且有证据。脚本只能检查记录条件，不能证明批准真实、业务规则正确或来源有法律效力。

示例与模拟评审永远标synthetic，不能给真实银行模型“代签”。即使结构验证通过，也需要检查能力问题覆盖、来源的权威和适用性、正反例以及语义损失。

## 技术交接

按目标追加转换约定：RDF/OWL标识及公理映射；属性图标签、关系与约束；语义检索的粒度和证据；决策表输入/输出/冲突；操作本体的对象、事件、动作及权限。只在需要时生成技术表示，并验证转换；JSON或Draw.io文件不是可直接部署的推理/业务执行系统。
