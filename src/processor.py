"""
图片处理器

功能：
- A 类图片处理：背景反色 + 文字/线条颜色重映射
- B 类图片处理：色调映射（降亮度 + 降饱和度 + 深色叠加）
- 支持多种图片格式（PNG, JPEG, WebP, GIF）
- 支持批量处理
"""

from typing import Optional
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import cv2


class ImageProcessor:
    """图片处理器：根据类别应用不同的暗黑模式转换策略"""

    # 默认参数
    DEFAULT_A_CLASS_WEIGHT = 0.95  # A 类背景反色强度
    DEFAULT_B_CLASS_BRIGHTNESS = 0.7  # B 类亮度降低因子
    DEFAULT_B_CLASS_SATURATION = 0.6  # B 类饱和度降低因子

    def __init__(self, intensity: str = 'medium'):
        """
        初始化处理器

        Args:
            intensity: 变暗强度 ('light', 'medium', 'strong')
        """
        self.intensity = intensity
        self._params = self._get_params(intensity)

    def _get_params(self, intensity: str) -> dict:
        """根据强度获取参数"""
        params_map = {
            'light': {
                'a_class_weight': 0.85,
                'b_brightness': 0.85,
                'b_saturation': 0.8,
            },
            'medium': {
                'a_class_weight': 0.95,
                'b_brightness': 0.7,
                'b_saturation': 0.6,
            },
            'strong': {
                'a_class_weight': 1.0,
                'b_brightness': 0.5,
                'b_saturation': 0.4,
            },
        }
        return params_map.get(intensity, params_map['medium'])

    def process(self, image_path: str, category: str = 'auto',
                output_path: Optional[str] = None) -> str:
        """
        处理图片，生成暗黑版

        Args:
            image_path: 输入图片路径
            category: 图片类别 ('auto', 'A', 'B')
            output_path: 输出路径（可选，默认为 input.dark.ext）

        Returns:
            输出文件路径
        """
        # 打开图片
        img = Image.open(image_path)

        # 自动分类
        if category == 'auto':
            from classifier import ImageClassifier
            classifier = ImageClassifier()
            category, features = classifier.classify(image_path)
            print(f"分类结果: {category} (特征: {features})")

        # 根据类别处理
        if category == 'A':
            dark_img = self._process_class_a(img)
        else:  # B 类
            dark_img = self._process_class_b(img)

        # 确定输出路径
        if output_path is None:
            output_path = self._generate_output_path(image_path)

        # 保存图片
        self._save_image(dark_img, output_path, image_path)

        return output_path

    def _process_class_a(self, img: Image.Image) -> Image.Image:
        """
        A 类处理：全图反色
        - 所有像素统一执行 255 - x，白底变黑底，浅灰文字变中亮灰
        - 保留透明度通道
        """
        # 转 numpy 数组
        arr = np.array(img)

        # 分离 RGB 通道
        if arr.shape[-1] == 4:  # RGBA
            r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
        else:  # RGB
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            a = None

        # 全图反色
        r_dark = 255 - r
        g_dark = 255 - g
        b_dark = 255 - b

        # 合并通道
        result = np.stack([r_dark, g_dark, b_dark], axis=-1).astype(np.uint8)

        # 恢复透明度
        if a is not None:
            result = np.concatenate([result, a[:, :, np.newaxis]], axis=-1)

        return Image.fromarray(result)

    def _process_class_b(self, img: Image.Image) -> Image.Image:
        """
        B 类处理：色调映射
        - 降亮度
        - 降饱和度
        - 深色叠加
        """
        # 转 RGB（如果包含透明度通道，先合成背景）
        if img.mode == 'RGBA':
            # 创建黑色背景并合成
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[3])
            img_rgb = np.array(background)
        else:
            img_rgb = np.array(img.convert('RGB'))

        # 转 HSV 颜色空间
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

        # 降亮度
        v = v * self._params['b_brightness']

        # 降饱和度
        s = s * self._params['b_saturation']

        # 合并通道并转回 RGB
        hsv_dark = np.stack([h, s, v], axis=-1).astype(np.uint8)
        img_dark = cv2.cvtColor(hsv_dark, cv2.COLOR_HSV2RGB)

        return Image.fromarray(img_dark)

    @staticmethod
    def _generate_output_path(input_path: str) -> str:
        """生成输出路径（input.dark.ext）"""
        path = Path(input_path)
        return str(path.parent / f"{path.stem}.dark{path.suffix}")

    @staticmethod
    def _save_image(img: Image.Image, output_path: str, input_path: str):
        """保存图片，保持原格式"""
        input_path_obj = Path(input_path)
        output_path_obj = Path(output_path)

        # 如果是 GIF，保留动画
        if input_path_obj.suffix.lower() == '.gif':
            # 简化处理：只保存第一帧
            img.save(output_path, save_all=True, append_images=[])
        else:
            img.save(output_path)

    def batch_process(self, input_dir: str, output_dir: str,
                      category: str = 'auto', intensity: str = 'medium'):
        """
        批量处理

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            category: 图片类别
            intensity: 变暗强度
        """
        from pathlib import Path
        import glob

        # 支持的图片格式
        patterns = ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif', '*.bmp']

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        processed = 0
        skipped = 0
        for pattern in patterns:
            for img_file in input_path.glob(pattern):
                # 跳过已经处理过的暗黑版文件（避免二次处理）
                if '.dark' in img_file.stem:
                    skipped += 1
                    continue
                print(f"处理: {img_file.name}")
                try:
                    output_file = output_path / f"{img_file.stem}.dark{img_file.suffix}"
                    self.process(str(img_file), category, str(output_file))
                    processed += 1
                except Exception as e:
                    print(f"处理失败 {img_file.name}: {e}")

        print(f"\n批量处理完成：成功 {processed} 张，跳过 {skipped} 个已处理的暗黑版文件")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("用法: python processor.py <input_image> [output_image] [category]")
        sys.exit(1)

    processor = ImageProcessor()
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    category = sys.argv[3] if len(sys.argv) > 3 else 'auto'

    result = processor.process(input_path, category, output_path)
    print(f"输出: {result}")