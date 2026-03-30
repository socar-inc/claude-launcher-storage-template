# Claude Launcher MCP 설정 가이드

`.github/actions/mcp-setup/mcp-config.json`에 MCP 서버가 정의되어 있으며,
GitHub Actions 실행 시 Secrets에서 환경변수를 주입합니다.

---

## 필요한 GitHub Secrets

| Secret | 해당 서비스 | 발급 방법 |
|--------|------------|-----------|
| `CLAUDE_CODE_TOKEN` | Claude | 아래 참고 |
| `ATLASSIAN_EMAIL` | Atlassian | Atlassian 계정 이메일 |
| `ATLASSIAN_API_TOKEN` | Atlassian | [Atlassian API 토큰 발급](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `SLACK_BOT_TOKEN` | Slack | 아래 참고 (`xoxb-` 형식) |
| `DATADOG_MCP_TOKEN` | Datadog | 아래 참고 (JSON 형식) |
| `FIGMA_ACCESS_TOKEN` | Figma | [Figma Personal Access Token](https://www.figma.com/developers/api#access-tokens) |

> **GitHub 인증:** `GITHUB_TOKEN`은 GitHub Actions 실행 시 자동 제공되므로 별도 설정 불필요.

---

## CLAUDE_CODE_TOKEN 설정

**방법 1 — 수동**

```bash
claude setup-token
```

출력된 토큰(`sk-ant-` / `euauth_` / `oa_` 로 시작)을 `CLAUDE_CODE_TOKEN` 시크릿으로 등록

**방법 2 — claude-launcher 앱**

앱 하단 상태바 **⚡ Storage** → `CLAUDE_CODE_TOKEN` **발급** 버튼

---

## Slack 설정

### 봇 토큰 확인
```bash
curl -H "Authorization: Bearer <token>" https://slack.com/api/auth.test
```

### 채널 접근 설정
봇이 메시지를 보내려면 해당 채널에 초대되어 있어야 합니다.
```
/invite @your-bot-name
```

---

## Atlassian 설정

Atlassian 도메인: `socarcorp.atlassian.net`

1. https://id.atlassian.com/manage-profile/security/api-tokens 에서 API 토큰 발급
2. `ATLASSIAN_EMAIL`: Atlassian 로그인 이메일
3. `ATLASSIAN_API_TOKEN`: 발급한 API 토큰

---

## Datadog 설정

`DATADOG_MCP_TOKEN`은 OAuth 2.1 PKCE 플로우로 발급되는 JSON 형식입니다:

```json
{"client_id": "...", "refresh_token": "..."}
```

**방법 1 — 수동**

```bash
python3 scripts/datadog-mcp-auth.py
```

브라우저에서 Datadog 로그인 → 출력된 JSON을 `DATADOG_MCP_TOKEN` 시크릿에 저장

**방법 2 — claude-launcher 앱**

앱 하단 상태바 **⚡ Storage** → `DATADOG_MCP_TOKEN` **🔑 OAuth 인증** 버튼

> 토큰 전체 revoke: https://app.datadoghq.com/personal-settings/apps → `_datadog` Disable

---

## Figma 설정

1. Figma → 우측 상단 프로필 → **Settings**
2. **Security** 탭 → **Personal access tokens** → **Generate new token**
3. Secret 이름: `FIGMA_ACCESS_TOKEN`
