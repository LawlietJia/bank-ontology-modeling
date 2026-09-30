# bank-ontology-modeling

银行业务本体建模 Agent Skill：从银行制度、需求、流程、产品文档、数据字典、DDL 和表结构出发，开展业务本体建模、评审与维护。也适用于 FIBO 对齐、Palantir 式决策与操作建模、指定交付物反推，以及 Word/Excel 修订接续。

## 能力

- 方法论：三类模型（共享概念 / 领域 / 场景）+ 双循环 + 五入口（文档提取、表结构分析、FIBO 复用、决策反推、标准数字化）
- 本地 Python CLI（`scripts/ontology.py`）：ingest 解析 → validate 校验 → export 交付（业务说明书 / Excel 台账 / 可编辑图 / 结构化模型）→ 修订合并回读（Excel/Word 三方合并）
- FIBO 离线参考：固定 [edmcouncil/fibo](https://github.com/edmcouncil/fibo) master_2026Q2 快照 + SQLite 索引，先检索后核对，只有确认存在的 IRI 才可写入映射
- GB/T 48000.3 第 5/7/9 章作为对标基线
- OWL/Turtle + SHACL 仅作可选单向形式化投影，不涉及图数据库查询与 GraphRAG

治理立场：脚本不裁决业务语义，人类评审不可替代，未知如实声明。

## 🎥 视频介绍

3 分半钟了解这个 skill 解决什么问题、方法论与实机演示（一条命令解析 → 校验 → 全套交付物）：

**[docs/video-intro-720p.mp4](docs/video-intro-720p.mp4)**（720p 嵌入版；B站高清版链接发布后回填）

> 视频 02:35 处口径说明：FIBO 标准文件因版权原因**不随仓库分发**，获取与本地索引重建方式见下文「FIBO 离线参考包（不入库）」一节。

## 安装

```bash
git clone https://github.com/LawlietJia/bank-ontology-modeling.git
cd bank-ontology-modeling
pip install -r requirements.txt
```

放入 Claude Code 项目的 `.claude/skills/` 下即可被识别（其他 runtime 放对应 skills 目录）。

## FIBO 离线参考包（不入库）

`references/fibo/` 下的 `source/`（FIBO 全仓快照，约 75MB）、`dependencies/`（外部机器文件）与 `index.sqlite`（约 19MB）**不随仓库分发**，原因：体积与再分发许可（OMG 规范文件不可当作 MIT 内容再分发）。

仓库保留完整元数据用于重建与校验：

- `upstream.json` — 上游 repo / tag / commit / archive sha256
- `manifest.json` — 全量文件 sha256 清单
- `dependency-sources.json` / `dependency-licenses.json` — 外部依赖来源与许可
- `coverage.json` / `DEPENDENCIES.md` — 覆盖率与依赖说明

重建：按 `upstream.json` 固定的 commit 获取 FIBO 快照放入 `references/fibo/source/`（外部依赖按 `dependency-sources.json` 获取，放入 `dependencies/`），再执行：

```bash
python3 scripts/ontology.py fibo-build --root references/fibo   # 重建 index.sqlite
python3 scripts/ontology.py fibo-verify --root references/fibo  # 完整性校验
```

详细使用与升级规程见 [references/fibo-use.md](references/fibo-use.md)。

## 命令速览

```bash
python3 scripts/ontology.py --help
# ingest / validate / export / review-workbook / word-opinions / merge
# fibo-search / fibo-describe / fibo-build / fibo-verify
```

工具细节见 [references/tools.md](references/tools.md)，方法论见 [references/methodology.md](references/methodology.md)。

## 许可

- 本仓库自有内容：未声明开源许可，保留所有权利。
- FIBO 上游内容（重建使用时）：遵循 EDM Council 原始许可（MIT），见其仓库 LICENSE；OMG 规范文件另有许可，不可作为 MIT 内容再分发。
