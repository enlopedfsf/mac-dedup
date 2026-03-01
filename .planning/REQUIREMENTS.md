# Requirements: viral-phylogeny-pipeline

**Defined:** 2026-03-01
**Core Value:** 准确高效的病毒 SNP 系统发育分析，支持 DNA/RNA 病毒分支，重组检测可选

## v1 Requirements

### Quality Control

- [ ] **QC-01**: FastQC 报告生成原始测序数据质量评估 HTML
- [ ] **QC-02**: MultiQC 汇总所有样本的质控结果
- [ ] **QC-03**: CheckV 评估病毒基因组完整性（≥90% 完整度）和污染度（≤5%）
- [ ] **QC-04**: 质量过滤根据 CheckV 阈值排除低质量样本

### Data Processing

- [ ] **DP-01**: BWA-MEM 序列比对支持 DNA 病毒和 Illumina 数据
- [ ] **DP-02**: Minimap2 序列比对支持 RNA 病毒和 ONT/PacBio 数据
- [ ] **DP-03**: LoFreq 共识序列生成支持 DNA 病毒（可配置最小频率）
- [ ] **DP-04**: iVar 共识序列生成支持 RNA 病毒（60% 最小等位基因频率）
- [ ] **DP-05**: SAM/BAM 文件转换和索引生成
- [ ] **DP-06**: 支持 FASTQ 和 FASTA 两种输入格式

### Phylogenetic Analysis

- [ ] **PA-01**: MAFFT 高精度多序列比对
- [ ] **PA-02**: trimAl 比对修剪和去噪
- [ ] **PA-03**: SNP-sites 提取 SNP 位点
- [ ] **PA-04**: IQ-TREE 2 系统发育树构建
- [ ] **PA-05**: ModelFinder 自动选择最佳替代模型
- [ ] **PA-06**: UFBoot 超快 Bootstrap（1000 次）
- [ ] **PA-07**: SH-aLRT 分支支持度评估
- [ ] **PA-08**: Newick 树格式输出

### Lineage Assignment

- [ ] **LA-01**: Nextclade Clade 分配（多病毒支持）
- [ ] **LA-02**: Pangolin PANGO 世系分配（SARS-CoV-2 等 RNA 病毒）
- [ ] **LA-03**: 双重世系验证和冲突解决
- [ ] **LA-04**: 世系分配 TSV 报告生成

### Optional Features

- [ ] **OPT-01**: GARD 重组检测（可选，默认关闭）
- [ ] **OPT-02**: 重组断点报告生成
- [ ] **OPT-03**: 重组区域过滤

### Infrastructure

- [ ] **INF-01**: Nextflow DSL2 主流程文件
- [ ] **INF-02**: 病毒类型参数验证（dna/rna）
- [ ] **INF-03**: 配置文件系统（viral_dna.config, viral_rna.config）
- [ ] **INF-04**: Docker 容器镜像定义
- [ ] **INF-05**: Singularity 容器支持
- [ ] **INF-06**: Slurm 执行环境支持
- [ ] **INF-07**: AWS Batch 执行环境支持
- [ ] **INF-08**: 本地执行环境支持
- [ ] **INF-09**: 进度跟踪和日志记录

### Visualization & Reporting

- [ ] **VIS-01**: iTOL 交互式树可视化导出
- [ ] **VIS-02**: Auspice 时空可视化数据格式
- [ ] **VIS-03**: Nextstrain 实时追踪兼容格式
- [ ] **VIS-04**: 结果目录模块化组织（01_qc 到 10_visualization）

## v2 Requirements

### Advanced Analysis

- [ ] **ADV-01**: 实时变异追踪
- [ ] **ADV-02**: 时间尺标定分析
- [ ] **ADV-03**: 选择压力分析
- [ ] **ADV-04**: 传播网络重建

### Enhanced Visualization

- [ ] **ENH-01**: 内置网页可视化界面
- [ ] **ENH-02**: 动态树图生成
- [ ] **ENH-03**: 地理信息叠加
- [ ] **ENH-04**: 元数据标注工具

## Out of Scope

| Feature | Reason |
|---------|--------|
| RDP4 重组检测 | 闭源软件，已停止维护 |
| Gubbins | 主要用于细菌，不适用于病毒 |
| 病毒宏基因组分析 | 聚焦于单个病毒 SNP 分析 |
| 病毒准种检测 | 超出系统发育分析范围 |
| 基因注释 | 可依赖外部工具完成 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| QC-01, QC-02 | Phase 2 | Pending |
| QC-03, QC-04 | Phase 2 | Pending |
| DP-01, DP-02 | Phase 2 | Pending |
| DP-03, DP-04 | Phase 2 | Pending |
| DP-05, DP-06 | Phase 2 | Pending |
| PA-01, PA-02 | Phase 3 | Pending |
| PA-03, PA-04 | Phase 3 | Pending |
| PA-05, PA-06, PA-07, PA-08 | Phase 3 | Pending |
| LA-01, LA-02 | Phase 4 | Pending |
| LA-03, LA-04 | Phase 4 | Pending |
| OPT-01, OPT-02, OPT-03 | Phase 3 | Pending |
| VIS-01, VIS-02, VIS-03, VIS-04 | Phase 4 | Pending |
| INF-01 to INF-09 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-01*
*Last updated: 2026-03-01 after initial definition*
EOFREQU'