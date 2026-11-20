# 数据科学起始资料包 v0.3｜中文阅读版

[返回中文总入口](index.html) · [英文 ZIP](../../MRI_Hackathon_DataScience_StarterPack_v0.3.zip) · [英文展开目录](../../MRI_Hackathon_DataScience_StarterPack_v0.3/) · [Markdown 源](starterpack.md)

ZIP 和展开目录是同一资料包。两处均有 88 个交付文件。

## 起始说明：MRI 与局部波谱黑客松数据科学资料包 v0.3

[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/README.md)

本包是**合成教学数据**，无真实患者信息，仅供教学使用。

### 为什么有四种格式

- **DICOM** 是用于采集和临床的对象格式。有丰富的元数据和大量标签。每个序列可包含一个或多个实例。
- **NIfTI** 将 n 维数组与几何信息紧凑存储。它便于分析，有意省去许多 DICOM 采集元数据。
- **BIDS** 定义数据集组织和元数据约定，以 NIfTI 等标准文件配合 JSON 或 TSV 旁车文件。
- **MRS-BIDS** 是用于磁共振波谱的 BIDS 模态。波谱源数据用 **NIfTI-MRS** 表示，保存复数时域数据和波谱元数据。

教学流程：DICOM／NIfTI／NIfTI-MRS → BIDS／MRS-BIDS → 质控与溯源 → `features.csv`／证据包（`packets/*.json`）→ 数字孪生更新。

### 数据科学方向的学习目标

课程聚焦数据接口。

1. 识别源格式及各自提供和省略的信息。
2. 把元数据和特征转换为小型、明确的 JSON／CSV 数据契约。
3. 识别缺失和无效值，保留质控标记。
4. 保留单位、时间、坐标参考和溯源信息。
5. 向数字孪生层交付经过验证的证据包。

### 数据质量责任边界

- **量子工程**决定测量的物理含义及适用的物理层面质控指标。
- **精密机械／计量学**提供校准、可追溯性、几何和重复性信息以及不确定度。
- **数据科学**检查结构、类型、缺失情况、有效范围、标识符、单位、元数据、去标识化、数据沿袭和协调一致性。发现可疑证据时应标记，禁止静默修复或填补。
- **数字孪生**制定状态更新所需的输入契约和接收策略。可在计入不确定度后接收 `WARN` 证据，并按共同契约拒绝 `FAIL` 证据。

### 建议的 60–75 分钟合作方课程

1. **5 分钟**。数据格式为何属于科学证据的一部分。
2. **15 分钟**。DICOM → NIfTI → BIDS／MRS-BIDS：哪些信息变化、保留或可能丢失。
3. **15 分钟**。把 JSON 和 CSV 用作小型接口格式。查看 `05_TwinReady_JSON_CSV/`。
4. **10 分钟**。质控标记、缺失值、无效值、单位和去标识化。
5. **10 分钟**。溯源与数据沿袭。每个特征链接到源文件和处理步骤。
6. **15–20 分钟实践**。利用所附示例构建或修改一份证据包（`packets/*.json`）。

### 建议的学生作业

使用基线与随访示例完成下列步骤。

1. 清点可用文件及元数据。
2. 生成或修订 `features.csv`。
3. 做基本的有效性和缺失检查，生成 `qc_report.json`。
4. 生成一个满足 `data_contract.json` 的证据包（`packets/*.json`）。
5. 标明各字段由量子工程、精密机械／计量学或数据科学中的哪个方向提供。
6. 解释数字孪生应该 `update`、`update_with_warning` 还是 `reject`。

可以选做详细数据库模式。

### 推荐工具

- DICOM：pydicom、dcmtk。转换可用 dcm2niix。
- NIfTI：nibabel、FSL、AFNI、MRIcroGL。
- BIDS：BIDS Validator、BIDS Starter Kit。
- NIfTI-MRS／MRS-BIDS：spec2nii、FSL-MRS、Osprey。

### 示例所用标准

- [DICOM PS3.3／PS3.5，原文注明 2026 版](https://dicom.nema.org/medical/dicom/current/output/chtml/)
- [NIfTI-1](https://nifti.nimh.nih.gov/nifti-1/)
- [BIDS 1.11.x](https://bids-specification.readthedocs.io/en/stable/)
- [MRS-BIDS](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetic-resonance-spectroscopy.html)
- [NIfTI-MRS 0.3](https://wtclarke.github.io/mrs_nifti_standard/)

这些文件是有意做小的合成数据。使用真实临床或科研数据前，按当地规定落实数据治理、去标识化、知情同意及数据保护，并用适用的工具验证数据集。

### v0.3 的变化（2026-10-20）

详见下方变更记录。合成波谱的化学位移已按记录的约定修正，VOI 位于额叶。统一 DICOM／NIfTI 几何，T1 加权协议与图像一致，ROI 体积可复现，两次采集相隔 6 个月。新增证据包 v1.0 和阈值 v1.0。T1w 图像具备 T1 加权对比，随访解剖形态保持一致。MRS 噪声按期望值校准。

### 波谱约定（NIfTI-MRS 文件）

- 时域模型 \(s(t)=\sum_j a_j\exp(-\pi\,\mathrm{LW}\,t)\exp(+i2\pi f_jt)\)，其中 \(f_j=(\delta_j-4.65\,\mathrm{ppm})\nu_0\)，\(\nu_0=123.25\,\mathrm{MHz}\)。
- 频谱为 `fftshift(FFT(s))`。频率 \(f\) 随采样点索引递增。ppm 标尺为 \(4.65+f/\nu_0\)。接收频率对应 4.65 ppm，采用 FSL-MRS 对 ¹H 的约定。绘图时 ppm 从左向右递减。
- 驻留时间 0.5 ms（`pixdim[4]`），1,024 点，谱宽 2,000 Hz（16.2 ppm）。
- SNR 为实部频谱上的 NAA 峰高除以 −3.0 至 0.0 ppm 区间内实部频谱的标准差，即峰高／噪声标准差。
- 标称场强 3.0 T。按谱仪频率得到的实际场强为 123.25／42.577 = 2.895 T。两者均需保留。

## 数据科学合作课程与作业

[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/DATA_SCIENCE_LECTURE_AND_ASSIGNMENT.md)

### 课程内容（60–75 分钟）

课程面向量子工程学生，重点练习如何让物理测量可移植、可查询，并能安全地提供给下游数字孪生更新。

1. **数据格式为何属于证据（5 分钟）**。可信的测量数值应附单位、采集上下文、坐标系和溯源信息。
2. **DICOM → NIfTI → BIDS／MRS-BIDS（15 分钟）**。说明每种表示的用途及转换时哪些元数据保留、外置或可能丢失。
3. **JSON 与 CSV 接口格式（15 分钟）**。查看 `data_contract.json`、`features.csv` 和证据包（`packets/*.json`）。
4. **数据质量（10 分钟）**。检查必需字段、缺失或无效值、单位、标识符、范围和去标识化。保留 `null` 并记录原因。
5. **溯源与数据沿袭（10 分钟）**。把每个派生特征链接到源文件、处理步骤、版本和质控状态。
6. **实践（15–20 分钟）**。修改示例证据包，决定孪生体应 `update`、`update_with_warning` 或 `reject`。

### 学生作业

使用基线和随访示例。

1. 清点可用文件和元数据。
2. 新建或修订 `features.csv`。
3. 检查一组缺失值、类型、单位和范围条件，生成 `qc_report.json`。
4. 生成一份满足 `data_contract.json` 的证据包（`packets/*.json`）。
5. 标明每个质量判定的责任方：量子工程、精密机械／计量学、数据科学、数字孪生或共同负责。
6. 决定 `update`、`update_with_warning` 或 `reject`，给出机器可读的原因。
7. 演示从某个孪生体变量追溯到源文件的路径。

无需开设完整的关系数据库理论课程，也无需高级 SQL 优化、生产数据仓库或复杂机器学习模型。禁止静默填补缺失的科学数值。优先采用简单、明确、可测试的契约。

## 合作方接口简报

[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/PARTNER_INTERFACE_BRIEF.md)

四门合作课程共同服务于一个集成演示。每门课程需准备一件跨方向接口产物，以完成一次从基线到随访的更新。

| 层 | 核心问题 | 课程重点 | 必须交付 |
| --- | --- | --- | --- |
| 量子工程 | 实际观测到了什么？ | MRI／MRS 信号的含义，空间和频谱定位，定量与对比加权可观测量，物理质控 | 测量卡及可解释的可观测量 |
| 精密机械／计量学 | 观察结果是否可信并可复现？ | 几何、B₀／B₁／梯度效应、校准、漂移、重复性、可追溯性、不确定度 | 校准／不确定度卡及阈值 |
| 数据科学 | 如何表示和检查证据？ | DICOM／NIfTI／BIDS／MRS-BIDS、JSON／CSV 契约、缺失或无效值、单位、标识符、溯源 | `qc_report.json` 及证据包（`packets/*.json`） |
| 数字孪生 | 如何用已接收证据更新模型？ | 状态和观测的区别、输入契约、时间对齐、更新逻辑、不确定度、情景、下一次测量逻辑 | 状态／更新契约和一次更新事件 |

### 共同质量门控

1. **量子工程**标记物理和采集问题，并定义有物理意义的可观测量。
2. **精密机械／计量学**提供校准状态、重复性、几何及场的不确定度和接收阈值。
3. **数据科学**验证结构、类型、必需字段、标识符、单位、缺失情况、技术上合理的范围、去标识化和数据沿袭。禁止静默修复或填补科学证据。
4. **数字孪生**定义更新所需的输入并应用 `PASS`、`WARN`、`FAIL` 接收逻辑。

对每个被拒绝或降级的项目保留机器可读的原因。

### 最终集成层

最低演示要求：先验状态 → 随访证据 → 质量门控 → 证据包 → 孪生体更新或拒绝 → 不确定度视图 → 下一次测量建议。最终原型应至少演示一条从源文件到孪生体变量的完整溯源路径。

## v0.3 变更记录（2026-10-20）

[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/CHANGELOG_v0.3.md)

`make_starterpack_v03.py` 从 v0.2 的副本生成 v0.3，原 v0.2 保持不变。数据是合成教学数据，仅供非临床使用。

| 编号 | v0.2 问题 | v0.3 修正 |
| --- | --- | --- |
| X1 | Explorer 中 NAA、Cr 和 Cho 峰约为 5.7／4.7／4.0 ppm。三个峰的间隔与任一统一的 ppm 参考不一致。 | 重新生成 FID：`f_j = (delta_j - 4.65 ppm) x 123.25 MHz`。六条等效单峰线分别为 NAA、Cr、Cho、mI、Glx、Cr CH₂，振幅复现证据包的比值。在起始 README 记录 FFT 约定。 |
| X4 | T1w 旁车文件写的是 2D 梯度回波、TR 2 s、90°，无法给出所需的 T1 加权协议。 | 旁车文件和 DICOM 标签均采用类 3D MPRAGE 协议：TR 2.3 s、TI 0.9 s、TE 3 ms、9°。 |
| X5 | 3.0 T 标称值与 123.25 MHz 之间的差异无解释。 | 保留两者。添加 DICOM `ImagingFrequency (0018,0084) = 123.25 MHz`，README 解释 B₀ = 2.895 T。 |
| X6 | 证据包缺少单位、证据性质标签和阈值引用。 | v1.0 证据包（每个可观测量一包）、`thresholds-v1.0.json` 和数据契约 v1.0。v0.2 文件放在 `legacy_v0.2/`。 |
| X9 | MRS VOI 的仿射以（−96, −96, −32）mm 为中心，即头部之外的视野角点。 | VOI 中心为 RAS 坐标（−16, 45, 6）mm，位于额叶，是脑掩膜内边长 20 mm 的立方体。 |
| X10 | `dicom_metadata_extract_example.csv` 与文件不符，TE 为 3.5 与 12 ms，IPP z 为 −30 与 −32。 | 根据 DICOM 文件重新生成。 |
| X11 | DICOM（LPS）与 NIfTI（RAS）几何描述了镜像图像。 | 使用常规 DICOM 定向（IOP `1\0\0\0\1\0`，IPP `-93\-93\z`，像素旋转 180°）。世界坐标中的强度现与 NIfTI 一致。 |
| X12 | `nifti_header_example.json` 写作 `int16`，文件实际为 `float32`。 | 改正并加入仿射与轴向代码。 |
| X13 | 文件无法复现证据包中的 ROI 体积。 | 部分容积 ROI 掩膜（`03_BIDS_MRI/derivatives/roi`）积分给出恰好 22,140 和 27,810 mm³。 |
| X14 | 两次会话都标作 2026-11-20，而孪生体假定间隔 6 个月。 | 改为 2026-05-20 和 2026-11-20，涉及 DICOM `StudyDate`、`sessions.tsv` 和 `relative_time`。 |

有意保留的异常（手册 §3.10）：随访 ROI 证据包声称 \(u=4\%\)，而 1.1 mm 的配准 RMS 指向约 19%。阈值 v1.0 中的 `roi_u_consistency` 可以捕获异常。生成该证据包的管线未运行这一检查。

| 编号 | v0.2 问题 | v0.3 修正 |
| --- | --- | --- |
| X15 | T1w 图中病灶（T1 = 1,450 ms）亮于灰质（1,200 ms），偏离 T1 加权对比。随访图中有 60 个体素变化（病灶边缘类似病灶的白质），而 ROI 变化应当是处理伪差。 | 从 T1 图重新生成 T1w 图：白质 900 > 灰质 650 > 病灶 540 > 脑脊液 180 a.u.，噪声 SD 为 12。随访图使用独立噪声实现，解剖和真值保持一致。 |
| X16 | MRS 噪声针对该次实现本身调整以命中 SNR。同一协议下，随访时每通道 σ 降低 27%，拟合 CRLB 未增长。 | 选择噪声实现，使 SNR 校准后每通道 σ 与期望值（无噪声 NAA 峰高／(SNR √N)）的偏差不超过 2%，而拟合比值与真值的偏差在半个 SD 内。现在 σ 随峰高变化（随访时低约 10%），随访时 Cho/Cr 的 CRLB 增加。 |

T1 图和脑掩膜 NIfTI 文件（字节相同）、受试对象文件、MRS 旁车文件沿用旧版。方向名称改为与挑战手册一致的量子工程、精密机械／计量学、数据科学和数字孪生。

## BIDS 示例说明

- **MRI。** 合成 BIDS MRI 教学示例，无真实患者数据。[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/README)
- **MRS。** 合成 MRS-BIDS 示例。NIfTI-MRS 文件包含复数时域 FID 和带 MRS 元数据的 NIfTI 文件头扩展。[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/README)

## 面向数字孪生的接口

[英文原件](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/README.md)

- `packets/` 存放 v1.0 证据包，每个可观测量一份。`E-t0-*` 是基线（第 0 个月），`E-t1-*` 是随访（第 6 个月），`E-t1-chobad` 是有意构造的无效 `FAIL` 示例，必须拒绝更新。
- `evidence_packet_v1.0.schema.json` 是证据包的 JSON Schema 2020-12（挑战手册 v1.0 §8.2）。
- `thresholds-v1.0.json` 记录机器可读的门控规则和孪生体策略（手册 §5.8）。
- `data_contract.json` 说明孪生层的输入要求。
- `features.csv` 和 `data_dictionary.csv` 提供紧凑的特征表、单位、责任方和证据性质标签。
- `qc_report.json` 是随访质控报告，需留意 `not_run_by_pipeline`。
- `legacy_v0.2/` 保留 v0.2 文件，供将旧版证据包迁移为 v1.0 证据包的练习使用。

教学规则：严禁静默补值把 `FAIL` 转成 `PASS`。保留异常并交给责任方向。随访 ROI 证据包记录为 `PASS`，因为生成管线没有运行阈值 v1.0 的 `roi_u_consistency`。运行该规则后再决定孪生体操作，Explorer 可执行这一步。

## 质量控制与证据字段

### 各层标签的含义

| 字段或值 | 中文说明 |
| --- | --- |
| `subject_id`、`session_id`、`relative_time` | 假名受试对象、采集会话、相对基线的时间。实际采集时间查 `sessions.tsv` 的 `acq_time`。 |
| `spatial_reference`、`source_object`、`source_sha256` | 空间坐标系（如 `scanner` 或 `registered_anatomical`）及 ROI／VOI、源对象路径和源对象摘要。 |
| `observable`、`value`、`unit`、`valid_range` | 可观测量、报告的值、单位和有效范围。单位 `1` 表示无量纲。必需值缺失为 `FAIL`。可选值缺失时显式写 `null` 并给出原因。 |
| `origin` | 来源为 `MEASURED`（实测）或 `SIMULATED`（模拟）。 |
| `value_epistemic` | 值来自测量 `MEASURED`、计算或拟合 `DERIVED`、模型推断 `INFERRED` 或模拟 `SIMULATED`。模拟来源的值不得标为实测；可标为从合成数据派生。 |
| `decision_epistemic` | 决策的证据性质。例如，原始值为派生比值，建议则可标为 `INFERRED`。 |
| `uncertainty.type`、`uncertainty.value`、`budget_ref` | 不确定度类型、数值及其预算引用。例：Cho/Cr 随访为 SD 0.06，预算引用为 `D-worksheet-t1`。用于状态更新的每个值必须提供不确定度。 |
| `qc_checks`、`qc_status`、`qc_reasons` | 逐项质控、生成时汇总的状态、质控原因。按当前阈值或补做漏检时，浏览器可得到更严格的有效状态。 |
| `thresholds_ref`、`calibration_id`、`system_qc_id` | 阈值配置、校准记录和系统质控记录的引用。 |
| `protocol_match`、`comparable` | 采集协议是否匹配、是否允许纵向比较。即使数值与类型均合法，也需单独判断这两项。 |
| `acquisition_context`、`processing`、`provenance` | 采集参数、处理方法及版本、源对象和活动的溯源链。 |
| `twin_action.recommended`、`interpretation_limit` | 声明的建议操作及解读边界。由孪生层根据门控与不确定度决定实际更新。 |

### v1.0 教学阈值与通过条件

| 检查 | 规则 | 责任方 |
| --- | --- | --- |
| `registration_rms_mm` | > 2.0 mm 为 `WARN`，> 3.0 mm 为 `FAIL`（失败阈值为提议）。 | PM |
| `mrs_linewidth_Hz` | 对 3 T、¹H NAA 的 FWHM，> 10.0 Hz 为 `WARN`，> 20.0 Hz 为 `FAIL`（失败阈值为提议）。 | PM |
| `mrs_snr` | < 25 为 `WARN`，< 10 为 `FAIL`。SNR 定义见数据字典。 | QE |
| `roi_u_consistency` | 对通过配准传播的 ROI 掩膜，声明的相对不确定度应 ≥ 3 × 配准 RMS／参照 ROI 的等体积球半径。若不满足则警告，并在下游采用隐含的不确定度。 | PM |
| `missing_values` | 缺失值数 > 0 为 `FAIL`。 | DS |
| `valid_range` | 值超出声明范围为 `FAIL`。 | QE |
| `protocol_match` | 序列系列、TE、TR 或场强与基线不一致为 `WARN`。 | PM |
| `system_qc` | 缺少 `system_qc_id` 为 `FAIL`。 | PM |

- `PASS` → `update`，`R_factor = 1.0`。
- `WARN` → `update_with_warning`，该配置用 `R_factor = 2.0` 放大观测方差。接受依据应可解释。
- `FAIL` → `reject`。保留拒绝理由。
- `R_factor` 是声明的团队接收策略。创新统计量为 \(d^2=(y-x_{\mathrm{prior}})^2/(P_{\mathrm{prior}}+R_{\mathrm{packet}})\)。超过 3.841 时标记异常（95%，1 个自由度）。

### 随访示例核对

`qc_report.json` 的随访总体状态为 `WARN`。四项原始检查为：SNR 24.8（`WARN`）、FWHM 11.4 Hz（`WARN`）、配准 RMS 1.1 mm（`PASS`）、缺失值数 0（`PASS`）。报告的 `not_run_by_pipeline` 标出未运行的 `roi_u_consistency`。ROI 包的 `PASS` 对应当时运行的检查。补做一致性检查时，声明的 4% 低于由配准推得的约 19%，应携带警告和修正后的不确定度。随访 `E-t1-chobad.json` 的波谱源对象缺失，值和不确定度为 `null`，其 SNR 为 9.0、线宽为 24.0 Hz、配准 RMS 为 3.8 mm，均达到相应的失败条件。

### 版本阅读方式

v0.3 将每个可观测量封装为独立证据包，并将阈值、契约和模式分开配置。打开 `legacy_v0.2/` 可查看原来的示例记录与字段字典。完成迁移练习时，以对应版本的原始接口和枚举为依据。

## 数据字典和 DICOM 标签指南

### DICOM 标签指南

[英文原表](../../MRI_Hackathon_DataScience_StarterPack_v0.3/01_DICOM/dicom_tag_guide.csv)

| 标签 | 名称 | 用途 |
| --- | --- | --- |
| `(0010,0020)` | `PatientID` | 合成主题标识符；在真实项目中进行去标识处理 |
| `(0020,000D)` | `StudyInstanceUID` | 唯一标识研究 |
| `(0020,000E)` | `SeriesInstanceUID` | 唯一标识系列 |
| `(0008,0018)` | `SOPInstanceUID` | 唯一标识一个 DICOM 对象 |
| `(0018,0080)` | `RepetitionTime` | 采集参数（DICOM MR 图像中的毫秒） |
| `(0018,0081)` | `EchoTime` | 采集参数（DICOM MR 图像中的毫秒） |
| `(0028,0030)` | `PixelSpacing` | 平面几何（毫米） |
| `(0020,0032)` | `ImagePositionPatient` | 以患者坐标系表示的图像原点 |
| `(0020,0037)` | `ImageOrientationPatient` | 图像方向余弦 |
| `(0008,0020)` | `StudyDate` | 会议日期；在去标识化处理后的真实数据中进行调整或移除 |
| `(0018,0084)` | `ImagingFrequency` | 拉莫尔频率，单位为 MHz；表示实际场强 B0 = f / 42.577 MHz T^-1 |
| `(0018,0082)` | `InversionTime` | 反演预处理序列（毫秒） |
| `(0018,1314)` | `FlipAngle` | 激发翻转角（度） |
| `(0018,1020)` | `SoftwareVersions` | 不同会话之间的变化会带来可比性风险。 |
| `(0018,1250)` | `ReceiveCoilName` | 不同会话之间的变化会带来可比性风险。 |
| `(0010,0010)` | `PatientName` | 需要识别；在真实数据中必须去除或替换这些元素。 |

### 数据字典（v0.3）

[英文原表](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/data_dictionary.csv)

| 字段 | 类型 | 单位 | 责任方 | 证据性质 | 含义 |
| --- | --- | --- | --- | --- | --- |
| `subject_id` | `string` | — | 数据科学 | — | 化名主题标识符（BIDS 子标签） |
| `session_id` | `string` | — | 数据科学 | — | BIDS 会话标签 |
| `relative_time_month` | `number` | `mo` | 数据科学 | — | 距基线的时间；`acq_time` 在 `sub-01_sessions.tsv` 中 |
| `roi_volume_mm3` | `number` | `mm3` | 精密机械／计量学 | `DERIVED` | 部分体积感兴趣区域体积 = 分数总和 × 体素体积 |
| `u_roi_volume_mm3` | `number` | `mm3` | 精密机械／计量学 | `DERIVED` | ROI 体积的标准不确定度声明 |
| `mri_roi_mean_au` | `number` | `a.u.` | 量子工程 | `DERIVED` | ROI 中 PV 加权平均 T1w 强度；对比加权值，并非组织参数 |
| `NAA_Cr` | `number` | `1` | 量子工程 | `DERIVED` | 从时域拟合得到的 NAA/Cr(CH3)幅度比 |
| `u_NAA_Cr` | `number` | `1` | 精密机械／计量学 | `DERIVED` | 标准不确定度（预算，工作表 D） |
| `Cho_Cr` | `number` | `1` | 量子工程 | `DERIVED` | 从时域拟合中得到的 Cho/Cr(CH3)幅度比 |
| `u_Cho_Cr` | `number` | `1` | 精密机械／计量学 | `DERIVED` | 标准不确定度（预算，工作表 D） |
| `mrs_snr` | `number` | `1` | 量子工程 | `DERIVED` | 信噪比 = 实际（吸收）光谱中 NAA 峰的高度（1.9-2.1 ppm）除以无信号窗口内实际光谱的标准差（-3.0 至 0.0 ppm）。峰高/噪声标准差；LCModel 的信噪比计算方法是用 RMS 残差的两倍来计算，结果约为前者的一半。 |
| `mrs_linewidth_Hz` | `number` | `Hz` | 精密机械／计量学 | `DERIVED` | 洛伦兹线的全宽半值宽度（拟合的常用线宽） |
| `registration_rms_mm` | `number` | `mm` | 精密机械／计量学 | `DERIVED` | 与基线刚性配准的残差均方根值 |
| `qc_status` | `enum` | — | 共同门控 | — | PASS / WARN / FAIL = 最严格的检查标准；绝不进行无声删除操作 |

### 数据字典（v0.2）

[英文原表](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/data_dictionary.csv)

| 字段 | 类型 | 单位 | 责任方 | 含义 |
| --- | --- | --- | --- | --- |
| `subject_id` | `string` | — | 数据科学 | 匿名主题标识符 |
| `session` | `string` | — | 数据科学 | 纵向会话标签 |
| `roi_volume_mm3` | `number` | `mm3` | 应用物理学 + 精密技术 | 注册的投资回报量 |
| `mri_roi_mean_au` | `number` | `a.u.` | 应用物理学 | ROI 中的平均信号强度；并非定量组织参数 |
| `mrs_NAA_Cr` | `number` | `ratio` | 应用物理学 | 合成 NAA/Cr 比例 |
| `mrs_Cho_Cr` | `number` | `ratio` | 应用物理学 | 合成 Cho/Cr 比例 |
| `mrs_snr` | `number` | `ratio` | 应用物理学 + 数据科学 | 频谱信噪比指标 |
| `mrs_linewidth_Hz` | `number` | `Hz` | 应用物理学 + 精密技术 | 光谱线宽质量指标 |
| `qc_status` | `enum` | — | 共享质量门控 | 通过/警告/失败；切勿默默删除 |

## 原始采集、派生数据、接口与代码索引

### 00_START_HERE 与根目录

| 项目方文件 | 用途 |
| --- | --- |
| [README.md](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/README.md) · [DATA_SCIENCE_LECTURE_AND_ASSIGNMENT.md](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/DATA_SCIENCE_LECTURE_AND_ASSIGNMENT.md) · [PARTNER_INTERFACE_BRIEF.md](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/PARTNER_INTERFACE_BRIEF.md) · [CHANGELOG_v0.3.md](../../MRI_Hackathon_DataScience_StarterPack_v0.3/CHANGELOG_v0.3.md) | 起始说明、课程与作业、合作方接口简报、变更记录。上方提供对应译文。 |
| [tree.txt](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/tree.txt) | 项目方记录的目录树。 |
| [validate_pack.py](../../MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/validate_pack.py) | 项目方数据包验证代码。 |
| [manifest_sha256.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/manifest_sha256.csv) | 项目方发布的源文件路径、尺寸和摘要清单。 |

### 01_DICOM 与 02_NIfTI

| 项目方文件 | 用途 |
| --- | --- |
| [baseline](../../MRI_Hackathon_DataScience_StarterPack_v0.3/01_DICOM/baseline) · [followup](../../MRI_Hackathon_DataScience_StarterPack_v0.3/01_DICOM/followup) | 各有 `IM0001.dcm` 至 `IM0016.dcm`，共 32 个 DICOM 切片。按会话区分基线和随访。 |
| [dicom_metadata_extract_example.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/01_DICOM/dicom_metadata_extract_example.csv) · [dicom_tag_guide.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/01_DICOM/dicom_tag_guide.csv) | 逐实例元数据提取示例与 DICOM 标签指南。标签译注见上方。 |
| [synthetic_T1w_baseline.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/synthetic_T1w_baseline.nii.gz) · [synthetic_T1w_followup.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/synthetic_T1w_followup.nii.gz) | 基线和随访 T1 加权三维图像。强度为对比加权量。 |
| [synthetic_T1map_ms.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/synthetic_T1map_ms.nii.gz) · [synthetic_brain_mask.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/synthetic_brain_mask.nii.gz) | 以 ms 表示的合成 T1 参数图及脑掩膜。 |
| [nifti_header_example.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/nifti_header_example.json) · [nifti_example_metadata.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/02_NIfTI/nifti_example_metadata.json) | NIfTI 文件头示例与额外元数据示例。 |

### 03_BIDS_MRI

| 项目方文件 | 用途 |
| --- | --- |
| [README](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/README) | 教学示例的项目方说明。上方提供译文。 |
| [dataset_description.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/dataset_description.json) | BIDS 数据集声明。 |
| [dataset_description.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/derivatives/roi/dataset_description.json) | ROI 派生数据集声明。 |
| [sub-01_ses-baseline_space-T1w_label-ROI_probseg.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/derivatives/roi/sub-01/ses-baseline/anat/sub-01_ses-baseline_space-T1w_label-ROI_probseg.nii.gz) · [sub-01_ses-followup_space-T1w_label-ROI_probseg.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/derivatives/roi/sub-01/ses-followup/anat/sub-01_ses-followup_space-T1w_label-ROI_probseg.nii.gz) | 基线与随访的派生部分容积分割。值是体素的 ROI 占比，可用于积分体积。以每个掩膜的坐标系为准。 |
| [participants.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/participants.json) · [participants.tsv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/participants.tsv) | 受试对象元数据与标识。 |
| [sub-01_ses-baseline_T1w.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/sub-01/ses-baseline/anat/sub-01_ses-baseline_T1w.json) · [sub-01_ses-followup_T1w.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/sub-01/ses-followup/anat/sub-01_ses-followup_T1w.json) | T1w MRI 采集旁车，包括序列、时间参数和场强。 |
| [sub-01_ses-baseline_T1w.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/sub-01/ses-baseline/anat/sub-01_ses-baseline_T1w.nii.gz) · [sub-01_ses-followup_T1w.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/sub-01/ses-followup/anat/sub-01_ses-followup_T1w.nii.gz) | 基线和随访的 T1w 解剖图像。 |
| [sub-01_sessions.tsv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/03_BIDS_MRI/sub-01/sub-01_sessions.tsv) | 受试对象的会话和采集时间，供纵向连接。 |

### 04_MRS_BIDS

| 项目方文件 | 用途 |
| --- | --- |
| [README](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/README) | 教学示例的项目方说明。上方提供译文。 |
| [dataset_description.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/dataset_description.json) | BIDS 数据集声明。 |
| [participants.tsv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/participants.tsv) | 受试对象元数据与标识。 |
| [sub-01_ses-baseline_acq-press_nuc-1H_voi-frontal_svs.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/sub-01/ses-baseline/mrs/sub-01_ses-baseline_acq-press_nuc-1H_voi-frontal_svs.json) · [sub-01_ses-followup_acq-press_nuc-1H_voi-frontal_svs.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/sub-01/ses-followup/mrs/sub-01_ses-followup_acq-press_nuc-1H_voi-frontal_svs.json) | MRS 采集旁车，包括序列、时间、电磁频率及采集次数。 |
| [sub-01_ses-baseline_acq-press_nuc-1H_voi-frontal_svs.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/sub-01/ses-baseline/mrs/sub-01_ses-baseline_acq-press_nuc-1H_voi-frontal_svs.nii.gz) · [sub-01_ses-followup_acq-press_nuc-1H_voi-frontal_svs.nii.gz](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/sub-01/ses-followup/mrs/sub-01_ses-followup_acq-press_nuc-1H_voi-frontal_svs.nii.gz) | 基线和随访的额叶单体素 PRESS 波谱，复数时域 FID。 |
| [sub-01_sessions.tsv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/04_MRS_BIDS/sub-01/sub-01_sessions.tsv) | 受试对象的会话和采集时间，供纵向连接。 |

### 05_TwinReady_JSON_CSV

| 项目方文件 | 用途 |
| --- | --- |
| [README.md](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/README.md) · [data_contract.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/data_contract.json) · [evidence_packet_v1.0.schema.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/evidence_packet_v1.0.schema.json) · [thresholds-v1.0.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/thresholds-v1.0.json) | 接口说明、下游输入契约、证据包结构验证及质量门控配置。 |
| [features.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/features.csv) · [data_dictionary.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/data_dictionary.csv) · [qc_report.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/qc_report.json) | 宽表特征、字段字典和随访的管线质控报告。 |
| [E-t0-roi.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t0-roi.json) · [E-t0-naa.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t0-naa.json) · [E-t0-cho.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t0-cho.json) | 基线的 ROI 体积、NAA/Cr 和 Cho/Cr 证据包。 |
| [E-t1-roi.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t1-roi.json) · [E-t1-naa.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t1-naa.json) · [E-t1-cho.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t1-cho.json) · [E-t1-chobad.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/packets/E-t1-chobad.json) | 随访的 ROI 体积、NAA/Cr、Cho/Cr 以及刻意构造的 FAIL 比值示例。 |
| [data_contract.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/data_contract.json) · [data_dictionary.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/data_dictionary.csv) · [features.csv](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/features.csv) · [qc_report.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/qc_report.json) | v0.2 的契约、字典、宽表和质控报告，供迁移比较。 |
| [evidence_packet.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/evidence_packet.json) · [evidence_packet_PASS.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/evidence_packet_PASS.json) · [evidence_packet_FAIL.json](../../MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/legacy_v0.2/evidence_packet_FAIL.json) | v0.2 的旧版证据包及具名 PASS／FAIL 示例。 |


[返回中文总入口](index.html)
