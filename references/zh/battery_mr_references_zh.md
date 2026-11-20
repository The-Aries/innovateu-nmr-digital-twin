# 电池磁共振：文献与数据来源

InnovateU Hackathon 2026，NMR Quantum Engineering 挑战。检索日期：2026-11-20。

## 目录

- [摘要](#摘要)
- [如何使用这些来源](#如何使用这些来源)
- [A. 测量物理](#a-测量物理)
- [B. 快充与析锂](#b-快充与析锂)
- [C. 可下载的数据](#c-可下载的数据)
- [D. 测量模型的关键数值](#d-测量模型的关键数值)
- [E. 核实状态](#e-核实状态)

## 摘要

- 公开的电池 MRI 原始数据几乎不存在。主要的 MRI 论文写的是"可向通讯作者合理索取"，或者没有数据声明。
- 只确认了一个公开的 ⁷Li NMR 原始数据集：Cambridge Apollo，DOI 10.17863/CAM.46593（CC BY-NC-SA 4.0）。它研究的是 SEI 与金属锂的界面，不是快充析锂。
- 建议做法：从文献中取物理参数和数值范围，自己生成已知真值的合成数据；用公开的电池循环数据集确定退化趋势和过程噪声。
- 不得使用 BMW 或其子公司的任何内部数据或参数。挑战只允许合成、公开或去标识的数据。

## 如何使用这些来源

| 需求 | 来源 | 章节 |
|---|---|---|
| 测量模型：化学位移、趋肤深度、形貌混淆 | Benders 2020、Bhattacharyya 2010、Trease/Köster/Grey 综述 | [A](#a-测量物理) |
| 替代观测：电池周围的磁场图（SOC、缺陷） | Ilott 2018、Romanenko & Jerschow 2019 | [A](#a-测量物理) |
| 快充析锂情景和起点检测 | Märker/Xu/Grey、McMaster 团队、HAL 0 °C 研究 | [B](#b-快充与析锂) |
| 真实的 ⁷Li 噪声、线宽和峰形 | Apollo 数据集（Hope et al. 2020） | [C](#c-可下载的数据) |
| 容量衰减趋势、先验和过程噪声 Q | Severson 2019、NASA PCoE、CALCE | [C](#c-可下载的数据) |
| pitch 中的局限说明 | RSC Sustainable Energy & Fuels 2025 | [B](#b-快充与析锂) |

所有生成的数据标记为 `SIMULATED`，并记录每个参数参考了哪篇文献。

## A. 测量物理

| 文献 | 提供的内容 | 数据 |
|---|---|---|
| Bhattacharyya R, Key B, Chen H, et al. In situ NMR observation of the formation of metallic lithium microstructures in lithium batteries. *Nat Mater* 9:504–510 (2010). [doi:10.1038/nmat2764](https://dx.doi.org/10.1038/nmat2764) | 原位 ⁷Li NMR 对金属锂做时间分辨的定量测量。利用 RF 趋肤深度和体磁化率区分苔藓状（高比表面积）和致密沉积。 | 未找到 |
| Chandrashekar S, Trease NM, Chang HJ, Du LS, Grey CP, Jerschow A. ⁷Li MRI of Li batteries reveals location of microstructural lithium. *Nat Mater* 11:311–315 (2012). doi:10.1038/nmat3246（[记录](https://ouci.dntb.gov.ua/works/4NoNmwYl)）。Dossier 参考文献 [41]。 | ⁷Li MRI 定位电池内的锂微结构（枝晶）。 | 未找到 |
| Benders S, Mohammadi M, Klug CA, Jerschow A. Nuclear magnetic resonance spectroscopy of rechargeable pouch cell batteries: beating the skin depth by excitation and detection via the casing. *Sci Rep* 10:13781 (2020). [PMC7426951](https://pmc.ncbi.nlm.nih.gov/articles/PMC7426951/) | 商用 600 mAh 石墨/NMC 软包电池的 ⁷Li NMR，用电池外壳作 RF 线圈。9.4 T，155.5 MHz。化学位移：电解液 Li ≈ 0 ppm，金属 Li ≈ 260 ppm，石墨嵌锂 ≈ 30 ppm。 | 无声明 |
| Ilott AJ, Mohammadi M, Schauerman CM, Ganter MJ, Jerschow A. Rechargeable lithium-ion cell state of charge and defect detection by in-situ inside-out magnetic resonance imaging. *Nat Commun* 9:1776 (2018). [PMC5934497](https://pmc.ncbi.nlm.nih.gov/articles/PMC5934497/)。Dossier 参考文献 [42]。 | inside-out MRI：对电池周围的水做 ¹H MRI，得到磁化率引起的磁场分布，从而反映 SOC 和缺陷。9.4 T，各向同性分辨率 400 µm，跨电池场变化 1–2 ppm，可分辨差异约 0.1 ppm。 | 按需索取 |
| Romanenko K, Jerschow A. Distortion-free inside-out imaging for rapid diagnostics of rechargeable Li-ion cells. *PNAS* 116:18783–18789 (2019). [PMC6754580](https://pmc.ncbi.nlm.nih.gov/articles/PMC6754580/) | 基于 SPRITE 的商用电池 inside-out 成像，包括损坏的手机电池。分辨率约 1 mm；充电使磁场变化最多约 4 ppm。 | 未找到 |
| Trease NM, Köster TKJ, Grey CP. In situ NMR studies of lithium ion batteries. *Electrochem Soc Interface*（2011 秋季刊）。[PDF](https://www.electrochem.org/dl/interface/fal/fal11/fal11_p069-073.pdf) | 趋肤深度：在 77 MHz 下只有金属锂表层约 15 µm 能被激发。 | — |
| Pecher O, Carretero-González J, Griffith KJ, Grey CP. Materials' methods: NMR in battery research. *Chem Mater* 29:213 (2017). doi:10.1021/acs.chemmater.6b03183（[Apollo](https://www.repository.cam.ac.uk/handle/1810/262008)） | 原位和非原位电池 NMR 方法综述。适合作为 measurement card 的入门资料。 | — |
| Hu Y, Iwata GZ, Mohammadi M, et al. Sensitive magnetometry reveals inhomogeneities in charge storage and weak transient internal currents in Li-ion cells. *PNAS* 117:10667–10672 (2020). [PMC7245122](https://pmc.ncbi.nlm.nih.gov/articles/PMC7245122/) | 不是 NMR：用原子磁力计测量软包电池周围的磁场（局部 SOC、内部电流）。可作为"下一次测量"的候选模态。 | OSF（见 C） |

## B. 快充与析锂

- **Märker K, Xu C, Grey CP.** Operando NMR of NMC811/graphite lithium-ion batteries: structure, dynamics, and lithium metal deposition. [Apollo 记录](https://www.repository.cam.ac.uk/items/f6f318ad-cb57-4fa5-b843-9df7e4ac478e)。全电池中的 operando ⁷Li NMR，包括金属锂沉积。与"快充是否仍然安全"最贴近。
- **Krachkovskiy et al., *J Electrochem Soc* 2020。** [记录](https://experts.mcmaster.ca/scholarly-works/3593110)。在由拆解的商用 EV 电极制成的单层电池中原位监测石墨上的锂沉积；区分表面膜和枝晶。
- **Sanders et al., *Carbon* 2022。** [记录](https://experts.mcmaster.ca/scholarly-works/2159077)。石墨/NMC622 在 ≥1C 下直接转变为高浓度 LixC6 相，锂在石墨表面累积，促进析锂。
- **Sadighi et al. 2025（预印本，未经同行评审）。** [ChemRxiv](https://chemrxiv.org/engage/chemrxiv/article-details/6827763050018ac7c58c6726)。快充时对 SiO–石墨负极同时做 operando ⁷Li NMR 和三电极电化学；估计可逆析锂的比例。
- **0 °C 下的 operando ⁷Li NMR，NMC622/石墨。** [HAL 04272140](https://hal.archives-ouvertes.fr/hal-04272140)。检测快充时亚稳态锂沉积的起点。
- **商用软包电池的拆解研究，*Sustainable Energy & Fuels* 2025。** [PDF](https://pubs.rsc.org/en/content/articlepdf/2025/se/d5se00509d)。对石墨–SiOx/NMC 电池做 ⁷Li NMR + ICP-OES + SEM。文中指出，由于商用电池的结构，原位方法无法用于商用电池。可用于局限说明。

## C. 可下载的数据

| 数据集 | 内容 | 许可 | 用途 |
|---|---|---|---|
| Apollo，[doi:10.17863/CAM.46593](https://www.repository.cam.ac.uk/handle/1810/304633)。Hope et al., *Nat Commun* 11:2224 (2020) 的支撑数据 | `Li_DNP_NMR_data.zip`，60.7 MB：¹H、⁷Li、¹⁹F 的 FID、谱图和元数据，TopSpin 格式 | CC BY-NC-SA 4.0 | 唯一确认公开的 ⁷Li 原始 FID。可作为噪声、线宽和峰形的参照。研究主题是 DNP/SEI，不是快充析锂。 |
| OSF [cw8zv](https://osf.io/cw8zv/)，Hu et al. 2020 引用 | 磁力计数据（软包电池周围的磁场） | 未知 | 内容未核实；需要用浏览器打开。 |
| Severson KA et al., Data-driven prediction of battery cycle life before capacity degradation. *Nat Energy* 4:383 (2019). [doi:10.1038/s41560-019-0356-8](https://www.doi.org/10.1038/S41560-019-0356-8)；数据位于 data.matr.io/1 | 124 个 LFP/石墨电池，72 种快充协议，寿命约 150–2,300 次循环，以 80% 容量为寿命终点 | 公开 | 容量衰减先验和过程噪声 Q |
| [NASA PCoE 数据库](https://www.nasa.gov/Intelligent-Systems-Division/Discovery-and-Systems-Health/Pcoe/Pcoe-Data-Set-Repository/) | 不同温度下的锂离子老化数据；充电、放电和阻抗曲线 | 按数据集确认 | 同上 |
| [CALCE 电池数据](https://calce.umd.edu/data) | 循环、存储、OCV 和阻抗数据 | 需要引用 | 同上 |
| [Battery Imaging Library](https://zenodo.org/records/17011440) | 18650 电池的 X 射线 micro-CT（不是 MRI） | 公开 | 候选的交叉验证模态 |

## D. 测量模型的关键数值

| 量 | 数值 | 来源 |
|---|---|---|
| ⁷Li 旋磁比 γ/2π | ≈ 16.55 MHz/T | 标准常数 |
| 2.895 T（StarterPack 场强）下的 ⁷Li 频率 | ≈ 47.9 MHz | 推导：16.55 × 2.895 |
| 电解液 / 抗磁性 Li 的化学位移 | ≈ 0 ppm | Benders 2020 |
| 金属 Li 的位移（Knight shift） | ≈ 260 ppm | Benders 2020 |
| 石墨嵌锂的位移 | ≈ 30 ppm | Benders 2020 |
| 金属锂中的 RF 趋肤深度 | 77 MHz 下约 15 µm；频率越低越深 | Trease/Köster/Grey 2011 |
| 跨电池的磁化率场变化 | 1–2 ppm；约 0.1 ppm 可分辨 | Ilott 2018 |
| 充电引起的场变化 | 最多约 4 ppm | Romanenko & Jerschow 2019 |

主要混淆因素：金属锂信号与可被激发的表面（趋肤深度）成正比，而不只是与质量成正比。信号增加可能来自形貌变化（苔藓状锂对比致密锂），而不是析锂量增加。其他混淆因素：测量时的 SOC 和温度、电池相对 B0 的朝向、线圈调谐。

## E. 核实状态

- 已全文或大部分阅读：Benders 2020、Ilott 2018、Romanenko & Jerschow 2019、Hu 2020（PMC 页面），以及 Apollo 数据集页面。
- 未阅读全文：Bhattacharyya 2010、Chandrashekar 2012、Märker/Xu/Grey 和 McMaster 的几篇论文。其定量方法和数值在此未确认。
- Hu 2020 的数据声明（OSF）来自对 PMC 页面的模型摘要，不是逐字阅读。
- NASA 和 CALCE 的下载链接未测试。
- Sadighi 2025 是预印本。
