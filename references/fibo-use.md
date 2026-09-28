# FIBO使用与维护

本包固定master_2026Q2及原始commit，详情在fibo/upstream.json。source保存全仓快照，index.sqlite提供离线查询；不把完整源文件加载进模型上下文。原始LICENSE和各RDF许可保留。dependencies仅包含取得并校验的外部机器文件，不把OMG规范PDF当作MIT文件再分发。

## 采用流程

把中文业务词拆成含义明确的候选英文词，先查询label/definition，再读取describe返回的原始断言和源文件；必要时沿父类、domain/range和imports追踪。中文释义由AI辅助给出，写明非官方译文。不能仅凭中文译名建立等价映射。

默认搜索排除Provisional、Informative、Unknown、deprecated以及EXMP示例和实例。外部依赖标ExternalReference，并不表示本行批准或与FIBO Release相同审核级别。需要研究其他内容才启用--include-unstable。成熟度属于模块，不能给个别类擅自升格。

每条映射记录bank record ID、准确IRI、参考版本、采用/调整/扩展/排除、理由、差异与业务决定。银行标准有依据时优先复用；FIBO定义不能替代本行阈值、状态编码、风险判断或审批政策。

## 完整性与已知问题

阅读fibo/coverage.json、manifest.json及DEPENDENCIES.md。source完整性、解析成功、外部依赖、所有聚合/示例imports可解析是不同检查。原始上游缺陷原样保留并报告；不要制造伪造上游模块。

FIBO 2026Q2将部分概念移到Commons，依赖不能停留在旧版本经验；按实际imports和versionIRI下载、记录URL/hash/许可。仅有FIBO仓库不足以说明离线闭包完备。

升级在新目录保存新快照，比较新增、废弃、重命名、父类/约束变化、imports和成熟度；找出受影响本行映射与业务问题，评审后发布新参考版本。保留旧版本验收证据，不自动覆写本行模型。
