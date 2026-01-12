"""
Qwen Multiangle Lightning Node for ComfyUI
Extreme Stability Version: Locks Scene, Camera, Pose, and Composition.
"""

import numpy as np
from PIL import Image
import base64
import io
import hashlib
import torch

_cache = {}
_max_cache_size = 50

class QwenMultiangleLightningNode:
    """
    Lighting Control Node - Extreme Stability Edition
    Strictly maintains scene and character while only adjusting the lighting profile.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "light_azimuth": ("INT", {
                    "default": 0, "min": 0, "max": 360, "step": 1, "display": "slider"
                }),
                "light_elevation": ("INT", {
                    "default": 30, "min": -90, "max": 90, "step": 1, "display": "slider"
                }),
                "light_intensity": ("FLOAT", {
                    "default": 5.0, "min": 0.0, "max": 10.0, "step": 0.1, "display": "slider"
                }),
                "light_color_hex": ("COLOR", {"default": "#FFFFFF"}),
                "cinematic_mode": ("BOOLEAN", {
                    "default": True, "display": "checkbox"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("lighting_prompt",)
    FUNCTION = "generate_lighting_prompt"
    CATEGORY = "image/lighting"
    OUTPUT_NODE = True

    def _compute_image_hash(self, image):
        if image is None: return None
        try:
            if hasattr(image, 'cpu'):
                img_np = image[0].cpu().numpy() if len(image.shape) == 4 else image.cpu().numpy()
            else:
                img_np = image.numpy()[0] if hasattr(image, 'numpy') and len(image.shape) == 4 else image
            return hashlib.md5(img_np.tobytes()).hexdigest()
        except:
            return str(hash(str(image)))

    def generate_lighting_prompt(self, light_azimuth, light_elevation, light_intensity, light_color_hex, cinematic_mode=True, image=None, unique_id=None):
        cache_key = str(unique_id) if unique_id else "default"
        image_hash = self._compute_image_hash(image)
        cached = _cache.get(cache_key, {})
        
        if (cached.get('azimuth') == light_azimuth and 
            cached.get('elevation') == light_elevation and 
            cached.get('intensity') == light_intensity and
            cached.get('color') == light_color_hex and
            cached.get('cinematic') == cinematic_mode and
            cached.get('image_hash') == image_hash):
            return cached['result']

        # 1. 映射光照方位描述
        az = light_azimuth % 360
        if az < 22.5 or az >= 337.5: pos_desc = "light hitting from the front"
        elif az < 67.5: pos_desc = "light hitting from the front-right side"
        elif az < 112.5: pos_desc = "light hitting from the right (90 degrees)"
        elif az < 157.5: pos_desc = "light hitting from the back-right"
        elif az < 202.5: pos_desc = "backlighting, light from behind"
        elif az < 247.5: pos_desc = "light hitting from the back-left"
        elif az < 292.5: pos_desc = "light hitting from the left (90 degrees)"
        else: pos_desc = "light hitting from the front-left side"

        # 2. 映射光照高度（避免使用俯仰角相关词汇）
        if light_elevation <= -60: elev_desc = "extreme low-angle light source, strong bottom-up shadow"
        elif light_elevation < -30: elev_desc = "low-level light source, bottom-up shadow"
        elif light_elevation < 20: elev_desc = "horizontal light source"
        elif light_elevation < 60: elev_desc = "high-positioned light source"
        else: elev_desc = "top-down ceiling light source"

        # 3. 强度描述
        if light_intensity < 3.0: int_desc = "soft ambient"
        elif light_intensity < 7.0: int_desc = "bright directional"
        else: int_desc = "strong dramatic contrast"

        # --- 核心修改：极致场景与镜头锁定 ---
        # 加入了 SCENE LOCK 和 CONSTANT BACKGROUND 等强力提示词
        global_constraints = (
            "SCENE LOCK, CONSTANT BACKGROUND, FIXED SCENERY. " # 锁定场景和背景
            "STATIC SHOT, FIXED VIEWPOINT, NO CAMERA MOVEMENT. " # 锁定镜头
            "maintaining character consistency, "
            "keeping the same character pose and action, "
            "maintaining the same composition, "
            "RELIGHTING ONLY: only the light rays and shadows change, the scene remains untouched. " # 明确重塑光影任务
        )
        
        color_desc = f"colored light (hex: {light_color_hex})"
        detail_prompt = f"{int_desc} {color_desc}, {pos_desc}, {elev_desc}"
        
        if cinematic_mode:
            prompt = f"{global_constraints}professional cinematic relighting, {detail_prompt}, raytraced shadows, realistic global illumination"
        else:
            prompt = f"{global_constraints}{detail_prompt}"

        # 预览图处理
        image_base64 = ""
        if image is not None:
            try:
                i = 255. * image[0].cpu().numpy()
                img_np = np.clip(i, 0, 255).astype(np.uint8)
                pil_image = Image.fromarray(img_np)
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")
                image_base64 = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
            except: pass

        result = {"ui": {"image_base64": [image_base64]}, "result": (prompt,)}
        
        _cache[cache_key] = {
            'azimuth': light_azimuth, 'elevation': light_elevation, 
            'intensity': light_intensity, 'color': light_color_hex,
            'cinematic': cinematic_mode, 'image_hash': image_hash, 
            'result': result
        }
        
        return result

NODE_CLASS_MAPPINGS = {
    "QwenMultiangleLightningNode": QwenMultiangleLightningNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenMultiangleLightningNode": "Qwen Multiangle Lightning",
}