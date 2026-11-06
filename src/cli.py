"""
图片暗黑模式转换器 - M1 核心算法原型

功能：
- 自动分类图片（A类：文字/图形，B类：照片/绘画）
- A类：全图反色（背景/前景统一 255-x）
- B类：色调映射（降亮度 + 降饱和度）
- 支持批量处理
- 支持多种图片格式（PNG, JPEG, WebP, GIF）

用法：
    python src/cli.py --input <image> --output <image.dark.png> [--type auto|text|photo]
    python src/cli.py --batch <input_dir> --output-dir <output_dir>
"""

import argparse
import sys
from pathlib import Path

# 确保 src/ 在模块搜索路径中，使同级 import 生效
sys.path.insert(0, str(Path(__file__).parent))

# 类型参数到类别字母的映射
TYPE_MAP = {
    'auto': 'auto',
    'text': 'A',
    'photo': 'B',
}


def main():
    parser = argparse.ArgumentParser(description='图片暗黑模式转换器')
    parser.add_argument('--input', '-i', help='输入图片路径')
    parser.add_argument('--output', '-o', help='输出图片路径（不填则自动生成 <name>.dark.<ext>）')
    parser.add_argument('--type', '-t', choices=['auto', 'text', 'photo'], default='auto',
                        help='图片类型：auto=自动分类，text=A类（文字/图形），photo=B类（照片）')
    parser.add_argument('--intensity', '-I', choices=['light', 'medium', 'strong'], default='medium',
                        help='变暗强度：light=柔和，medium=标准，strong=强力')
    parser.add_argument('--batch', '-b', help='批量处理目录')
    parser.add_argument('--output-dir', help='批量处理输出目录')

    args = parser.parse_args()

    if args.batch and args.output_dir:
        _batch_mode(args)
    elif args.input:
        _single_mode(args)
    else:
        parser.print_help()
        sys.exit(1)


def _single_mode(args):
    """单文件处理"""
    from processor import ImageProcessor
    processor = ImageProcessor(intensity=args.intensity)
    category = TYPE_MAP[args.type]
    output_path = processor.process(
        image_path=args.input,
        category=category,
        output_path=args.output,
    )
    print(f"处理完成: {output_path}")


def _batch_mode(args):
    """批量处理"""
    from processor import ImageProcessor
    processor = ImageProcessor(intensity=args.intensity)
    processor.batch_process(
        input_dir=args.batch,
        output_dir=args.output_dir,
        category=TYPE_MAP[args.type],
        intensity=args.intensity,
    )


if __name__ == '__main__':
    main()