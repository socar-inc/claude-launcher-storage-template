# claude-launcher-storage

Claude Launcher의 스케줄 및 자동화 워크플로우 저장소입니다.

---

## 시작 전 준비

> `mcp-config.json`의 Atlassian URL을 실제 도메인으로 변경하세요.
> `.github/actions/mcp-setup/mcp-config.json` → `your-domain.atlassian.net` 수정

---

## GitHub Actions 토큰 설정

Repository Settings → Secrets and variables → Actions 에 등록합니다.

| Secret | 설명 | 사용 워크플로우 |
|--------|------|----------------|
| `CLAUDE_CODE_TOKEN` | Claude Code OAuth 토큰 | 전체 |
| `GH_PAT` | GitHub Personal Access Token (다른 org 레포 접근용) | 전체 |
| `ATLASSIAN_EMAIL` | Atlassian 계정 이메일 | Atlassian |
| `ATLASSIAN_API_TOKEN` | Atlassian API 토큰 | Atlassian |
| `SLACK_BOT_TOKEN` | Slack Bot Token (`xoxb-` 형식) | Slack |
| `DATADOG_MCP_TOKEN` | Datadog MCP 토큰 (JSON: `{client_id, refresh_token}`) | Datadog |
| `FIGMA_ACCESS_TOKEN` | Figma Personal Access Token | Figma |

---

## MCP 동작 구조

Claude 실행 전 `.github/actions/mcp-setup` 이 MCP 서버를 설치하고 환경을 준비합니다.

```
워크플로우 실행
    │
    ├── mcp-setup action
    │       ├── MCP 서버 설치 (토큰이 있는 서비스만)
    │       │       ├── mcp-atlassian (pip)       ← ATLASSIAN_API_TOKEN 있을 때
    │       │       └── figma-developer-mcp (npm)  ← FIGMA_ACCESS_TOKEN 있을 때
    │       ├── Datadog OAuth 토큰 교환
    │       │       └── DATADOG_MCP_TOKEN → DATADOG_ACCESS_TOKEN
    │       ├── /tmp/mcp-config.json 생성 (mcp-config.json 템플릿 + 토큰 주입)
    │       └── curl용 시크릿 환경변수 주입 (SLACK_BOT_TOKEN 등)
    │
    └── Claude 실행
            ├── --mcp-config /tmp/mcp-config.json 으로 MCP 서버 연결
            └── CLAUDE_ACTIONS.md 읽고 서비스별 사용 방법 참고
```

### 서비스별 접근 방식

| 서비스 | 방식 | 비고 |
|--------|------|------|
| GitHub | `gh` CLI | `GITHUB_TOKEN` 자동 주입, 다른 org는 `GH_PAT` |
| Atlassian | MCP (`mcp-atlassian`) | Confluence / Jira |
| Slack | curl | MCP 미사용, `SLACK_BOT_TOKEN` 환경변수로 직접 호출 |
| Datadog | MCP (HTTP) | `https://mcp.datadoghq.com` |
| Figma | MCP (`figma-developer-mcp`) → curl 폴백 | |

관련 파일:
- `.github/actions/mcp-setup/action.yml` — MCP 설치 및 환경 준비
- `.github/actions/mcp-setup/mcp-config.json` — MCP 서버 설정 템플릿 (**Atlassian URL 수정 필요**)
- `CLAUDE_ACTIONS.md` — Claude가 참고하는 서비스별 사용 지침

---

## 테스트 워크플로우

각 서비스 연동을 독립적으로 검증할 수 있는 테스트 워크플로우입니다.
Actions 탭에서 수동 실행(`workflow_dispatch`)합니다.

| 워크플로우 | 테스트 내용 |
|-----------|------------|
| `Test - Claude Atlassian(MCP)` | Confluence MCP로 스페이스 목록 조회 |
| `Test - Claude Datadog(MCP)` | Datadog MCP로 모니터 조회 |
| `Test - Claude Figma(MCP)` | Figma MCP로 파일 데이터 조회 |
| `Test - Claude Figma(CURL)` | Figma REST API curl로 계정 정보 조회 |
| `Test - Claude Slack(CURL)` | Slack API curl로 메시지 전송 |
| `Test - Claude GitHub(CLI)` | `gh` CLI로 PR 조회 및 다른 org 파일 읽기 |
