# PET 基抗菌碳点：文献数据库与配方筛选

本项目以 **PET 为固定主前驱体**，研究搭配哪些共前驱体、掺杂剂和制备条件，能够使纯化后的游离碳点表现出抗菌活性。

当前阶段完成了木质素相关文献数据整理。**目前没有 PET 共前驱体配方的抗菌实测标签，也尚未训练或验证 PET 配方预测模型。** 文献数据用于筛选候选路线、定义特征和设计后续 PET 实验。

## 从哪里开始

- [Excel 文献数据库](output/木质素碳点训练数据库/PET搭配材料筛选_木质素碳点文献数据库.xlsx)：先看“路线筛选”“建库说明”和“待核查”。
- [CSV 数据](output/木质素碳点训练数据库/csv/)：用于程序读取，各字段在“字段字典”中有中文解释。
- [CSV 数据包](output/木质素碳点训练数据库/机器学习CSV数据包.zip)：包含全部 CSV 与使用说明。
- [建库与建模说明](output/木质素碳点训练数据库/建库与建模说明.md)：单位、缺失值、标签与数据切分规则。
- [项目记录](docs/PROJECT_LOG.md)：每次实质改动及验证结果。

## 当前数据版本

2026-10-16 从本地资料整理，包含去重后的 9 篇原始研究、2 份补充材料，以及 5 篇综述的来源索引。原有文献目录中另有 6 篇研究全文未提供。

| 内容 | 记录数 |
| --- | ---: |
| 碳点合成样品 | 20 |
| 配方组分 | 77 |
| 工艺步骤 | 119 |
| 复合体系 | 23 |
| 抗菌相关记录 | 96 |
| 全部性能测量记录 | 250 |
| 综述二次数据 | 51 |
| 待核查问题 | 13 |

这些行数不是独立配方或独立合成批次数。抗菌记录包含不同菌种、条件、定性观察及派生值。目前明确、非冲突、非派生的游离碳点定量抗菌结果有 6 条，来自 2 个非 PET 样品，端点与测试协议不同。

## 目录

```text
scripts/                         提取、建库、工作簿生成和验证脚本
docs/                            项目记录与复现说明
output/木质素碳点训练数据库/       Excel、CSV、字段字典及数据包
文献-木质素基抗菌碳点/             原始论文、补充材料、已有资料
tmp/                             临时提取文本、预览图和验证报告（不上传）
```

保留了原始文献目录和文件名，方便核对已有引用。两个重复 PDF 版本仍保留在原始资料中，数据库通过文件哈希或 DOI 去重。原始压缩包与解压内容重复，不进入版本库。

## 复现

Python 负责文本提取、数据整理及验证；Excel 使用 Codex 提供的 `@oai/artifact-tool` 生成，不通过 Python 写入工作簿。详见 [复现说明](docs/REPRODUCING.md)。

```powershell
python scripts/extract_sources.py
python scripts/build_database.py
node scripts/build_workbook.mjs
python scripts/verify_database.py
```

需要先安装 Python 依赖，并让 Node 能解析 Codex 的 `@oai/artifact-tool`。不要将本机虚拟环境或 `node_modules` 提交到 Git。

## 训练前必须保留的区别

- 游离碳点、依赖 H2O2 的碳点、复合膜、水凝胶及金属复合体系分别处理。
- MIC/MBC、抑菌圈、存活率、杀菌率和接触抑菌观察分别作为端点。
- 空值不代表 0；无抗菌试验不标为负例；“无抑菌圈”不直接等同于无抗菌活性。
- 综述转述数据先追溯原文，不直接混入全文实测数据。
- 原值与由“100−存活率”得到的派生值不能作为两个独立观测。
- 按论文和共同合成样品分组切分数据，避免同一配方跨训练集和测试集。
- 配方预测模型不直接使用制备后才知道的表征结果；需要时建立单独的两阶段模型。

## Git 留档规则

本项目按用户要求持续通过 Git 留档。每次实质改动应更新项目记录、完成适用验证、提交有意义的 commit，并同步到 `origin`。不得将临时文件、凭据或虚拟环境上传。

原始 PDF 和 Word 文件由 **Git LFS** 保存。首次克隆建议使用：

```powershell
git lfs install
git clone https://github.com/Tinker-Zhang404/-.git
```

第三方论文及图片的权利归各自权利人；本仓库不为这些原始资料重新授予许可。

## 第一版传统模型基线

新增 [CUDA XGBoost 训练报告](output/training/literature_pva_xgb_cuda_v1/report.md)、[模型及元数据](models/literature_pva_xgb_cuda_v1/)和可复现训练/预测脚本。

该模型仅针对 **A08 单篇论文中 PVA/木质素碳点膜的抗菌结果**：16 条观察、3 个膜添加水平、1 个碳点合成样品。输入为添加百分数、接触时间、光照和菌种；按膜配方完整留出验证，并与训练折均值基线比较。不将其他论文、抑菌圈、定性结果或重复派生值混入训练。

它用于建立传统模型流程及验证基线，**不能预测 PET 共前驱体/掺杂剂配方，也未获得跨论文或独立 PET 实验验证**。详见报告中的数据筛选、折外误差和源文献歧义说明。

```powershell
python -m venv .venv-ml
.\.venv-ml\Scripts\python -m pip install -r requirements-ml.lock.txt
.\.venv-ml\Scripts\python scripts/train_baseline.py
.\.venv-ml\Scripts\python -m unittest discover -s tests -v
.\.venv-ml\Scripts\python scripts/predict_baseline.py --input examples/non_pet_pva_prediction.csv --output tmp/example_prediction.csv
```

训练需要支持当前 XGBoost CUDA 构建的 NVIDIA 显卡和驱动；程序核查每折实际设备，禁止静默回退 CPU。数字/类别编码与均值对照由 CPU 完成，树模型训练使用 GPU。预测入口拒绝 PET、其他材料层级、未知菌种/光照以及训练数值范围外的输入。
