# ⑨表达式求解器 🧊

一个基于9、99、999三个基础数字，通过加减乘除运算生成目标整数的智能推理器

<img title="" src="https://s3.bmp.ovh/imgs/2025/02/12/82641ee40331811a.png" alt="" width="369"> 
（运行截图）



## 📖 项目简介

灵感起源

本项目灵感来源于：

1. **2025=⑨⑨⑨+⑨⑨⑨+⑨+⑨+⑨**
2. **恶臭数字论证器**：[homo数字论证器](https://lab.magiconch.com/homo/)的运算哲学

我们希望通过⑨的完美算术智慧(大嘘)，构建一个兼具数学严谨性与趣味性的数字论证系统

```python
print("示例：108 = ⑨⑨ + ⑨")  # 实际输出会根据算法动态生成
```

## 

## 🧩 池沼对比

| 功能   | 本项目      | Homo论证器 |
| ---- | -------- | ------- |
| 基础数字 | 9/99/999 | 114514  |
| 运算方式 | 四则运算     | 四则运算    |
| 输出风格 | ⑨        | 恶臭化学式   |
| 音频反馈 | ⑨のbaka音效 | 无       |
| 算法目标 | 最优解搜索    | 数字推理    |

## 

## ✨ 核心特性

- **⑨的完美运算**：仅使用9/99/999进行四则运算
- **智能推理算法**：动态优先级搜索 + 预计算缓存
- **跨平台支持**：Windows/macOS/Linux全兼容
- **趣味交互**：
  - 动态进度提示
  - 任意键中断搜索
  - 音频反馈（需要音频设备支持）
  - ⑨

## 

## 📦 版本说明

| 版本   | 路径                        | 状态  | 推荐指数  |
| ---- | ------------------------- | --- | ----- |
| 命令行版 | `version1.1/main.py`      | 稳定  | ⭐⭐⭐⭐⭐ |
| GUI版 | `GUI_Version/main_gui.py` | 摆烂中 | ⭐     |

## 

## 🛠️ 快速开始

### 环境要求

- Python 3.8+
- 音频播放支持（可选）

```bash
# 安装依赖
pip instll pyaudio

# Ubuntu额外依赖
sudo apt install libportaudio2

# macOS
brew install portaudio
```

### 运行命令行版

```bash
cd version1.1
python main.py

# 示例输入输出
请输入目标整数: 108
结果 (0.23s):
108 = ⑨⑨ + ⑨
baka~
```

## 

## 📂 项目结构

```
结构推理器/
├── version1.1/            # 主版本
│   ├── main.py            # 核心算法实现
│   ├── Number_generater.py # 高频数字生成逻辑
│   └── Audio_coding.py    # 音频编码模块
└── GUI_Version/           # 实验性GUI
    ├── main_gui.py        # 后端
    └── gui.py             # 前端                  
```

## 

## 🧠 算法亮点

```python
class ImprovedNineExpressionFinder:
    def __init__(self):
        self.expression_cache = {108: '⑨⑨+⑨'}  # 智能预加载
        self._precompute_common_results()     # 预计算优化

    def _find_expression_with_timeout(self):
        # 动态运算符优先级
        # 智能剪枝策略
        # 跨平台中断检测 
```

## 

## ⚠️ 注意事项

- 大数字（>10^4）可能需要更长时间
- 音频播放依赖系统解码器

## 

## 🤝 贡献指南

欢迎提交PR！请遵循现有代码风格：

- 使用类型注解
- 尽量保持docstring规范

**~~以及大佬们带带我，我啥也不会，只会面向ai编程😭~~**

## 

## 📜 许可证

   [MIT License](LICENSE) 

## 

## 🌟 特别致谢

- [homo数字论证器](https://github.com/itorr/homo) 提供灵感启发
- FinaleDreamilyNeko的暴论（bushi

## 

## **🔗 相关链接**

- [homo数字论证器在线版](https://lab.magiconch.com/homo/)
- [【经典回顾】东方数学小课堂：琪露诺的完美算术教室](https://www.bilibili.com/video/BV1rs41197Xn)

##### 

##### **⑨是最强的！** 本项目的所有运算都经过⑨的严格验证，保证⑨⑨%正确！✨



> 提示：遇到卡顿时大喊"baka"可能会提升运算速度哦~ ❄️
