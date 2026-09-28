# 信息单元、元数据与业务约束

用于文档知识追溯和可交接的类、属性、约束台账。借鉴GB/T 48000.3—2026；普通银行材料不自动视为标准化文件，本契约不是完整国标实现。

## 文档信息单元

先保存解析块，再按完整语义组织information_unit。段落/单元格不等于信息单元：一项要求可跨多个块，一个块也可包含要求、例外和说明。evidence保留相关原文锚点，AI解释放definition，不能写成原文。

details字段：

- content：原文；unit_type：requirement/recommendation/instruction/permission/statement/definition/example/note/other。
- statement_nature：normative/fact/proposed/example/modeling_decision/unknown。要求型句子仍可能来自未批准草稿，结合来源确认性质，不能只凭“应”字判定有效规范。
- representation：字符串列表，如text/table/figure/formula；同一语义可有多种形式，不因此创建多个业务类。
- about_ids：涉及的业务记录；related_unit_ids：引用的信息单元；exception_unit_ids：限定当前要求的例外信息单元。后两项只引用information_unit。
- effective_from/effective_to：已知适用日期；未知留空并登记问题。原文保留日期写法，本契约用ISO日期。

业务规则、属性、动作等以source_unit_ids引用其依据信息单元。about_ids表示内容涉及什么，source_unit_ids表示业务定义依赖什么；不互相替代。条款及例外变化通过依赖传播到业务记录。交叉引用允许，循环继承不允许。

## 类与属性元数据

所有字段放details。1.1中concept/object/role/attribute/relation在用记录应有model_level、term_name、labels：草案缺失提示，基线缺失阻止发布。

|字段|语义|
|---|---|
|model_level|class/individual/property/statement；关系断言与关系类型、样本实例与类分开|
|term_name、labels、synonyms|规范名称；语言代码到标签的对象如{"zh":"支付指令"}；同义词字符串列表|
|iri|按命名空间治理分配的绝对IRI，与稳定ID并存；业务草案可不分配，形式交接应补齐；external_iri仍是外部参考|
|parent_ids、equivalent_ids、disjoint_ids|有依据的父类、等价类、互斥类ID列表；不适用留空，不强造等价|
|instance_of_ids|实例所属类ID列表|
|property_type|attribute用data，relation用object；属性类型记录model_level=property|
|domain_ids、range_ids|定义域类ID列表、对象属性值域类ID列表；多类表示业务允许候选集合，正式导出须明确联合或其他逻辑，不能逐项直接写多个rdfs:domain|
|datatype、allowed_values、unit|数据属性值类型、允许值、单位；数据属性不用range_ids指向类|

保留owner_id及relation的subject/object/cardinality作业务归属和交接；与域/值域须逐项核对一致。父类只放真正共享且含义一致的属性。工具检查ID存在、IRI基本形态/重复、已声明层次冲突和继承循环，不证明逻辑等价、身份正确或全世界无IRI冲突。

## 结构化业务约束

rule保留完整业务判断；constraint承载可单独评审的约束，以links连接依赖。所有目标都应出现在target_ids，不仅藏在正文或specification任意键中。

|constraint_type|specification例子|target_ids|
|---|---|---|
|unique|{"scope":"同一来源系统和有效期间内"}|组成业务键的属性；单值性另建cardinality|
|cardinality|{"min":0,"max":1}|受约束属性/关系|
|value_range|{"min":0,"min_inclusive":true}|数值属性；单位、币种、时点另记|
|enumeration|{"values":[false,true]}|属性；0与false均为有效值|
|date_order|{"operator":"le"}|恰好两个不同属性，第一项≤第二项；lt为严格早于|
|disjoint|{"rationale":"业务定义确认互斥"}|恰好两个不同类，区别于现实多角色|
|reference|{"policy":"must_exist"}|受约束关系；policy还可为allow_external/requires_resolution|
|custom|{"language":"business-text","expression":"完整业务表达"}|相关业务记录；转换和执行待技术确认|

另须condition、exceptions、unknown_handling、positive_case、negative_case，可补time_basis、verification_owner、conformance_basis、interpretation。未知例外写明待确认并登记blocking问题，不能用“无”掩盖缺口。

工具检查约束规格的结构、边界、枚举、基数及支持的操作符，不求值银行样本、不执行表达式、不运行OWL/SHACL。业务验收仍由tests的实际result/evidence记录。

## 交付与维护

Excel新增信息单元、业务约束页，原有对象/属性/关系页增加元数据列。复杂列表和对象可通过对话由AI填写，业务人员不必手写JSON；回读对新增行也显式解析结构列。

Word展示新增记录和解释。对象关系图仍聚焦业务对象，任务需要时再绘条款证据图。验证结果区分模型规格检查、政策执行、SHACL及国标符合性。

以类型化ID列表或links登记依赖。来源版本、条款/例外、元数据、约束变化后，重新评审传递依赖并重置旧测试；删除记录先处理断链。Word意见仍需语义确认，不成为自动批准。
