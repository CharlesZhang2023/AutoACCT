# AutoACCT — Claude Code 记账 Skill

[English](README.md) | **简体中文**

一个 [Claude Code](https://claude.com/claude-code) skill，把小票照片（可附文字说明）自动变成 Google Sheet 里结构化的一行记录，并按当日 ECB 汇率换算为港币。

目前在 Claude Code 中手动调用；后续计划接入 WhatsApp webhook 实现真正的"发张图就记账"。

## 功能

1. 用视觉识别读取小票 / 发票 / 支付截图。
2. 提取：日期、商家、分类、金额、币种、支付方式、商品明细、原始 OCR 文本、用户备注。
3. 通过 [frankfurter.app](https://frankfurter.app)（免费，无需 API key）按当日 ECB 参考汇率换算为 **HKD**。
4. 向已配置好的 Google Sheet 追加一行（14 列，具体见 `schema.md`）。
5. 回复记账结果，并标注任何靠推测填入的字段。

## 安装

把仓库 clone 到 Claude Code 的 skills 目录：

```bash
git clone https://git.deepknow.site/Knowit/AutoACCT.git ~/.claude/skills/bookkeeping
```

然后按 [`scripts/setup.md`](scripts/setup.md) 完成一次性配置：

- 安装 Python 依赖：`pip install google-api-python-client google-auth`
- 在 GCP 建服务账号并下载 JSON key
- 新建 Google Sheet，填好 14 列表头，把 sheet 分享给服务账号的 email
- `cp config.example.json config.json`，填入 `sheet_id` 和 `service_account_path`

## 使用

在 Claude Code 会话里把小票图片拖进来，然后说 "log this" / "记一下" 之类即可。Skill 会根据"小票/记账"类请求自动触发，**不需要** slash command。

文字说明可选，可用来补充上下文（支付方式、AA、分类提示、备注等）。

## 文件结构

| 文件                   | 作用                                          |
|------------------------|-----------------------------------------------|
| `SKILL.md`             | 入口文件 — Claude 读它来决定如何执行 skill    |
| `categories.md`        | 固定的 14 个分类列表                          |
| `schema.md`            | Google Sheet 列顺序（A–N）                    |
| `config.example.json`  | 配置模板 → 复制为 `config.json`（已 gitignore）|
| `scripts/fx_convert.py`| 原币种 → HKD 换算（frankfurter.app）          |
| `scripts/append_row.py`| 向 Google Sheet 写入一行                      |
| `scripts/setup.md`     | 一次性配置步骤                                |

## Roadmap

- [ ] WhatsApp webhook 接入层（Meta Cloud API 或 Twilio），实现手机端直接发图记账
- [ ] 可选的 Google Drive 上传，让 `Receipt` 列直接变成可点的图片链接
- [ ] 月度汇总脚本（按分类、按币种统计）

## License

私有 — 仅供内部使用。
