# tests/ — 测试用例目录

本目录存放项目的单元测试和测试图片资源。

## 文件清单

| 文件 | 说明 |
|------|------|
| `__init__.py` | 包初始化（空文件，使 tests 成为 Python 包） |
| `test_classifier.py` | ImageClassifier 分类器单元测试 |
| `test_processor.py` | ImageProcessor 处理器单元测试 |
| `test_*.png` | 测试用图片资源（A/B 类样例、不同强度效果对比等） |

## 测试约定

- 使用 `pytest` 框架，测试函数以 `test_` 开头
- 断言直接写 `assert`，不引入额外库
- 测试图片资源统一放在本目录下，路径通过 `Path(__file__).parent / "xxx.png"` 获取
- 新增功能需同步补充对应测试用例
- 覆盖率目标：核心模块（classifier、processor）行覆盖率 ≥ 80%
