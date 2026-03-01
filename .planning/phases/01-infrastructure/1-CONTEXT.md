# Phase 1: Infrastructure Setup - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

---

## Phase Boundary

**Goal:** 建立 Nextflow 工作流基础设施，包括主流程、配置文件和容器化支持

这是基础设施阶段，专注于建立可运行的开发框架。

---

## Implementation Decisions

### Nextflow 项目结构

**Decision:** 使用标准 Nextflow DSL2 项目布局

**Rationale:** Nextflow DSL2 是现代标准，模块化设计支持独立开发和测试。

---

**模块组织**

**Decision:** 按功能模块组织 Nextflow 文件

**Rationale:** 清晰的模块边界便于并行开发和独立测试。

---

**配置系统**

**Decision:** 使用 Groovy 配置文件（viral_dna.config 和 viral_rna.config）

**Rationale:** 分离配置便于 DNA/RNA 分支参数管理，用户可在不修改主流程的情况下调整参数。

---

**容器化策略**

**Decision:** 使用 Docker 作为主要容器方案，Singularity 作为 HPC 选项

**Rationale:** Docker 开发更友好，Singularity 在 HPC 环境是必需的。

---

## Code Context

### 现有相关代码

mac-dedup 项目：
- 使用 Click 进行 CLI 接口
- 使用 Python 作为主要脚本语言
- 使用 mypy 进行类型检查
- 已有测试框架（pytest）

**可复用模式：**
- Click 参数验证模式
- 错误处理和日志记录模式
- 测试结构（fixtures, parametrize）

### 新项目与现有代码分离

**Decision:** viral-phylogeny-pipeline 作为独立项目

**Rationale:** 两个项目技术栈差异较大（Python vs Nextflow），保持分离避免耦合。

---

## Environment Specifics

### 开发环境

- macOS (darwin)
- Python 3.11+
- Nextflow 24.10+
- Docker Desktop

### 执行环境

- HPC: Slurm（目标环境）
- 云端: AWS Batch（可选）
- 本地测试环境

### 数据源

- FASTQ: 原始测序数据（Illumina、ONT）
- FASTA: 已组装基因组

---

## Constraints

### 依赖管理

**Decision:** 使用 Conda 管理 Python 和 bioinformatics 工具

**Rationale:** bioconda 是权威的生物信息学包源，版本控制可靠。

### 文件路径

**Decision:** 使用 Nextflow params 动态指定所有路径

**Rationale:** 避免硬编码路径，支持不同执行环境。

---

## Deferred Ideas

### v2 功能

以下功能已识别但推迟到 v2：

- 实时变异追踪
- 时间尺度定分析
- 选择压力分析
- 传播网络重建
- 内置网页可视化界面
- 动态树图生成
- 地理信息叠加
- 元数据标注工具

**原因：** 这些功能超出 v1 范围（基础设施和核心分析功能），可在后续独立开发。

---

## Next Steps

根据配置，下一步是：
- `/gsd:plan-phase 1` - 创建详细执行计划

---
*Last updated: 2026-03-01*
EOFCTX'