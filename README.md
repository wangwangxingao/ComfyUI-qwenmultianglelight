# ComfyUI-QwenMultiangle WW

**作者:** wangwang

## 中文简介

这是一个用于ComfyUI的3D光照控制自定义节点（WW版本），在原版基础上增加了强大的自定义提示shiy

### 主要更新功能

#### 1. **自定义提示词系统**


- **灵活配置**：允许用户完全自定义方位角、仰角、强度、颜色等各个维度的提示词
- **管道符分隔**：使用 `|` 符号分隔多个提示词选项，系统自动根据数值映射到对应的描述
- **模板变量**：颜色提示词支持 `$1` 变量占位符，自动替换为HEX颜色值

#### 2. **完整可配置维度**

- **方位角提示词**：自定义方位描述
- **仰角提示词**：自定义垂直角度的描述
- **强度提示词**：自定义强度级别描述
- **颜色提示词模板**：支持自定义颜色描述模板，如"colored light ($1)"
- **全局约束文本**：可修改提示词开头的场景锁定和重光照约束文本

#### 3. **智能数值映射**

- 系统自动将数值范围（如方位角0-360°，仰角-90°到90°，强度0-10）映射到用户定义的提示词列表中
- 实时预览更新，3D视图中的提示词显示会立即反映自定义设置

#### 4. **向后兼容**

- 保留原有默认提示词系统，可通过"使用自定义提示词"复选框切换
- 原有工作流程完全兼容，新功能为可选增强

#### 5. **优化的前端交互**

- 3D视图中实时显示自定义提示词结果

[file content begin]

# 提示词预设示例

## 不同风格的预设配置

## 1. 相机视角风格（Camera View Style）

**适用场景**：模拟相机角度，用于视角控制而非光照控制

**方位角提示词**


front view|front-right quarter view|right side view|back-right quarter view|back view|back-left quarter view|left side view|front-left quarter view

正面视角|右前四分之一视角|右侧视角|右后四分之一视角|背面视角|左后四分之一视角|左侧视角|左前四分之一视角

**仰角提示词**


low-angle shot|eye-level shot|elevated shot|high-angle shot

低角度拍摄|平视拍摄|抬升拍摄|高角度拍摄

**强度提示词**

wide shot|medium shot|close-up

广角拍摄|中景拍摄|特写拍摄

**颜色提示词模板**


空（相机视角通常不包含颜色描述）

**全局约束文本**

`<sks>`



## 2. 专业光照风格（Professional Lighting Style）

**适用场景**：专业摄影/电影光照描述，详细的光源位置说明

**方位角提示词**

light source in front|light source from the front-right|light source from the right|light source from the back-right|light source from behind|light source from the back-left|light source from the left|light source from the front-left

前方光源|右前方光源|右侧光源|右后方光源|后光源|左后方光源|左侧光源|左前方光源

**仰角提示词**

uplighting, light source positioned below the character, light shining upwards|low-angle light source from below, upward illumination|horizontal level light source|high-angle light source|overhead top-down light source

向上照明，光源位于角色下方，光线向上照射|低角度光源从下方，向上照明|水平光源|高角度光源|顶置自上而下光源

**强度提示词**

strong|medium|soft

强烈|中等|柔和

**颜色提示词模板**

colored light ($1)

彩色光线（$1）

**全局约束文本**

SCENE LOCK, FIXED VIEWPOINT, maintaining character consistency and pose. RELIGHTING ONLY:

场景锁定，固定视点，保持角色一致性和姿势。仅重光照：

## 3. 简洁光照风格（Concise Lighting Style）

**适用场景**：简洁明了的光照描述，适合快速预览

**方位角提示词**

light from front|light from front-right|light from right|light from back-right|light from back|light from back-left|light from left|light from front-left

前方光线|右前方光线|右侧光线|右后方光线|后方光线|左后方光线|左侧光线|左前方光线

**仰角提示词**

from below|eye level|from high angle|from above|overhead

从下方|眼平线|从高角度|从上方|头顶

**强度提示词**

strong|medium|soft

强烈|中等|柔和

**颜色提示词模板**

colored light ($1)

彩色光线（$1） - $1将被替换为实际颜色值

**全局约束文本**

SCENE LOCK, FIXED VIEWPOINT, maintaining character consistency and pose. RELIGHTING ONLY:

场景锁定，固定视点，保持角色一致性和姿势。仅重光照：

## 4. Qwen格式风格（Qwen Format Style）

**适用场景**：符合Qwen模型期望的格式，优化AI理解

**方位角提示词**

front lighting|front-right lighting|right side lighting|back-right lighting|back lighting|back-left lighting|left side lighting|front-left lighting

前方光照|右前方光照|右侧光照|右后方光照|后方光照|左后方光照|左侧光照|左前方光照

**仰角提示词**

lighting from below|level lighting|lighting from above|top-down lighting

从下方光照|水平光照|从上方光照|自上而下光照

**强度提示词**

strong/close lighting|medium distance lighting|soft/far lighting

强烈/近距离光照|中等距离光照|柔和/远距离光照

**颜色提示词模板**

colored light ($1)

彩色光线（$1） - $1将被替换为实际颜色值

**全局约束文本**


SCENE LOCK, FIXED VIEWPOINT, maintaining character consistency and pose. RELIGHTING ONLY:

场景锁定，固定视点，保持角色一致性和姿势。仅重光照：

## 引用与致谢

本项目基于以下优秀项目进行开发，特此表示感谢：

#### 基础项目引用

- **原始项目**：ComfyUI-QwenMultiangle Lightning
- **原作者**：aiwood & wallen
- **项目地址**：https://github.com/wallen0322/ComfyUI-qwenmultianglelight
- **核心功能**：3D交互式光照控制、多光源配置、实时预览、电影模式光照

