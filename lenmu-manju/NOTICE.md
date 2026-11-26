# NOTICE

本目錄是下列專案的 fork（修改版）：

- 來源：<https://github.com/lixiaoxiao9888-create/manju-laoli-skill>
- 版本：V8.2.0-SLIM，commit `5b7befe9d5ecde9ee4e624adf4456d4fe89aca2f`
- 授權：MIT，Copyright (c) 2026 Short-Drama Director Suite contributors（全文見 [LICENSE](LICENSE)）

## 相對上游的改動

**沒有帶過來的檔案**

- 倉庫根的 `README.md`（落地頁，含贊助與聯絡資訊）與 `assets/`（贊助商圖片）。
- `.gitignore`（併入本倉庫根的 `.gitignore`）。

**新增**

- `sd-lenmu-engine/`：Lenmu 執行層技能（`SKILL.md`、`scripts/lenmu_wiring.py`）。
- `README.md`、`NOTICE.md`（本目錄）。

**修改（全部是加法，標有「Lenmu 執行層（fork 增補）」或「Lenmu fork」字樣）**

| 檔案 | 改動 |
|---|---|
| `short-drama-director/SKILL.md` | frontmatter description 加一句；開工確認卡加第 9 項「執行方式」；B 鎖加 21:9 說明；新增 §〇·E.2；子技能路由表加 `sd-lenmu-engine` 一列 |
| `short-drama-director/references/asset-delivery-modes.md` | 文末新增 §十一「Lenmu 執行形態 M2-L」 |
| `sd-asset-engine/SKILL.md`、`sd-feed-engine/SKILL.md`、`sd-qc-engine/SKILL.md` | 各加一段指向 `sd-lenmu-engine` 的說明 |
| `short-drama-director/scripts/check_package.py` | 檢查項 ◑26 的檔案數比較由 `==` 改為 `<=`（照該檢查註解寫的「只卡不虛報」本意；上游原樣在乾淨 clone 上此項即不通過） |
| `run_all_checks.py` | 加一項 `lenmu_wiring.py --self-test` |
| `short-drama-director/scripts/build_board_lite.py` | 離線看板的 HTML 跳脫函式 `esc` 補上雙引號與單引號（原本只跳脫 `& < >`，鏡頭文字含引號時會打斷 `title` 屬性，也可被用來注入屬性） |

**全部內文轉為繁體中文**

- 所有 `.md` 與 `.py`（含腳本裡的訊息、比對字串與正規表示式）以 OpenCC `s2tw` 由簡體轉為繁體，再把「臺」統一為「台」。逐字轉換、不增刪內容，檔案長度（字數）不變。
- 自動轉換選錯字的地方已人工修正（例如 乾喊／乾聊／乾淨、髮型、只能／只有、複雜、上游、注意力、如鐘、面部／面容）。
- 因轉換而調整的兩處比對規則（`short-drama-director/scripts/validate_prompt.py`）：懸空指示代詞 C20b 的量詞同時接受「只／隻」；抽象比喻 C20c 同時接受「如鐘／如鍾」。
- 技能名稱、檔名、機檢代碼（C1~C41、G1~G8 等）與英文內容不變。

除上述之外，內容與上游該 commit 相同。
