"""
Qwen Multiangle Lightning Node for ComfyUI
Multi-Light Configuration Version with Custom Prompts
"""

import numpy as np
from PIL import Image
import base64
import io
import hashlib
import json

_cache = {}

class QwenMultiangleNodeWW:
    """
    Lighting Control Node - Multi-Light Configuration Edition with Custom Prompts
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
                "light_color_hex": ("STRING", {"default": "#FFFFFF"}),
                "cinematic_mode": ("BOOLEAN", {
                    "default": True, "display": "checkbox"
                }),
                "use_custom_prompts": ("BOOLEAN", {
                    "default": False, "display": "checkbox", 
                    "label": "Use Custom Prompts"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
                "custom_azimuth_prompts": ("STRING", {
                    "multiline": True,
                    "default": "light source in front|light source from the front-right|light source from the right|light source from the back-right|light source from behind|light source from the back-left|light source from the left|light source from the front-left",
                    "placeholder": "Azimuth prompts separated by |",
                    "label": "Azimuth Prompts"
                }),
                "custom_elevation_prompts": ("STRING", {
                    "multiline": True,
                    "default": "uplighting, light source positioned below the character, light shining upwards|low-angle light source from below, upward illumination|horizontal level light source|high-angle light source|overhead top-down light source",
                    "placeholder": "Elevation prompts separated by |",
                    "label": "Elevation Prompts"
                }),
                "custom_intensity_prompts": ("STRING", {
                    "multiline": True,
                    "default": "soft|bright|intense",
                    "placeholder": "Intensity prompts separated by |",
                    "label": "Intensity Prompts"
                }),
                "custom_color_prompt": ("STRING", {
                    "multiline": True,
                    "default": "colored light ($1)",
                    "placeholder": "Color prompt template, use $1 for color value",
                    "label": "Color Prompt Template"
                }),
                "custom_global_constraints": ("STRING", {
                    "multiline": True,
                    "default": "SCENE LOCK, FIXED VIEWPOINT, maintaining character consistency and pose. RELIGHTING ONLY: ",
                    "placeholder": "Global constraints text",
                    "label": "Global Constraints"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "light_configs_json": ("STRING", {"default": "[]"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("lighting_prompt",)
    OUTPUT_IS_LIST = (True,)  # 支持多输出
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
        except Exception:
            return str(hash(str(image)))

    def _get_prompt_from_custom(self, value, min_val, max_val, custom_prompts_str, default_prompts):
        """根据自定义提示词列表获取对应的提示词"""
        if not custom_prompts_str or '|' not in custom_prompts_str:
            # 如果没有自定义提示词或格式不正确，返回默认提示词
            return default_prompts
        
        prompts = custom_prompts_str.split('|')
        prompts = [p for p in prompts]
        
        if not prompts:
            return default_prompts
        
        # 将值映射到提示词索引
        value_range = max_val - min_val
        if value_range == 0:
            idx = 0
        else:
            normalized = (value - min_val) / value_range
            idx = int(normalized * len(prompts))
            idx = max(0, min(len(prompts) - 1, idx))
        
        return prompts[idx]

    def _get_color_prompt(self, color_hex, custom_color_prompt):
        """根据颜色提示词模板生成颜色描述"""
        if not custom_color_prompt:
            # 如果没有自定义颜色模板，使用默认
            return f"colored light ({color_hex})"
        
        # 替换模板中的 $1 为实际颜色值
        if '$1' in custom_color_prompt:
            return custom_color_prompt.replace('$1', color_hex)
        else:
            # 如果模板中没有 $1，直接使用模板
            return custom_color_prompt

    def _build_prompt(self, azimuth, elevation, intensity, color_hex, cinematic_mode, 
                     use_custom_prompts=False, custom_azimuth_prompts="", custom_elevation_prompts="",
                     custom_intensity_prompts="", custom_color_prompt="", custom_global_constraints=""):
        """根据配置生成 prompt"""
        
        # 1. 方位描述
        if use_custom_prompts and custom_azimuth_prompts:
            pos_desc = self._get_prompt_from_custom(
                azimuth % 360, 0, 360, custom_azimuth_prompts,
                "light source in front"  # 默认值
            )
        else:
            # 使用默认的方位区间判断
            az = azimuth % 360
            if (az >= 337.5) or (az < 22.5): pos_desc = "light source in front"
            elif 22.5 <= az < 67.5: pos_desc = "light source from the front-right"
            elif 67.5 <= az < 112.5: pos_desc = "light source from the right"
            elif 112.5 <= az < 157.5: pos_desc = "light source from the back-right"
            elif 157.5 <= az < 202.5: pos_desc = "light source from behind"
            elif 202.5 <= az < 247.5: pos_desc = "light source from the back-left"
            elif 247.5 <= az < 292.5: pos_desc = "light source from the left"
            else: pos_desc = "light source from the front-left"

        # 2. 高度描述
        if use_custom_prompts and custom_elevation_prompts:
            elev_desc = self._get_prompt_from_custom(
                elevation, -90, 90, custom_elevation_prompts,
                "horizontal level light source"  # 默认值
            )
        else:
            # 使用默认的高度区间判断
            e = elevation
            if -90 <= e < -30:
                elev_desc = "uplighting, light source positioned below the character, light shining upwards"
            elif -30 <= e < -10:
                elev_desc = "low-angle light source from below, upward illumination"
            elif -10 <= e < 20:
                elev_desc = "horizontal level light source"
            elif 20 <= e < 60:
                elev_desc = "high-angle light source"
            else:
                elev_desc = "overhead top-down light source"

        # 3. 强度描述
        if use_custom_prompts and custom_intensity_prompts:
            int_desc = self._get_prompt_from_custom(
                intensity, 0.0, 10.0, custom_intensity_prompts,
                "bright"  # 默认值
            )
        else:
            # 使用默认的强度描述
            if intensity < 3.0: int_desc = "soft"
            elif intensity < 7.0: int_desc = "bright"
            else: int_desc = "intense"

        # 4. 颜色描述
        if use_custom_prompts and custom_color_prompt:
            color_desc = self._get_color_prompt(color_hex, custom_color_prompt)
        else:
            color_desc = f"colored light ({color_hex})"

        # 5. 提示词结构
        if use_custom_prompts and custom_global_constraints:
            global_constraints = custom_global_constraints.strip()
        else:
            global_constraints = "SCENE LOCK, FIXED VIEWPOINT, maintaining character consistency and pose. RELIGHTING ONLY: "
        
        light_positioning = f"{pos_desc} {elev_desc}"
        light_attributes = f"{int_desc} {color_desc}"
        
        if cinematic_mode:
            return f"{global_constraints} {light_positioning} {light_attributes}, cinematic relighting"
        else:
            return f"{global_constraints} {light_positioning} {light_attributes}"

    def generate_lighting_prompt(self, light_azimuth, light_elevation, light_intensity, 
                                light_color_hex, cinematic_mode=True, use_custom_prompts=False,
                                image=None, light_configs_json="[]", unique_id=None,
                                custom_azimuth_prompts="", custom_elevation_prompts="",
                                custom_intensity_prompts="", custom_color_prompt="", 
                                custom_global_constraints=""):
        # 解析多配置 JSON
        configs = []
        if light_configs_json and light_configs_json != "[]":
            try:
                configs = json.loads(light_configs_json)
            except:
                pass
        
        # 生成 prompts 列表
        prompts = []
        if configs and len(configs) > 0:
            # 有多配置数据，按配置生成
            for cfg in configs:
                prompt = self._build_prompt(
                    cfg.get('azimuth', light_azimuth),
                    cfg.get('elevation', light_elevation),
                    cfg.get('intensity', light_intensity),
                    cfg.get('color', light_color_hex),
                    cinematic_mode,
                    use_custom_prompts,
                    custom_azimuth_prompts,
                    custom_elevation_prompts,
                    custom_intensity_prompts,
                    custom_color_prompt,
                    custom_global_constraints
                )
                prompts.append(prompt)
        else:
            # 无多配置，使用当前 widget 值生成单个
            prompt = self._build_prompt(
                light_azimuth, light_elevation, light_intensity, 
                light_color_hex, cinematic_mode,
                use_custom_prompts,
                custom_azimuth_prompts,
                custom_elevation_prompts,
                custom_intensity_prompts,
                custom_color_prompt,
                custom_global_constraints
            )
            prompts.append(prompt)

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

        # 返回提示词和自定义提示词数据给前端
        custom_prompts_data = {
            "use_custom": use_custom_prompts,
            "azimuth": custom_azimuth_prompts,
            "elevation": custom_elevation_prompts,
            "intensity": custom_intensity_prompts,
            "color": custom_color_prompt,
            "global_constraints": custom_global_constraints
        } if use_custom_prompts else None

        return {"ui": {"image_base64": [image_base64], "custom_prompts": [custom_prompts_data]}, "result": (prompts,)}

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenMultiangleNodeWW": QwenMultiangleNodeWW,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenMultiangleNodeWW": "Qwen Multiangle WW",
}
