# 《攀龙》LoRA训练素材包

## 概述

为6位核心角色准备了完整的LoRA训练素材包，用于AI视频生成工具的角色一致性训练。
LoRA微调可将角色跨镜头一致性从参考图方案的60-75%提升至90%+。

---

## 训练素材包清单

| 角色 | 目录 | 图片数 | 用途 |
|------|------|--------|------|
| 宓之（女主） | `mizhi_pack/` | 17张 | 核心角色，全剧出场最多 |
| 宗凛（男主） | `zonglin_pack/` | 17张 | 核心角色，全剧出场最多 |
| 薛氏（二夫人） | `xueshi_pack/` | 17张 | 主要反派 |
| 王妃 | `wangfei_pack/` | 20张 | 关键角色，含轮椅动作 |
| 定安王 | `dinganwang_pack/` | 17张 | 权力核心角色 |
| 俞氏 | `yushi_pack/` | 17张 | 重要配角 |

**总计：105张训练图片**

---

## 每位角色素材构成

### 标准构成（17张/角色）
- **三视图**（3张）：正面、侧面、背面 — 提供基础面部和体型参考
- **表情表**（1张）：6种核心情绪 — 提供表情变化参考
- **动作参考**（6张）：行走、跪拜、切菜、惊退、深情、行礼等 — 提供动作姿态参考
- **4K角色设定图**（1张）：全身形象参考
- **服装设定图**（1张）：服装细节参考
- **LoRA补充角度**（5张）：
  - 45度侧面暖光 — 补充非正侧面角度
  - 低头/仰头 — 补充非平视角度
  - 逆光 — 补充极端光照条件
  - 冷光 — 补充不同色温光照
  - 全身/半身 — 补充不同构图

### 王妃特殊构成（20张）
- 标准17张 + 3张修正版轮椅图（正面/侧面/动作）

---

## LoRA训练参数建议

### 推荐工具
- **即梦AI 3.0**：内置角色ID机制，支持上传参考图训练，亚洲人脸一致性95%+
- **可灵AI 2.0**：多图参考模型，角色一致性评分91.3分
- **Stable Diffusion + Kohya_ss**：开源方案，完全可控，需GPU算力

### 训练参数
| 参数 | 建议值 | 说明 |
|------|--------|------|
| 学习率 (Learning Rate) | 1e-4 ~ 3e-4 | 过高导致过拟合，过低训练不充分 |
| 训练步数 (Training Steps) | 1000-1500步 | 17张素材建议1200步 |
| 批次大小 (Batch Size) | 1-2 | 取决于GPU显存 |
| 分辨率 | 512×768 或 768×1024 | 匹配目标视频分辨率 |
| 文本编码器 | CLIP ViT-L/14 | 标准配置 |

### 验收标准
训练完成后生成测试集（至少10张不同姿态的图片），验收标准：
1. 五官核心特征一致（误差<2像素）
2. 服装颜色和款式稳定
3. 发型和发色一致
4. 5种不同光照下保持稳定
5. 正面、侧面、背面均能识别为同一角色

---

## 角色触发词（Trigger Words）

在LoRA训练时，需要为每个角色设定唯一的触发词：

| 角色 | 触发词 | 英文描述 |
|------|--------|---------|
| 宓之 | `mizhi_pl` | 20yo Chinese woman, almond eyes, oval face, light blue hanfu, wooden hairpin |
| 宗凛 | `zonglin_pl` | 25yo Chinese nobleman, sharp jawline, deep eyes, dark blue hanfu, silver crown |
| 薛氏 | `xueshi_pl` | 28yo Chinese noblewoman, beautiful shrewd, deep red hanfu, gold embroidery |
| 王妃 | `wangfei_pl` | 50yo Chinese princess consort, purple hanfu, phoenix crown, wooden wheelchair |
| 定安王 | `dinganwang_pl` | 55yo Chinese prince, dignified, brown hanfu, dragon embroidery, gray beard |
| 俞氏 | `yushi_pl` | 22yo Chinese gentlewoman, soft oval face, pink hanfu, yingluo necklace |

---

## 文件目录结构

```
lora_training/
├── mizhi_pack/          # 宓之训练包 (17张)
├── zonglin_pack/        # 宗凛训练包 (17张)
├── xueshi_pack/         # 薛氏训练包 (17张)
├── wangfei_pack/        # 王妃训练包 (20张)
├── dinganwang_pack/     # 定安王训练包 (17张)
├── yushi_pack/          # 俞氏训练包 (17张)
└── LoRA训练说明.md      # 本文件
```

---

## 训练后使用流程

1. 将训练好的LoRA模型导入视频生成工具
2. 在提示词中使用角色触发词 + 场景描述
3. 每个镜头生成时自动调用LoRA，确保角色一致性
4. 配合首尾帧控制（即梦AI）或Character Lock（Runway）进一步稳定

## 预期效果

- 角色跨镜头一致性：**≥90%**（LoRA方案 vs 参考图方案60-75%）
- 跨集一致性：**≥85%**（配合角色资产管理系统）
- 训练时间：每角色约5-8小时（GPU依赖）
- 训练完成后可跨项目复用
