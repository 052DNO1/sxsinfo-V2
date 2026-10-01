"""
生成桌面端应用图标源图（1024x1024 PNG）

设计：与系统登录页一致的蓝青渐变圆角方块 + 白色 LIMS 字标。
生成后由 `cargo tauri icon` 派生出 .ico / .icns / 各尺寸 PNG。

用法：
    python generate-icon.py <输出路径>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
# 与 frontend Login.vue 的登录按钮渐变保持一致
GRADIENT_START = (24, 144, 255)   # #1890ff
GRADIENT_END = (54, 207, 201)     # #36cfc9

# Windows 常见无衬线粗体，按优先级取第一个存在的
FONT_CANDIDATES = [
    r'C:\Windows\Fonts\msyhbd.ttc',    # 微软雅黑 Bold
    r'C:\Windows\Fonts\segoeuib.ttf',  # Segoe UI Bold
    r'C:\Windows\Fonts\arialbd.ttf',   # Arial Bold
]


def linear_gradient(size, start, end):
    """生成对角线性渐变"""
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    for y in range(size):
        for_x = y / (size - 1)
        # 每行先算一个基准色，再用一个小渐变横向铺开，兼顾速度与观感
        ratio = for_x * 0.65
        color = tuple(
            int(start[i] + (end[i] - start[i]) * ratio) for i in range(3)
        )
        draw.line([(0, y), (size, y)], fill=color)
    # 横向再叠加一层渐变，得到真正的对角效果
    overlay = Image.new('RGB', (size, size))
    odraw = ImageDraw.Draw(overlay)
    for x in range(size):
        ratio = (x / (size - 1)) * 0.65
        color = tuple(
            int(start[i] + (end[i] - start[i]) * ratio) for i in range(3)
        )
        odraw.line([(x, 0), (x, size)], fill=color)
    return Image.blend(img, overlay, 0.5)


def rounded_mask(size, radius):
    """圆角矩形遮罩（应用图标标准圆角比例）"""
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_centered_text(draw, text, font, center_y, fill, letter_spacing=0):
    """按字距居中绘制文本"""
    if letter_spacing <= 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text(
            ((SIZE - width) / 2 - bbox[0], center_y - height / 2 - bbox[1]),
            text,
            font=font,
            fill=fill,
        )
        return

    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        widths.append(bbox[2] - bbox[0])
    total = sum(widths) + letter_spacing * (len(text) - 1)

    x = (SIZE - total) / 2
    for ch, w in zip(text, widths):
        bbox = draw.textbbox((0, 0), ch, font=font)
        draw.text((x - bbox[0], center_y - (bbox[3] - bbox[1]) / 2 - bbox[1]), ch, font=font, fill=fill)
        x += w + letter_spacing


def main():
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else 'icon-source.png')
    out_path.parent.mkdir(parents=True, exist_ok=True)

    base = linear_gradient(SIZE, GRADIENT_START, GRADIENT_END).convert('RGBA')
    base.putalpha(rounded_mask(SIZE, radius=int(SIZE * 0.22)))

    draw = ImageDraw.Draw(base)

    # 字标
    font = load_font(int(SIZE * 0.30))
    draw_centered_text(draw, 'LIMS', font, SIZE * 0.47, (255, 255, 255, 255), letter_spacing=int(SIZE * 0.012))

    # 下方强调线
    line_w = int(SIZE * 0.30)
    line_h = int(SIZE * 0.032)
    draw.rounded_rectangle(
        [(SIZE - line_w) / 2, SIZE * 0.665, (SIZE + line_w) / 2, SIZE * 0.665 + line_h],
        radius=line_h // 2,
        fill=(255, 255, 255, 230),
    )

    base.save(out_path, 'PNG')
    print(f'已生成 {out_path} ({base.width}x{base.height})')


if __name__ == '__main__':
    main()
