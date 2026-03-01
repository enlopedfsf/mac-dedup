# Roadmap: viral-phylogeny-pipeline

**Created:** 2026-03-01
**Total Phases:** 5
**Requirements Mapped:** 30/30 (100% coverage)

---

## Phase 1: Infrastructure Setup

**Goal:** 建立 Nextflow 工作流基础设施，包括主流程、配置文件和容器化支持

**Requirements:**
- INF-01: Nextflow DSL2 主流程文件
- INF-02: 病毒类型参数验证（dna/rna）
- INF-03: 配置文件系统（viral_dna.config, viral_rna.config）
- INF-04: Docker 容器镜像定义
- INF-05: Singularity 容器支持
- INF-06: Slurm 执行环境支持
- INF-07: AWS Batch 执行环境支持
- INF-08: 本地执行环境支持
- INF-09: 进度跟踪和日志记录

**Success Criteria:**
1. nextflow run --help 显示正确的帮助信息
2. main.nf 文件定义所有 9 个模块的基本流程结构
3. viral_dna.config 和 viral_rna.config 可独立加载
4. Docker 镜像成功构建并可运行
5. 在 local、slurm、awsbatch 环境下均可运行

**Plans:**
- 1.1: 创建 Nextflow 主流程结构
- 1.2: 实现病毒类型参数验证
- 1.3: 创建 DNA 和 RNA 配置文件
- 1.4: 定义容器和执行环境配置
- 1.5: 实现日志和进度跟踪

---

## Phase 2: Quality Control & Data Processing

**Goal:** 实现质量控制、序列比对和共识序列生成模块

**Requirements:**
- QC-01, QC-02: FastQC 报告和 MultiQC 汇总
- QC-03, QC-04: CheckV 质量评估和过滤
- DP-01: BWA-MEM DNA 病毒序列比对
- DP-02: Minimap2 RNA 病毒序列比对
- DP-03: LoFreq DNA 病毒共识生成
- DP-04: iVar RNA 病毒共识生成（60% 频率）
- DP-05: SAM/BAM 文件转换和索引
- DP-06: FASTQ 和 FASTA 输入支持

**Success Criteria:**
1. FastQC 生成 HTML 质量报告
2. MultiQC 汇总所有样本的质控结果
3. CheckV 根据阈值过滤样本并输出质量报告
4. DNA 样本使用 BWA-MEM 生成 BAM 文件
5. RNA 样本使用 Minimap2 生成 BAM 文件
6. LoFreq 和 iVar 分别生成 FASTA 共识序列
7. FASTQ 和 FASTA 输入都能正确处理
8. 每个模块独立测试通过

**Plans:**
- 2.1: 实现 FastQC 质控流程
- 2.2: 实现 MultiQC 报告汇总
- 2.3: 实现 CheckV 病毒质量评估
- 2.4: 实现 BWA-MEM DNA 序列比对
- 2.5: 实现 Minimap2 RNA 序列比对
- 2.6: 实现 LoFreq 共识生成（DNA）
- 2.7: 实现 iVar 共识生成（RNA）
- 2.8: 实现 SAM/BAM 处理和 FASTA 输入支持

---

## Phase 3: Phylogenetic Analysis

**Goal:** 实现多序列比对、SNP 提取和系统发育树构建

**Requirements:**
- PA-01: MAFFT 高精度多序列比对
- PA-02: trimAl 比对修剪和去噪
- PA-03: SNP-sites SNP 位点提取
- PA-04: IQ-TREE 2 系统发育树构建
- PA-05: ModelFinder 自动选择模型
- PA-06: UFBoot Bootstrap (1000 次)
- PA-07: SH-aLRT 分支支持度评估
- PA-08: Newick 树格式输出
- OPT-01: GARD 重组检测（可选）
- OPT-02: 重组断点报告生成
- OPT-03: 重组区域过滤

**Success Criteria:**
1. MAFFT 生成高质量多序列比对
2. trimAl 成功修剪低质量区域
3. SNP-sites 提取正确的 SNP 位点
4. IQ-TREE 2 生成系统发育树（Newick 格式）
5. ModelFinder 自动选择并报告最佳模型
6. UFBoot 执行 1000 次 bootstrap
7. SH-aLRT 生成分支支持度评估
8. GARD 重组检测可选启用/禁用
9. 所有模块集成测试通过

**Plans:**
- 3.1: 实现 MAFFT 多序列比对
- 3.2: 实现 trimAl 比对修剪
- 3.3: 实现 SNP-sites SNP 提取
- 3.4: 实现 IQ-TREE 2 系统发育树构建
- 3.5: 实现 GARD 重组检测（可选模块）
- 3.6: 集成测试和验证

---

## Phase 4: Lineage Assignment & Visualization

**Goal:** 实现世系/Clade 分配和可视化导出功能

**Requirements:**
- LA-01: Nextclade Clade 分配（多病毒支持）
- LA-02: Pangolin PANGO 世系分配
- LA-03: 双重世系验证和冲突解决
- LA-04: 世系分配 TSV 报告生成
- VIS-01: iTOL 交互式树可视化导出
- VIS-02: Auspice 时空可视化数据格式
- VIS-03: Nextstrain 实时追踪兼容格式
- VIS-04: 结果目录模块化组织

**Success Criteria:**
1. Nextclade 正确分配 Clade 并生成 TSV 报告
2. Pangolin 正确分配 PANGO 世系并生成 TSV 报告
3. 双重世系验证检测冲突并解决
4. iTOL 生成可上传的数据包
5. Auspice 生成兼容的数据格式
6. Nextstrain 生成兼容的 JSON 格式
7. 结果目录按照模块化结构组织
8. 所有可视化功能集成测试通过

**Plans:**
- 4.1: 实现 Nextclade Clade 分配
- 4.2: 实现 Pangolin PANGO 世系分配
- 4.3: 实现双重世系验证和报告
- 4.4: 实现 iTOL 可视化导出
- 4.5: 实现 Auspice 数据格式导出
- 4.6: 实现 Nextstrain 兼容格式
- 4.7: 实现结果目录组织和文档

---

## Phase 5: Testing & Documentation

**Goal:** 完成单元测试、集成测试和用户文档

**Requirements:**
- 所有前面阶段的功能需要验证
- 用户文档和使用示例
- CI/CD 配置

**Success Criteria:**
1. 单元测试覆盖率 ≥80%
2. 所有核心模块有集成测试
3. README.md 包含完整使用说明
4. 使用示例在 README 中可运行
5. Conda 环境文件正确配置所有依赖
6. CI/CD 流程验证每次提交

**Plans:**
- 5.1: 编写单元测试（覆盖率目标 80%+）
- 5.2: 编写集成测试（端到端流程验证）
- 5.3: 撰写 README 用户文档
- 5.4: 创建 Conda 环境文件
- 5.5: 配置 CI/CD 流程
- 5.6: 最终验证和发布

---

## Progress Tracking

| Phase | Plans | Status |
|-------|--------|--------|
| Phase 1: Infrastructure | 5 plans | Pending |
| Phase 2: QC & Data Processing | 8 plans | Pending |
| Phase 3: Phylogenetic Analysis | 6 plans | Pending |
| Phase 4: Lineage & Visualization | 7 plans | Pending |
| Phase 5: Testing & Documentation | 6 plans | Pending |

---
*Roadmap created: 2026-03-01*
*Last updated: 2026-03-01*
EOFROAD'