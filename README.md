<div align="center">
  <img src="web/public/logo_main_page.png" alt="Agent Market Logo" width="200" />

  # Agent Market
  <a href="https://packyzhou.github.io/agent_marketing/">访问主页</a>

  **Clone Human Intelligence — Monetize Expertise Through AI**

  通过AI技术复制人类能力，实现专业经验的商业化变现

  AI技術で人間の能力を複製し、専門知識の商業化を実現

  [![Vue 3](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
  [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

<details>
<summary><b>🇨🇳 中文</b></summary>

### 项目简介

Agent Market 是一个功能完整的 AI 智能体 SaaS 平台。它将个人专业能力数字化，通过智能体市场进行交易，实现"人才克隆"的商业闭环。平台支持多租户架构、推荐分组、双层记忆系统、Token 用量分析和多语言界面（中文/英文/日文）。

**核心理念：** 将个人经验商品化，是实现全球生产力平权的第一步。

</details>

<details>
<summary><b>🇺🇸 English</b></summary>

### About

Agent Market is a full-featured AI agent SaaS platform. It digitizes personal expertise and trades it through an agent marketplace, creating a commercial closed-loop for "talent cloning." The platform supports multi-tenancy, referral grouping, dual-layer memory, token analytics, and a multilingual interface (Chinese/English/Japanese).

**Core Vision:** Commercializing personal experience is the first step towards global productivity equality.

</details>

<details>
<summary><b>🇯🇵 日本語</b></summary>

### プロジェクト概要

Agent Market は、フル機能の AI エージェント SaaS プラットフォームです。個人の専門能力をデジタル化し、エージェントマーケットプレイスで取引することで、「人材クローン」のビジネスサイクルを実現します。マルチテナント、紹介グループ、二層メモリシステム、トークン分析、多言語インターフェース（中国語/英語/日本語）をサポートしています。

**コアビジョン：** 個人の経験を商品化することは、グローバルな生産性の平等を実現するための第一歩です。

</details>

---

## Quick Start / 快速开始 / クイックスタート

### Prerequisites / 前置要求

- Docker Desktop 4.0+
- 4 GB+ available memory
- 10 GB+ available disk space

### Option 1 — Docker Compose (Recommended)

```bash
# Clone
git clone https://github.com/packyzhou/agent_marketing.git
cd agent_marketing

# Start all services
docker-compose up -d --build

# Wait 1-2 minutes, then verify
docker-compose ps
```

### Option 2 — Startup Script (Windows)

```bash
double-click start.bat
```

### Option 3 — Local Development

**Backend**

```bash
cd server
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd web
npm install
npm run dev
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

**Default Admin:** `admin` / `admin123`

### Configuration

<details>
<summary>Memory System — <code>server/agent_config.json</code></summary>

```json
{
  "memory_processing": {
    "rounds_threshold": 5,
    "enable_auto_processing": true,
    "digest_rounds": 10
  }
}
```

</details>

<details>
<summary>Environment — <code>docker-compose.yml</code></summary>

```yaml
environment:
  MYSQL_ROOT_PASSWORD: your-secure-password
  SECRET_KEY: your-jwt-secret-key
```

</details>

### Common Commands

```bash
docker-compose logs -f          # View logs
docker-compose restart          # Restart services
docker-compose down             # Stop services
docker-compose down -v          # Reset database
```

---

## Project Structure / 工程结构 / プロジェクト構造

```
agent_marketing/
├── server/                      # Backend (FastAPI + Python 3.11)
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin/          # Admin endpoints (users, tenants, providers, tokens, memory)
│   │   │   ├── user/           # User endpoints (auth, tenants, stats, memory)
│   │   │   └── proxy/          # AI proxy (chat completions)
│   │   ├── core/               # Config, DB, security, snowflake ID
│   │   ├── models/             # ORM models (8 tables)
│   │   ├── services/           # Memory engine, token service, LLM factory
│   │   └── main.py
│   ├── agent_config.json
│   ├── memory_files/
│   ├── Dockerfile
│   └── requirements.txt
├── web/                         # Frontend (Vue 3 + Vite)
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue        # Landing page & agent marketplace
│   │   │   ├── About.vue       # Cooperation form & project vision
│   │   │   ├── Docs.vue        # Documentation center
│   │   │   ├── Login.vue       # Auth (login / register)
│   │   │   ├── admin/          # Admin console (8 views)
│   │   │   └── user/           # User dashboard (7 views)
│   │   ├── components/         # Shared components (LangSwitcher)
│   │   ├── i18n/               # zh / en / ja translations
│   │   ├── router/
│   │   └── api/
│   ├── Dockerfile
│   └── package.json
├── init.sql                     # Database schema & seed data
├── docker-compose.yml
└── start.bat                    # One-click startup (Windows)
```

## Core Features / 核心功能 / コア機能

### AI Service Proxy / AI 服务中转

Unified API to multiple LLM providers (Qwen, Doubao, DeepSeek, etc.) with streaming support.

```bash
curl -X POST http://localhost:8000/api/proxy/chat/completions \
  -H "X-App-Key: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "model": "qwen-plus", "stream": false}'
```

### Dual-Layer Memory / 双层记忆系统 / 二層メモリシステム

| Layer | Description |
|-------|-------------|
| **KV Fact Memory** | Structured extraction — name, occupation, preferences, company |
| **Behavior Digest** | Recursive conversation summary, auto-compresses at 3000 chars |
| **Cross-Layer Refs** | Detects references to prior conversations |
| **Auto Trigger** | Configurable threshold (default: every 5 rounds) |

### Token Analytics / Token 统计 / トークン分析

Real-time per-tenant token tracking, daily aggregation, 30-day trend charts (ECharts), monthly comparison.

### Multi-Tenancy / 多租户 / マルチテナント

AppKey/AppSecret auth, tenant-level API isolation, provider key management, bound user association.

### Referral Groups / 推荐分组 / 紹介グループ

Referral-based automatic group creation, intra-group tenant visibility, group-level member management.

### i18n — Multilingual / 多语言 / 多言語

All pages support Chinese, English, and Japanese with a one-click language switcher. Preference persists via localStorage.

### Admin Console / 管理后台

Users, Roles & Permissions, Groups, Tenants, Providers, Token Stats, Memory Viewer, Chat Debug.

### User Dashboard / 用户中心

Dashboard (charts), My Tenants, Groups, Group Tenants, Tokens, Memory, Chat Debug (streaming SSE).

---

## Changelog / 更新日志 / 更新履歴

### v1.2.0 (2026-04-06)

- Redesigned `/about` page — cooperation inquiry form + project vision
- Added `/docs` documentation center with full deployment guide
- i18n: Chinese / English / Japanese with persistent language switcher
- Unified UI style across all pages (Home, Login, Admin, User) — Inter font, slate/cyan theme, glassmorphism nav
- Added new routes `/about`, `/docs` with public access

### v1.1.0 (2026-04-04)

- Role & permission management (CRUD, user role assignment)
- Admin global data views (users, groups, tenants, providers, tokens, memory)
- User profile management and personal memory viewer
- Top-bar user menu with profile edit and sign-out

### v1.0.0 (2026-04-03)

- Multi-tenant architecture with AppKey/AppSecret
- Referral grouping system
- Dual-layer memory (KV + Digest) with cross-layer reference detection
- Token usage analytics with 30-day trend visualization
- Admin console and user dashboard
- Conversation tracking and database-driven provider config
- Docker Compose one-click deployment

---

## Contact / 联系方式 / お問い合わせ

| | |
|---|---|
| **Initiator** | Mr. Joe |
| **Email** | packyzhou1990@gmail.com |
| **WeChat** | packyzhou |
| **GitHub** | [github.com/packyzhou/agent_marketing](https://github.com/packyzhou/agent_marketing) |

For cooperation inquiries, visit the [About page](http://localhost/about) on the live site, or submit a GitHub Issue.

---

<div align="center">

**MIT License** · Mr.Joe © 2026 · Designed for the intelligence era.

</div>
