# 复现说明

从仓库根目录执行脚本。先完成 `git lfs pull`，确认原始 PDF/Word 不是几行文本的 LFS 指针。

## Python

建议 Python 3.11 或更新版本：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python scripts/extract_sources.py
.\.venv\Scripts\python scripts/build_database.py
```

`extract_sources.py` 读取原始 PDF、Word XML 和已有 Excel，输出 `tmp/extracted/`。`build_database.py` 将逐项核对的文献事实组织为数据表，输出 CSV、数据包及 `tmp/database.json`。

来源包括原木质素文件夹与“抗菌文献”。`data/source_registry.json` 固定已有F编号/路径/哈希，新文件追加新编号；原文消失或哈希改变时中止提取，不重排已有编号。`append_antibacterial.py` 保存新增全文的核对记录，在旧250条测量之后追加，以保持旧ID。

**这不是能自动理解任意新论文的通用抽取器。** `build_database.py` 中的文献事实是本次经人工语义核对后编码的记录。加入新论文时，需要同步更新来源映射、样品、测量和疑点，再核查出处。

## Excel

Node 需要能够解析 `@oai/artifact-tool`，本次使用 Codex 捆绑运行时提供的版本。该依赖没有打包进仓库。可以在 Codex 中获取其依赖路径，然后将 `scripts/node_modules` 链接到运行时提供的 `node_modules`；不要提交链接或依赖目录。

```powershell
node scripts/build_workbook.mjs
python scripts/verify_database.py
```

若没有该运行时，可以直接使用已导出的 CSV 和 Excel。CSV 的生成不依赖 Node，也不需要 Excel 安装。

`build_workbook.mjs` 支持只渲染指定工作表以减少重复检查：

```powershell
node scripts/build_workbook.mjs '抗菌训练长表,性能测量,字段字典'
```

修改工作簿时，应遵循当前环境的表格技能要求。预览图和验证报告保存在 `tmp/`，不进入 Git。

已有同名Excel时，构建脚本导入原文件、扩展原生表并写入新增/更新内容，保留表名、顺序、宽度和冻结窗格；不创建并行版本。列结构变化或减少原有行时中止，须显式迁移。支持保留表格格式的追加与重复运行。

## 数据扩充

- 后续 PET 真实实验填入“PET实验录入”模板，不能用文献推测值冒充实测。
- 建模时先按端点、材料层级与试验协议筛选，再按论文/合成批次分组。
- 更新输出后运行验证，记录数据量、来源或筛选规则的变化，并提交 Git。
