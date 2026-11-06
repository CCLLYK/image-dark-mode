"""
image-dark-mode - 图片暗黑模式自动转换器

解决暗黑模式下"图片刺眼"问题：当用户处于暗黑模式时，网页/电子书/APP 中的图片也能自动切换为暗黑版本。

功能：
- A 类（文字/图形类）：流程图、示意图、图表 → 精确重着色
- B 类（照片/绘画类）：照片、插画 → 色调映射

用法：
    # 单文件处理
    python src/cli.py --input <image> --output <image.dark.png>

    # 批量处理
    python src/cli.py --batch <input_dir> --output-dir <output_dir>

    # 指定图片类型和强度
    python src/cli.py --input <image> --type text --intensity strong
"""

__version__ = '0.1.0'
__author__ = 'image-dark-mode'