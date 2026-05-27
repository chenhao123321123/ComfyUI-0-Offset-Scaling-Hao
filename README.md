# ComfyUI-0-Offset-Scaling-Hao

一套专为图片扩展场景设计的配套节点包。

## 包含节点
1.  **图片智能缩放**
    - 功能：等比例缩放 + 64对齐 + 居中
    - 输出：处理后图片、绘制遮罩、扩展遮罩、原图尺寸字符串（拼接）

2.  **还原尺寸**
    - 功能：根据扩展遮罩裁剪图片，再按「拼接」字符串还原为原图尺寸
    - 输入：处理后图片、扩展遮罩、拼接字符串

## 安装方式
在 ComfyUI Manager 中，使用 Git URL 安装：
`https://github.com/chenhao123321123/ComfyUI-0-Offset-Scaling-Hao`
