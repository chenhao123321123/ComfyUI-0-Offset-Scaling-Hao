import torch
import math
import numpy as np
from PIL import Image

def ceil64(x):
    return math.ceil(x / 64) * 64

class ImageSmartResize:
    NAME = "图片智能缩放"
    CATEGORY = "0 Offset Scaling - Hao"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "目标最长边": ("INT", {
                    "default": 1200,
                    "min": 64,
                    "max": 4096,
                    "step": 64
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "STRING")
    RETURN_NAMES = ("输出图片", "绘制遮罩", "扩展遮罩", "拼接")
    FUNCTION = "process"

    def process(self, image, mask, 目标最长边):
        B, H, W, C = image.shape
        original_width = W
        original_height = H
        size_string = f"{original_width}x{original_height}"

        target_long = ceil64(目标最长边)
        
        if W >= H:
            scale = target_long / W
            new_w = target_long
            new_h = int(round(H * scale))
        else:
            scale = target_long / H
            new_h = target_long
            new_w = int(round(W * scale))

        final_w = ceil64(new_w)
        final_h = ceil64(new_h)
        ox = (final_w - new_w) // 2
        oy = (final_h - new_h) // 2

        out_imgs = []
        out_masks_draw = []
        out_masks_expand = []

        for i in range(B):
            img_np = (image[i].cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
            canvas = Image.new("RGB", (final_w, final_h), 0)
            canvas.paste(pil_img, (ox, oy))
            out_img = torch.from_numpy(np.array(canvas)).float() / 255.0
            out_imgs.append(out_img)

            msk = mask[i].cpu().numpy()
            pil_msk = Image.fromarray((msk * 255).astype(np.uint8), mode="L")
            pil_msk = pil_msk.resize((new_w, new_h), Image.NEAREST)
            msk_canvas = Image.new("L", (final_w, final_h), 0)
            msk_canvas.paste(pil_msk, (ox, oy))
            draw_mask = torch.from_numpy(np.array(msk_canvas)).float() / 255.0
            out_masks_draw.append(draw_mask)

            expand_mask = Image.new("L", (final_w, final_h), 0)
            content_area = Image.new("L", (new_w, new_h), 255)
            expand_mask.paste(content_area, (ox, oy))
            expand_mask = Image.eval(expand_mask, lambda x: 255 - x)
            expand_mask_tensor = torch.from_numpy(np.array(expand_mask)).float() / 255.0
            out_masks_expand.append(expand_mask_tensor)

        return (
            torch.stack(out_imgs, dim=0),
            torch.stack(out_masks_draw, dim=0),
            torch.stack(out_masks_expand, dim=0),
            size_string
        )

class CropRestoreByMask:
    NAME = "还原尺寸"
    CATEGORY = "0 Offset Scaling - Hao"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "扩展遮罩": ("MASK",),
                "拼接": ("STRING", {"default": "1296x678"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("还原图片",)
    FUNCTION = "process"

    def process(self, image, 扩展遮罩, 拼接):
        w_str, h_str = 拼接.strip().split("x")
        target_w = int(w_str)
        target_h = int(h_str)

        B, H, W, C = image.shape
        out_imgs = []

        for i in range(B):
            img = image[i].cpu().numpy()
            msk = 扩展遮罩[i].cpu().numpy()
            msk_bin = (msk < 0.5).astype(np.uint8)

            ys, xs = np.where(msk_bin > 0)
            y1, y2 = ys.min(), ys.max() + 1
            x1, x2 = xs.min(), xs.max() + 1

            cropped = img[y1:y2, x1:x2, :]
            pil = Image.fromarray((cropped * 255).astype(np.uint8))
            pil = pil.resize((target_w, target_h), Image.LANCZOS)
            restored = torch.from_numpy(np.array(pil)).float() / 255.0
            out_imgs.append(restored)

        return (torch.stack(out_imgs, dim=0),)

NODE_CLASS_MAPPINGS = {
    "ImageSmartResize": ImageSmartResize,
    "CropRestoreByMask": CropRestoreByMask
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSmartResize": "图片智能缩放",
    "CropRestoreByMask": "还原尺寸"
}