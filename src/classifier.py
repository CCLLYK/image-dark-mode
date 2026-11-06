"""
图片分类器

功能：
- 基于启发式规则自动分类图片为 A 类（文字/图形）或 B 类（照片/绘画）
- 特征：颜色数量、近白/近黑像素比例、边缘密度、饱和度分布、文件大小/尺寸比
"""

from typing import Tuple
import numpy as np
from PIL import Image


class ImageClassifier:
    """图片分类器：判断图片属于 A 类（文字/图形）还是 B 类（照片/绘画）"""

    def __init__(self):
        # 分类阈值（可调整）
        self.WHITESATURATION_THRESHOLD = 0.15  # 白色/浅色像素比例
        self.SATURATIONSATURATION_THRESHOLD = 0.05  # 低饱和度像素比例
        self.EDGECOUNT_THRESHOLD = 0.3  # 边缘密度
        self.COLORCOUNT_THRESHOLD = 50  # 颜色数量

    def classify(self, image_path: str) -> Tuple[str, dict]:
        """
        分类图片

        Args:
            image_path: 图片路径

        Returns:
            (类别, 特征字典)
            类别: 'A' 表示文字/图形，'B' 表示照片/绘画
        """
        img = Image.open(image_path)
        img_array = np.array(img)

        # 计算特征
        features = self._extract_features(img_array)

        # 分类决策
        category = self._decide_category(features)

        return category, features

    def _extract_features(self, img_array: np.ndarray) -> dict:
        """提取图片特征"""
        # 转 RGB（如果包含透明度通道）
        if img_array.shape[-1] == 4:
            img_rgb = img_array[:, :, :3]
        else:
            img_rgb = img_array[:, :, :3]

        # 计算颜色统计
        mean_color = np.mean(img_rgb, axis=(0, 1))
        std_color = np.std(img_rgb, axis=(0, 1))

        # 计算白色/浅色像素比例
        white_pixels = np.sum(img_rgb > 200, axis=2) == 3
        white_ratio = np.sum(white_pixels) / img_rgb.shape[0] / img_rgb.shape[1]

        # 计算低饱和度像素比例（灰度图特征）
        hsv = self._rgb_to_hsv(img_rgb)
        saturation = hsv[:, :, 1]
        low_saturation_pixels = np.sum(saturation < 0.1)
        low_saturation_ratio = low_saturation_pixels / img_rgb.shape[0] / img_rgb.shape[1]

        # 估计颜色数量（通过量化）
        quantized = np.round(img_rgb / 32).astype(int)  # 降采样到 8^3 = 512 色
        unique_colors = len(np.unique(quantized.reshape(-1, 3), axis=0))

        # 计算边缘密度（简单 Sobel 边缘检测）
        edges = self._detect_edges(img_rgb)
        edge_density = np.mean(edges)

        # 计算宽高比
        aspect_ratio = img_rgb.shape[1] / img_rgb.shape[0]

        return {
            'width': img_rgb.shape[1],
            'height': img_rgb.shape[0],
            'aspect_ratio': aspect_ratio,
            'white_ratio': white_ratio,
            'low_saturation_ratio': low_saturation_ratio,
            'unique_colors': unique_colors,
            'edge_density': edge_density,
            'mean_brightness': np.mean(img_rgb),
            'std_brightness': np.std(img_rgb),
        }

    def _decide_category(self, features: dict) -> str:
        """根据特征决定图片类别"""
        # A 类特征：高白底比例、低饱和度、高边缘密度、颜色数量少
        # B 类特征：低白底比例、高饱和度、低边缘密度、颜色数量多

        score_a = 0
        score_b = 0

        # 白底比例（高得分 A 类）
        if features['white_ratio'] > self.WHITESATURATION_THRESHOLD:
            score_a += 2
        elif features['white_ratio'] < 0.1:
            score_b += 2

        # 颜色数量（少得分 A 类，多得分 B 类）
        if features['unique_colors'] < self.COLORCOUNT_THRESHOLD:
            score_a += 2
        elif features['unique_colors'] > 100:
            score_b += 2

        # 边缘密度（高得分 A 类）
        if features['edge_density'] > self.EDGECOUNT_THRESHOLD:
            score_a += 1
        elif features['edge_density'] < 0.05:
            score_b += 1

        # 低饱和度比例（高得分 A 类）
        if features['low_saturation_ratio'] > 0.5:
            score_a += 1
        elif features['low_saturation_ratio'] < 0.2:
            score_b += 1

        # 默认决策
        if score_a > score_b:
            return 'A'
        elif score_b > score_a:
            return 'B'
        else:
            # 平局时，根据白底比例决定
            return 'A' if features['white_ratio'] > 0.3 else 'B'

    @staticmethod
    def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        """RGB 转 HSV"""
        rgb_norm = rgb / 255.0
        r, g, b = rgb_norm[:, :, 0], rgb_norm[:, :, 1], rgb_norm[:, :, 2]

        max_c = np.max(rgb_norm, axis=2)
        min_c = np.min(rgb_norm, axis=2)
        delta = max_c - min_c

        # 计算 H
        h = np.zeros_like(max_c)
        mask = delta > 0
        r_mask = max_c == r
        g_mask = max_c == g
        b_mask = max_c == b

        h[r_mask & mask] = ((g[r_mask & mask] - b[r_mask & mask]) / delta[r_mask & mask]) % 6
        h[g_mask & mask] = (2 + (b[g_mask & mask] - r[g_mask & mask]) / delta[g_mask & mask])
        h[b_mask & mask] = (4 + (r[b_mask & mask] - g[b_mask & mask]) / delta[b_mask & mask])
        h = h / 6.0

        # 计算 S
        s = np.zeros_like(max_c)
        s[max_c > 0] = delta[max_c > 0] / max_c[max_c > 0]

        # 计算 V
        v = max_c

        return np.stack([h, s, v], axis=2)

    @staticmethod
    def _detect_edges(rgb: np.ndarray) -> np.ndarray:
        """简单的边缘检测（使用梯度）"""
        gray = np.mean(rgb, axis=2).astype(np.float32)

        # 水平梯度
        dx = np.abs(np.diff(gray, axis=1))
        dx = np.pad(dx, ((0, 0), (0, 1)), mode='edge')  # 补齐最后一列

        # 垂直梯度
        dy = np.abs(np.diff(gray, axis=0))
        dy = np.pad(dy, ((0, 1), (0, 0)), mode='edge')  # 补齐最后一行

        # 合并梯度
        edges = (dx + dy) / 2.0
        return edges / 255.0  # 归一化