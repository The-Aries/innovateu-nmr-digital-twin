# Birmingham 钠离子电池 NMR 数据指南

本指南介绍 Bray 等人在 *Nature Communications* 发表的钠电池研究（2020 年，第 11 卷，文章 2083）。Birmingham 数据库发布了 17 个数据包。指南逐项说明各包的内容，并介绍如何用 Figure 5 演示电池数字孪生的实测更新。 [Birmingham 数据记录](https://edata.bham.ac.uk/456/) · [原论文](https://doi.org/10.1038/s41467-020-15938-x)

## 目录

- [为什么从 Figure 5 开始](#为什么从-figure-5-开始)
- [数据包目录](#数据包目录)
- [Figure 5 的文件结构](#figure-5-的文件结构)
- [数字孪生能验证什么](#数字孪生能验证什么)

## 为什么从 Figure 5 开始

Figure 5 收录了同一块钠离子全电池以 30 mA/g 进行首圈化成时的 **16 次运行中（operando）²³Na NMR 采集**和 **99,841 条电化学数据**。数据包包含原始 NMR 信号、处理后的谱、采集日志和电化学时间序列。原型可以回放这轮实验，并在新谱可用后更新状态估计。 [原论文 Figure 5 和 Methods](https://doi.org/10.1038/s41467-020-15938-x) · [Figure 5 数据包](https://edata.bham.ac.uk/456/4/Figure%5F5.zip)

**60–75 是 Bruker TopSpin 的采集编号（`EXPNO`）。** 每个编号对应同一块全电池的一次谱采集。例如，日志中的原仪器目录分别是 `c_20_2/60` 和 `c_20_2/61`。数据页未说明为何这一组从 60 开始。每次采集持续约 30 分钟。用编号标识采集，用日志时间确定采集窗。 [Bruker TopSpin 处理参考手册](https://nmr.chem.ucsb.edu/docs/Bruker_NMR_Manuals/processing-reference_v007.pdf)

| 采集编号 | 2019 年 11 月 20 日 UTC 开始 | 2019 年 11 月 20 日 UTC 结束 |
|---|---|---|
| 60 | 19:23:08 | 19:52:47 |
| 61 | 19:57:47 | 20:27:20 |

NMR 日志记录绝对 UTC 时间。电化学文件记录经过时间，两套时钟的零点仍是暂定对齐。关联谱和电化学曲线时，使用完整的 NMR 采集窗。事件定时的精度受零点偏移和采集时长限制。

## 数据包目录

数据库按论文图表发布数据。以下说明根据 ZIP 内的文件清单、论文图注和补充材料整理。 [Birmingham 数据记录](https://edata.bham.ac.uk/456/) · [原论文 Figure 1–7](https://doi.org/10.1038/s41467-020-15938-x) · [补充材料](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-15938-x/MediaObjects/41467_2020_15938_MOESM1_ESM.pdf)

### 正文图

| 数据包 | 内容和用途 |
|---|---|
| [Figure_1.zip](https://edata.bham.ac.uk/456/1/Figure%5F1.zip) | 未循环的钠金属电池。包含金属钠和电解液钠的 ²³Na 谱、二维 MRI 和一维空间剖面。 |
| [Figure_2.zip](https://edata.bham.ac.uk/456/2/Figure%5F2.zip) | 钠金属电池完成一次循环后的 ²³Na 谱、二维 MRI 和一维空间剖面。 |
| [Figure_3.zip](https://edata.bham.ac.uk/456/16/Figure%5F3.zip) | 钠金属电池在 150 和 600 mA/g 两个恒流沉积阶段的 ²³Na 谱、二维 MRI 和一维空间剖面。 |
| [Figure_4.zip](https://edata.bham.ac.uk/456/3/Figure%5F4.zip) | 沉积前后各一组三维 ¹H MRI。包含原始采集和 `2dseq` 重建数据。可通过电解液信号变化观察沉积占据的空间。 |
| [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) | 全电池首圈化成的运行中谱序列。包含采集 60–75 和对应的电化学记录。 |
| [Figure_6.zip](https://edata.bham.ac.uk/456/5/Figure%5F6.zip) | 三张选定的 ²³Na 谱。编号 10 是未充电的基准谱，编号 63 和 67 的日志与 Figure 5 对应。论文展示了这些谱的峰拟合。 |
| [Figure_7.zip](https://edata.bham.ac.uk/456/6/Figure%5F7.zip) | 另一块全电池在 86 mA/g 条件下的三张原位（in situ）²³Na 谱，分别采自充至 4.18 V 后、充电结束 4 小时后和放电后。 |

### 补充图表

| 数据包 | 内容和用途 |
|---|---|
| [SupplementaryFigure_2.zip](https://edata.bham.ac.uk/456/15/SupplementaryFigure%5F2.zip) | 钠金属电池前两圈的两份电化学文本。首圈在磁体外以 30 mA/g 运行，第二圈在磁体内以 20 mA/g 运行。 |
| [SupplementaryFigure_3.zip](https://edata.bham.ac.uk/456/14/SupplementaryFigure%5F3.zip) | 两份全电池电化学记录。30 mA/g 的文件与 Figure 5 中的文件内容相同。86 mA/g 的文件对应 Figure 7。 |
| [SupplementaryFigure_4.zip](https://edata.bham.ac.uk/456/13/SupplementaryFigure%5F4.zip) | 未循环和循环后的两组 ²³Na 采集，用于比较溶剂化钠区域的分峰。 |
| [SupplementaryFigure_5.zip](https://edata.bham.ac.uk/456/17/SupplementaryFigure%5F5.zip) | 钠金属电池第二圈的电化学数据，以及循环前、中、后的 ²³Na 谱、二维 MRI 和一维空间剖面。 |
| [SupplementaryFigure_6.zip](https://edata.bham.ac.uk/456/12/SupplementaryFigure%5F6.zip) | 恒流沉积开始和继续沉积后的两组电解液钠谱，用于分峰。 |
| [SupplementaryFigure_7.zip](https://edata.bham.ac.uk/456/11/SupplementaryFigure%5F7.zip) | 恒流沉积开始和继续沉积后的两组金属钠谱，用于分峰。 |
| [SupplementaryFigure_8.zip](https://edata.bham.ac.uk/456/10/SupplementaryFigure%5F8.zip) | 首充早期的三组谱，用于观察金属钠区域。日志对应 Figure 5 的采集 63–65。包内目录与补图图注使用了不同的名义小时标签。 |
| [SupplementaryFigure_9.zip](https://edata.bham.ac.uk/456/9/SupplementaryFigure%5F9.zip) | 硬碳电极的首两圈和倍率性能数据，包含 Excel 工作簿和 Origin 项目。 |
| [SupplementaryFigure_10.zip](https://edata.bham.ac.uk/456/8/SupplementaryFigure%5F10.zip) | 三份 `.mpr` 电化学记录，分别对应硬碳负极半电池、正极半电池和全电池。 |
| [SupplementaryTable_1.zip](https://edata.bham.ac.uk/456/7/SupplementaryTable%5F1.zip) | 四组 Bruker 采集，用于测量金属钠和隔膜中溶解钠的 T₁、T₂ 弛豫参数。 |

## Figure 5 的文件结构

排除 macOS 元数据后，ZIP 共包含 498 个文件。一个是电化学文件，其余 497 个分布在 16 个 `Na_fullSpectrum_*` 文件夹中。每个文件夹对应一次采集，并将两套处理结果分别保存在 `pdata/1` 和 `pdata/2`。 [Figure 5 数据包](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) · [Bruker TopSpin 处理参考手册](https://nmr.chem.ucsb.edu/docs/Bruker_NMR_Manuals/processing-reference_v007.pdf)

| 文件或目录 | 作用 |
|---|---|
| `Electrochemistry_30mAhg-1.txt_1` | 无表头文本。根据数值范围和论文中的电化学曲线，三列解读为经过时间（s）、电流（A）和端电压（V）。 |
| `fid` | 原始 NMR 时域信号。 |
| `acqu`、`acqus` | 采集设置和采集时记录的参数。用 `acqus` 核对该次采集使用的参数。 |
| `audita.txt` | 采集日志，记录 UTC 起止时间和仪器路径。 |
| `pulseprogram`、`fq1list` | 脉冲序列和频率列表。该包只在编号 60 中提供了 `fq1list`。 |
| `format.temp`、`preemp_default_T121292_00024`、`scon2`、`shimvalues`、`specpar`、`uxnmr.info`、`uxnmr.par` | 参数界面、探头与仪器配置、匀场值等辅助文件。 |
| `pdata/1/1r`、`pdata/1/1i`、`pdata/2/1r`、`pdata/2/1i` | 两套处理谱的实部和虚部。当前 Birmingham Explorer 使用处理编号 2。 |
| `proc`、`procs`、`auditp.txt`、`base_info`、`outd`、`assocs` | 位于处理目录内，记录处理设置和实际参数、处理日志、显示和数据关联信息。 |
| `title`、`thumb.png`、`parm.txt` | 位于处理目录内，分别保存标题、缩略图和可读的参数导出。仅采集 62 的两套处理结果含 `parm.txt`。 |

## 数字孪生能验证什么

1. **回放外部实测。** 用电流和端电压跟踪电池的化成过程。
2. **更新内部状态估计。** 每当一张谱可用，提取金属钠谱区的相对面积、峰位和检出状态。谱质量通过检查时，用该观测更新估计。
3. **追溯每一次更新。** 随更新保存采集编号、UTC 采集窗、处理版本、谱指标的不确定度和暂定的时钟偏移。

原论文报告，首充早期的金属钠峰在约 1050 ppm 出现，随后向 1115 ppm 移动并降到检测水平以下。这为原型提供了可核对的实测变化。Figure 6 补充未充电基准谱，Figure 7 提供另一充电工况下的对照。 [原论文 Figure 5–7](https://doi.org/10.1038/s41467-020-15938-x)

Figure 5 支持**一块电池、一个循环的离线回放和实测驱动的状态更新**。谱积分提供相对金属钠信号。绝对钠质量需要标定，空间形貌需要成像，跨电池预测需要独立验证。
