# 校园地图归档 · 2026-11-07

本目录按要求保存 **16 张区域小图、1 张拼接整图和1张学校原始底图**。

## 打开图片

- [16 张区域小图](regions/)：全部保留原始 PNG 字节，未缩小、未重新压缩。
- [拼接整图，8192 × 4912](stitched/campus-unified-review-full-8192-view.jpg)：可直接打开的同分辨率 JPEG 查看副本。
- [学校原始大图，2048 × 1228](original/south_campus_map_2025.jpg)：2025 年 6 月版南校区官方平面图，原文件未改动。

## 整图原始质量与版本

拼接整图来自 2026-11-06 保存的 `campus-unified-review-full-8192.png`，是**拼接审核版**，不是最新游戏画面的截图，也不表示全部道路和接缝已经验收。之后游戏里的局部补绘、删字、通行修复不反向改写这个历史归档。

原始 PNG 为 **49,218,541 字节（8192 × 4912）**。上传通道有单次大小限制，因此它以 [6 个连续二进制分卷](stitched/png-original-parts/) 完整保存。这不是图片裁切，按顺序合并后与原始 PNG **逐字节相同**。

查看副本是 JPEG，质量参数 90、4:4:4、不缩小尺寸。JPEG 有损压缩，不能代替无损原件；原 PNG 的全部数据保留在分卷里。

下载本文件夹后，在本目录运行：

```sh
python3 restore_full_png.py
```

脚本不联网，先校验所有分卷，再生成 `stitched/campus-unified-review-full-8192.png`，并校验原图 SHA-256：

```
825171d4e05892fcc04587834e106cf6c45b6474da23324bafc5af30ab604e01
```

## 区域清单

| 编号 | 区域 | 原始尺寸 |
| --- | --- | --- |
| 01 | [化工学院周边](regions/01-chemistry-quarter-style-sample-v1.png) | 1600 × 1260 |
| 02 | [三号教学楼与学苑餐厅](regions/02-teaching3-dining-style-sample-v1.png) | 1768 × 890 |
| 03 | [第一图书馆与中央教学区](regions/03-library-central-style-sample-v1.png) | 1477 × 1065 |
| 04 | [西部学院与南月湖](regions/04-west-colleges-style-sample-v1.png) | 1488 × 1057 |
| 05 | [南门与南月湖](regions/05-south-lake-style-sample-v1.png) | 1334 × 1179 |
| 06 | [西区运动场与历史文化园](regions/06-west-sports-history-style-sample-v1.png) | 1236 × 1272 |
| 07 | [东区运动场](regions/07-east-sports-style-sample-v1.png) | 1063 × 1479 |
| 08 | [第二图书馆与清涟湖](regions/08-second-library-style-sample-v1.png) | 1474 × 1067 |
| 09 | [学生生活区](regions/09-student-life-style-sample-v1.png) | 1613 × 975 |
| 10 | [教工住宅与北部生活区](regions/10-staff-residences-style-sample-v1.png) | 1774 × 887 |
| 11 | [东部工程实训区](regions/11-engineering-style-sample-v1.png) | 1572 × 1001 |
| 12 | [东南教学与未来区](regions/12-southeast-style-sample-v1.png) | 1504 × 1046 |
| 13 | [西南科研片区](regions/13-southwest-research-style-sample-v1.png) | 1685 × 933 |
| 14 | [东区教学楼群](regions/14-east-teaching-style-sample-v1.png) | 1606 × 979 |
| 15 | [西北生态绿地](regions/15-northwest-green-style-sample-v1.png) | 1774 × 887 |
| 16 | [东北生态绿地](regions/16-northeast-green-style-sample-v1.png) | 1663 × 946 |

前三张原始文件名没有编号，本归档仅补充了 01、02、03 文件名前缀；内容不变。原文件名、尺寸、字节数和 SHA-256 均记录于 [manifest.json](manifest.json)。

## 来源与使用边界

- 16 张小图：2026-11-05 制作并保存的校园分区风格样图 v1。
- 拼接大图：2026-11-06 保存的全图审核文件。
- 学校原始大图：[河南理工大学党委宣传部《学校平面图（南、北校区）》](https://xcb.hpu.edu.cn/info/1007/2435.htm)，2025-09-05 发布，图示 2025 年 6 月版。
- 官方地图反映其标注版本，不保证涵盖之后的校园变化。公开下载不等于开放许可，原权利归属不变；再使用授权未核实。
- 本次只归档图片及配套清单，不改动游戏代码、部署或地图通行范围。
