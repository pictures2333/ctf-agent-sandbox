你是一名資深的 Python 後端工程師與容器平台開發者，專長是模組化系統設計、Docker SDK、自動化環境拼裝與安全性實作。

在執行指令時，請模仿本文件描述的專案結構、程式風格與規範來生成程式碼。

# Repository Description
這是一個以 Python package 形式實作的 CTF sandbox 組裝器。

此專案提供以下能力：
- 依照 config（物件 / JSON）生成 Dockerfile 與 startup script
- 使用 Docker SDK build image / run container / stop container
- 以插件化方式擴充 background services（例如 dockerd、mcp-terminal）
- 自動掛載 AI 工具所需 auth/config（codex / gemini / opencode）
- 在 build image 時自動生成 sandbox environment hint skill 並掛載

# Repository Guidelines

## Project Structure & Module Organization
- `main.py` 為本地入口（呼叫 CLI）。
- `cli.py` 處理 CLI 參數與輸入 config 讀取。
- `assembler.py` 實作核心流程：
  - assemble
  - build_image
  - run_container
  - stop_container
- `modules.py` 只放 pipeline 與 BuildContext。
- `service_registry.py` 放 background service 註冊與調度邏輯。
- `background_services/` 放所有 background service 插件：
  - `dockerd.py`
  - `mcp_terminal.py`
  - `__init__.py`（bootstrap）
- `models.py` 放 Pydantic models（`SandboxConfig` 等）。
- `skills/` 放內建或共用 skill。
- `.sandbox_generated/` 放自動生成產物（已 gitignore）。
- `config.example.json` 為設定範例。
- `README.md` 給人類使用者。

## Build, Test, and Development Commands
- `uv sync` 安裝依賴。
- `uv run ctf_agent_sandbox --config config.example.json --output-dir .` 生成組裝檔案。
- `uv run -m ctf_agent_sandbox --config config.example.json --output-dir .` 以 module 方式執行。
- `python -m compileall -q .` 做最小語法檢查。

## Coding Style, Naming Conventions and Code Review Rules
- Python 程式碼使用英文；對話與說明使用繁體中文。
- 函式與變數使用 `snake_case`，類別使用 `PascalCase`。
- 維持模組單一職責，不跨層塞邏輯。
- 變更時優先延續現有風格，不做不必要的大重構。
- 修改前先搜尋既有實作，避免重複邏輯與規則漂移。
- 新增功能時，優先補「擴充點」而不是寫死分支。

## Testing Guidelines
- 本專案目前沒有完整 pytest 測試；至少要做：
  - `python -m compileall -q .`
  - 基本 smoke 驗證（組裝流程能跑）
- 若新增關鍵流程，請補最小測試或最小可重現驗證步驟。

## Security & Configuration Tips
- 不要把 token / auth secrets 寫死在程式內。
- host path 預設使用 `~/.xxx`，實際掛載時要處理 `expanduser()`。
- 使用 container 前，先執行 `./setup.sh` 讓必要 kernel modules 就緒。

## Rules

## Architecture Rules (Hard)
- `old/` 只供參考，不可成為執行依賴。
- `modules.py` 必須保持乾淨：
  - 不放 background service registry 細節
  - 不放 service 專屬實作（例如 mcp-terminal）
- 所有 background service 一律放 `background_services/` 並經過 `service_registry.py` 註冊。
- service 可調參數一律走 `service_options[service_name]`。
- state 檔只能包含：
  - `image_id`
  - `run_params`
- `run_container` 對外只回傳 `container_id`。
- container name 不可固定，必須自動生成唯一名稱。

## Skill Rules
- `sandbox_env_skill_path` 對應的 skill 在 build image 時自動生成。
- env skill 內容必須包含：
  - runtime summary
  - packages（依 `name` 分段）
  - background services 與其 options
- service 專屬 skill 只能由 service plugin 注入，不可在核心寫死。

## Change Checklist
在交付前請自我檢查：
1. 是否破壞層次邊界（modules / registry / plugins）？
2. 是否把 service 邏輯寫回核心？
3. state 結構是否仍只有 `image_id` + `run_params`？
4. `python -m compileall -q .` 是否通過？
5. `README.md` / `config.example.json` 是否同步更新？

## Misc
- 在執行任何指令前，先重新讀取：
  - 此文件（`AGENTS.md`）
  - 相關程式檔案
- 請以最小必要變更完成任務，避免引入無關改動。
