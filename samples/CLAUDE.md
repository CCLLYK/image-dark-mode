# samples/ — 测试图片样本目录

本目录存放人工上传的 A 类（文字/图形）和 B 类（照片/绘画）测试图片，用于验证图片暗黑化处理的实际效果。

## 文件命名约定

- **A 类图片**：`a_class_<描述>.<ext>`（如 `a_class_flowchart.png`）
- **B 类图片**：`b_class_<描述>.<ext>`（如 `b_class_photo.jpg`）
- 保留原格式后缀（`.png`、`.jpg`、`.jpeg`、`.webp` 等）

## 处理规则

上传每张图片后，运行以下命令生成暗黑版：

```bash
# 自动分类 + 默认强度（medium）
python src/cli.py --input samples/a_class_xxx.png --output samples/a_class_xxx.dark.png

# 指定类型和强度
python src/cli.py --input samples/b_class_xxx.jpg --type photo --intensity strong
```

处理完成后将 `<name>.dark.<ext>` 与原图放在同目录，便于并排对比效果。

## 注意事项

- 此目录仅用于测试，不纳入项目发布产物
- 处理后的 `.dark.*` 文件同样保留在此目录，方便视觉对比
- 测试完毕后如需清理，可整体删除本目录内容
