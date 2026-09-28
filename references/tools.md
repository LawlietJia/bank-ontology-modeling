# 本地工具

在skill根目录使用Python 3.10+。需要的包见requirements.txt；在隔离环境安装，不改系统Python。Codex桌面优先使用workspace dependency loader返回的Python/Node。缺失包安装在任务独立目录后用PYTHONPATH指定；OCR需要本地pdftoppm、tesseract及中文语言包。

Excel优先使用桌面提供的artifact-tool；ONTOLOGY_NODE和ONTOLOGY_NODE_MODULES可指定加载器返回的路径。没有该库的环境才使用openpyxl备用生成；回读始终本地进行。Word使用python-docx，Draw.io使用可编辑XML，不依赖在线服务。

```bash
python3 scripts/ontology.py ingest input.docx --out run/source.json
python3 scripts/ontology.py ingest schema.sql --dialect postgres --out run/schema.json
python3 scripts/ontology.py ingest scan.pdf --ocr --out run/scan.json
python3 scripts/ontology.py validate run/model.json --out run/check.json
python3 scripts/ontology.py export run/model.json --out run/delivery-v1
python3 scripts/ontology.py review-workbook edited.xlsx --current run/model.json --out run/proposal.json
python3 scripts/ontology.py word-opinions reviewed.docx --out run/opinions.json
python3 scripts/ontology.py merge run/model.json run/proposal.json --decisions run/choices.json --version 0.2 --out run/model-v02.json
python3 scripts/ontology.py fibo-search 'Loan'
python3 scripts/ontology.py fibo-describe '已检索核实的完整IRI'
python3 scripts/ontology.py fibo-verify
```

ingest只生成证据块；下一步由AI阅读、分析、提问及填写model.json。CLI不使用在线LLM，不自动建本体、不批准模型、不执行源SQL或业务动作。退出码0表示工具检查正常，1表示检查失败，2表示输入或运行错误。

支持schema_version 1.0/1.1；新任务用1.1。信息单元、语义元数据与约束字段见semantic-records.md，合成示例见assets/semantic-example.json。validate检查结构、证据和约束规格，不运行政策或SHACL；export在validation.json中单列这些未执行状态，不提供国标认证。

输出路径不覆盖已有成果。export要求目标目录尚不存在，已有空目录也拒绝；完整生成并检查后才发布，异常清理本次临时产物，可使用原目标路径重试。相对证据路径以model.json所在目录为准；导出目录若移动，请保持证据相对路径有效或改为新的授权路径。检查结果中的warning不能在发布时自动忽略。

Word批注/修订回读是结构化意见，不会自动理解意见或修改模型。XLS旧格式、加密Office、复杂PDF阅读顺序和图片表格需要转换/视觉复核；公式缓存不是实时计算；数据库方言未覆盖的语句原文保留，补充分析。

Office交付必须渲染后复核。若macOS的无界面LibreOffice中文变成空白或方框，先检查字体是否被渲染器发现；可在任务目录创建Fontconfig配置，通过FONTCONFIG_FILE为该次渲染指定系统中文字体目录及可写临时缓存。不要修改运行时或系统字体目录，也不要以没有中文的预览宣布验收通过。

fibo-build仅用于维护参考包索引，重建前备份参考包。fibo-verify区分文件完整性和导入完整性；已知上游导入缺陷必须披露，不能用空文件消除错误。
