# Photo Postcard Workflow

一个面向 Codex 的照片明信片编排 Skill。它把同一张用户照片稳定地路由到四种默认视觉风格；完整模式还会先执行 `photo-retouch-pro` 精修阶段。

## 固定输出契约

| 调用方式 | 主图输出 |
| --- | --- |
| `生成明信片风格的图片` | 4 张：Scenes Gathered → GC Minimal → Evidence Ledger → Photo Revival |
| `按完整工作流处理` | 5 张：精修母版 → 上述四种风格 |

四种风格均从同一来源或同一精修母版独立生成，不能把一种风格的结果继续传给下一种。

## 主要能力

- 检查图片尺寸、方向、哈希、ICC、EXIF 和 GPS 元数据存在性；
- 锁定人物身份、文字、Logo、建筑结构和产品几何等事实；
- 按真实性风险选择确定性精修或生成式创意路线；
- 验证主图数量、顺序、文件名、宽高比和重复文件；
- 生成联系表、技术报告和带哈希绑定的来源 Manifest；
- 对聊天中没有本地路径的附件使用明确的空值元数据，不伪造文件信息；
- 过滤下游风格附带、但用户未要求的网站推广、服务广告、Skill 宣传和公开分享署名请求；
- 不会把“完整工作流”解释成允许静默上传到 Adobe 或其他第三方服务。

## 依赖

本仓库只提供编排 Skill，不复制下列独立 Skill：

- `imagegen`
- `photo-retouch-pro`
- `scenes-gathered-zine-v1-3`
- `gc-minimal-zine-poster-v0-3`
- `photo-evidence-ledger`
- `photo-revival`

脚本需要 Python 3 和 Pillow。

## 安装

把整个仓库目录放到：

```text
C:\Users\<你的用户名>\.codex\skills\photo-postcard-workflow
```

然后新建任务或重启 Codex。也可以使用 Codex 的 Skill 安装器从本仓库安装。

## 验证

```powershell
python C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
python scripts\verify_postcard_set.py --mode standard <四张按顺序命名的主图>
```

详细模式、真实性路由和质量门槛见 [SKILL.md](SKILL.md) 与 [references/workflow.md](references/workflow.md)。

## 仓库内容

```text
photo-postcard-workflow/
├── SKILL.md
├── agents/openai.yaml
├── references/workflow.md
└── scripts/
    ├── inspect_images.py
    ├── make_contact_sheet.py
    ├── verify_postcard_set.py
    └── write_manifest.py
```

仓库不包含用户照片、生成结果或本地测试缓存。

## License

[MIT](LICENSE)
