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

## 安装

按下面 6 步操作，整个过程约 10 分钟。

### Step 1 — Clone 仓库 + 装 Python 依赖

```bash
git clone https://git.deepknow.site/Knowit/AutoACCT.git ~/.openclaw/workspace/skills/AutoACCT
pip install google-api-python-client google-auth
```

### Step 2 — 建 Google Cloud 服务账号

1. 打开 https://console.cloud.google.com/，左上角下拉 → **New Project** → 随便起名（如 `autoacct`）→ Create
2. 顶部搜索框搜 **Google Sheets API** → 点进去 → **Enable**
3. 左侧菜单 **IAM & Admin → Service Accounts → + Create Service Account**
   - Name 填 `AutoACCT`（随意）
   - 点 **Create and Continue → Done**（中间可选的 role 步骤跳过）
4. 点进刚建好的服务账号 → 顶部 **Keys** 标签 → **Add Key → Create new key → 选 JSON → Create**
   浏览器会自动下载一个 `.json` 文件到你的 Downloads
5. **复制服务账号的 email**（形如 `autoacct@<项目名>.iam.gserviceaccount.com`），Step 4 要用

### Step 3 — 把 key 文件挪出 repo

**千万不要**把 key 留在 repo 目录里。挪到 `~/.config/gcp/`：

```bash
mkdir -p ~/.config/gcp
mv ~/Downloads/<你下载的文件名>.json ~/.config/gcp/autoacct-sa.json
chmod 600 ~/.config/gcp/autoacct-sa.json
```

### Step 4 — 建 Google Sheet

1. 打开 https://sheets.new（直接创建空白 sheet）
2. 给 sheet 起个标题（如 `AutoACCT Expenses`）
3. **记住左下角 tab 的名字** — 英文界面默认 `Sheet1`，中文界面默认 `工作表1`。Step 5 要用这个**精确字符串**
4. 点进 **A1** 单元格，粘贴下面这一整行（中间是 Tab 分隔，粘进去会自动拆到 A1–N1）：
   ```
   Date	Merchant	Category	Amount	Currency	Amount (HKD)	FX Rate	FX Date	Payment Method	Line Items	Raw OCR	Note	Receipt	Logged At
   ```
5. 右上角 **Share** → 粘贴 Step 2 复制的服务账号 email → 权限选 **Editor** → **Send**（"Notify people" 可以不勾）
6. 从 URL 里复制 **Sheet ID** —— `/d/` 和 `/edit` 之间那一长串：
   `https://docs.google.com/spreadsheets/d/`**`1abc...xyz`**`/edit`

### Step 5 — 写 config.json

```bash
cd ~/.openclaw/workspace/skills/AutoACCT
cp config.example.json config.json
```

用编辑器打开 `config.json`，把 Step 4 拿到的 **sheet_id** 和 **worksheet**（tab 名）填进去：

```json
{
  "sheet_id": "1abc...xyz",
  "worksheet": "Sheet1",
  "service_account_path": "~/.config/gcp/autoacct-sa.json",
  "hkd_fx_provider": "frankfurter"
}
```

> ⚠️ **常见坑**：如果你的 Google Sheets 界面是中文，默认 tab 名是 `工作表1`，**不是** `Sheet1`。必须写成 `"worksheet": "工作表1"`。tab 名不对会报 `HTTP 400: Unable to parse range`。

### Step 6 — 冒烟测试

```bash
echo '{"date":"2026-04-20","merchant":"TEST","category":"Other","amount":1,"currency":"HKD","amount_hkd":1,"fx_rate":1,"fx_date":"2026-04-20"}' | python3 ~/.openclaw/workspace/skills/AutoACCT/scripts/append_row.py
```

看到 `OK 'Sheet1'!A2:N2`（或中文 tab 名）并且 sheet 第 2 行出现 TEST，就全通了。完事记得把这行测试数据删掉。

遇到报错可以参考 [`scripts/setup.md`](scripts/setup.md) 的详细版。

## 使用

在 OpenClaw 会话里把小票图片拖进来，然后说 "log this" / "记一下" 之类即可。Skill 会根据"小票/记账"类请求自动触发，**不需要** slash command。

文字说明可选，可用来补充上下文（支付方式、AA、分类提示、备注等）。

## 文件结构

| 文件                   | 作用                                          |
|------------------------|-----------------------------------------------|
| `SKILL.md`             | 入口文件 — OpenClaw 读它来决定如何执行 skill |
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
