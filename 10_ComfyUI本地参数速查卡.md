# ComfyUI 本地参数速查卡 · RTX 5000 16GB

打印或钉在显示器旁。

## 启动

```bat
python main.py --lowvram --disable-mmap
```

## 工作流

`Template → Video → MiniMax H3 Reference to Video`

## 权重

| 用途 | 文件类型 |
|------|----------|
| DiT | pruned **INT4** / W4A8 / GGUF **Q4** |
| TE | **INT4** Qwen3-VL |
| Video VAE | fp16 或 int8 |
| Audio VAE | **fp32 必选** |
| 禁止 | **NVFP4**（非 Blackwell） |

## LowVRAM 节点

`balanced` → 不行再 `low_vram` → 再 `prefetch=disable`

## 分辨率（9:16）· 只做成片

| 项 | 值 |
|----|-----|
| MP | **0.65**（576×1024 / 608×1088） |
| Multiple | 32（不要 1.0 MP） |
| 时长 | **8 秒** |
| Turbo | **关** |
| Steps | **12–20** |

## Sampler（模板默认即可）

- `res_multistep` + `simple`  
- shift 跟模型默认（video≈12 / audio≈3）  

## 注意力

先默认跑通 → 再试 sol-attn；低显存慎用 Sage。

## 发布

成片 → 外挂超分 1080×1920 → 剪辑字幕 → 合规清单
