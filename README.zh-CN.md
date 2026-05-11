# AutoACCT for OpenClaw

[English](README.md) | **简体中文**

一个 OpenClaw skill，把小票照片（可附文字说明）自动变成 Google Sheet 里结构化的一行记录，并按当日 ECB 汇率换算为港币。

目前在 OpenClaw 中手动调用；后续计划接入 WhatsApp webhook 实现真正的"发张图就记账"。

## 功能

1. 用视觉识别读取小票 / 发票 / 支付截图。
2. 提取：日期、商家、分类、金额、币种、支付方式、商品明细、原始 OCR 文本、用户备注。
3. 通过 [frankfurter.app](https://frankfurter.app)（免费，无需 API key）按当日 ECB 参考汇率换算为 **HKD**。
4. 向已配置好的 Google Sheet 追加一行（14 列，具体见 `schema.md`）。
5. 回复记账结果，并标注任何靠推测填入的字段。

## 安装（用户端）

管理员（admin）会给你**两样东西**：一个 service-account JSON 密钥文件（如 `autoacct-sa.json`），以及一个 service-account 邮箱（形如 `autoacct@your-project.iam.gserviceaccount.com`）。没拿到先找管理员要。

按下面 4 步操作，约 5 分钟。

> **不太熟悉命令行？** 用 [`DEPLOY.md`](DEPLOY.md)（英文）—— 同样的安装流程，但是为非技术用户写的逐步指南，可配合 AI agent 一步步操作。

### Step 1 — Clone 仓库 + 装 Python 依赖

```bash
git clone https://github.com/CharlesZhang2023/AutoACCT.git ~/.openclaw/workspace/skills/AutoACCT
pip install google-api-python-client google-auth
```

### Step 2 — 把管理员发的 JSON 放到 `~/.config/gcp/`

```bash
mkdir -p ~/.config/gcp
mv ~/Downloads/autoacct-sa.json ~/.config/gcp/autoacct-sa.json
chmod 600 ~/.config/gcp/autoacct-sa.json
```

（`~/Downloads/autoacct-sa.json` 改成你实际保存文件的路径。）

### Step 3 — 建你自己的 Google Sheet 并把它 share 给 service account

1. 打开 https://sheets.new（直接创建空白 sheet）
2. 给 sheet 起个标题（如 `我的 AutoACCT 账本`）
3. **记住左下角 tab 的名字** —— 英文界面默认 `Sheet1`，中文界面默认 `工作表1`，Step 4 要用这个**精确字符串**
4. 点进 **A1** 单元格，粘贴下面这一整行（中间是 Tab 分隔，粘进去会自动拆到 A1–N1）：
   ```
   Date	Merchant	Category	Amount	Currency	Amount (HKD)	FX Rate	FX Date	Payment Method	Line Items	Raw OCR	Note	Receipt	Logged At
   ```
5. 右上角 **Share** → 粘贴管理员给你的 **service-account 邮箱** → 权限选 **Editor** → **Send**（"Notify people" 可以不勾）
6. **从浏览器地址栏直接复制 sheet 的完整 URL**，类似：
   `https://docs.google.com/spreadsheets/d/1abc...xyz/edit#gid=0`
   （脚本会自动从 URL 里抽出 sheet ID，所以完整链接或裸 ID 都行。）

### Step 4 — 写 config.json

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
cp config.example.json config.json
```

用编辑器打开 `config.json`，把 Step 3 拿到的 **sheet_id**（粘 URL 即可）和 **worksheet**（tab 名）填进去：

```json
{
  "sheet_id": "https://docs.google.com/spreadsheets/d/1abc...xyz/edit",
  "worksheet": "Sheet1",
  "service_account_path": "~/.config/gcp/autoacct-sa.json",
  "hkd_fx_provider": "frankfurter"
}
```

> **常见坑**：如果你的 Google Sheets 界面是中文，默认 tab 名是 `工作表1`，**不是** `Sheet1`。必须写成 `"worksheet": "工作表1"`。tab 名不对会报 `HTTP 400: Unable to parse range`。

### 冒烟测试

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' | python3 ~/.openclaw/workspace/skills/AutoACCT/scripts/append_row.py
```

看到 `OK 'Sheet1'!A2:N2`（或中文 tab 名）并且 sheet 第 2 行出现 TEST，就全通了。完事记得把这行测试数据删掉。

遇到报错可以参考 [`scripts/setup.md`](scripts/setup.md) 的故障排查。

## 管理员一次性配置（你做一遍，再把 JSON 发给用户）

用户能跑上面 4 步之前，**你（管理员）**先建好一个共享的 service account，把 JSON 发给用户。完整管理员指南见 [`scripts/setup.md`](scripts/setup.md)，简版流程：

1. 建 GCP 项目 → 启用 Sheets API → 建 service account → 下载 JSON key
2. 通过安全渠道把 JSON 文件 + service-account 邮箱发给每个用户（1Password / Bitwarden / 加密邮件 ——**绝不能 commit 到 git**）
3. 让用户按上面 4 步装

## 使用

在 OpenClaw 会话里把小票图片拖进来，然后说 "log this" / "记一下" 之类即可。Skill 会根据"小票/记账"类请求自动触发，**不需要** slash command。

文字说明可选，可用来补充上下文（支付方式、AA、分类提示、备注等）。

## 文件结构

| 文件                      | 作用                                              |
|---------------------------|---------------------------------------------------|
| `SKILL.md`                | 入口文件 — OpenClaw 读它来决定如何执行 skill     |
| `categories.md`           | 固定的 14 个分类列表                              |
| `schema.md`               | Google Sheet 列顺序（A–N）                        |
| `config.example.json`     | 配置模板 → 复制为 `config.json`（已 gitignore）    |
| `scripts/fx_convert.py`   | 原币种 → HKD 换算（frankfurter.app）              |
| `scripts/append_row.py`   | 向 Google Sheet 写入一行                          |
| `scripts/setup.md`        | 管理员配置指南 + 故障排查                          |
| `DEPLOY.md`               | 面向非技术用户的逐步安装指南（英文）              |

## License

[MIT](LICENSE) © 2026 Knowit
