# 开源工具（工作流层）

本目录只发布**短剧创作工作流**相关脚本。云端产线、SSH、FlowForge 提交、算力运维等脚本**不在本仓库**。

| 脚本 | 作用 |
|------|------|
| `h3_dialogue_codec.py` | H3 口型对白转码（`<d>[Chinese] …</d>`） |
| `v4_to_v3_prompts.py` | 从 V4 导演执行稿生成 V3 提示词 |
| `gen_local_prompts.py` | 本地成片提示词批量生成 |
| `gen_full_series.py` | 全集骨架生成辅助 |
| `polish_elevator.py` | 《末班电梯》文案抛光示例 |
| `h3_subtitle_patch.py` | 字幕/对白补丁辅助 |
| `check_qingfeng_assets.py` | 《青锋不问名》资产闸门检查 |
| `_fix_formula.py` | 提示词公式校验 |

自用产线请在本机私有目录维护，并通过环境变量配置端点，例如：

```text
FF_BASE=http://127.0.0.1:8188
H3_ROOT=/path/to/this/repo
```

切勿把真实主机、账号、令牌写进仓库。
