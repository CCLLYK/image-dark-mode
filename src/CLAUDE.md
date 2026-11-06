# src/ — 核心算法与工具源码

本目录存放项目的所有核心实现代码，是 image-dark-mode 的核心逻辑所在。

## 模块清单

| 文件 | 说明 |
|------|------|
| `__init__.py` | 包初始化，定义版本号和作者信息 |
| `cli.py` | 命令行入口，解析参数并调度处理流程 |
| `classifier.py` | 图片分类器：基于启发式特征自动识别 A 类（文字/图形）或 B 类（照片/绘画） |
| `processor.py` | 图片处理器：A 类精确重着色 / B 类色调映射，支持批量处理 |

## 核心类

- **`ImageClassifier`** (`classifier.py`)
  - 方法：`classify(image_path)` → `(category, features)`
  - 提取特征：白色比例、低饱和度比例、边缘密度、颜色数量、宽高比等
  - 决策逻辑：评分加权，A/B 两类默认阈值见 `__init__` 中的常量

- **`ImageProcessor`** (`processor.py`)
  - 方法：`process(image_path, category='auto', output_path=None)` → `output_path`
  - 方法：`batch_process(input_dir, output_dir, category='auto', intensity='medium')`
  - 强度档位：`light` / `medium` / `strong`，参数见 `_get_params`

## 依赖

- `PIL` (Pillow) — 图像处理
- `numpy` — 数值计算
- `opencv-python` (`cv2`) — B 类 HSV 色调映射

## 编码约定

- 中文注释为主，技术名词保留英文
- 所有公开方法需有 docstring
- 新增功能先更新对应 docstring 中的功能列表
- 算法参数调整需记录在 `docs/` 下，避免只存在于代码注释中
