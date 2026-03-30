# Claude Launcher MCP 설정 가이드

`.github/actions/mcp-setup/mcp-config.json`에 MCP 서버가 정의되어 있으며,
GitHub Actions 실행 시 Secrets에서 환경변수를 주입합니다.

> **시작 전:** `mcp-config.json`의 `your-domain.atlassian.net`을 실제 Atlassian 도메인으로 변경하세요.

---

## 필요한 GitHub Secrets

| Secret | 해당 서비스 | 발급 방법 |
|--------|------------|-----------|
| `CLAUDE_CODE_TOKEN` | Claude | Claude Code OAuth 토큰 |
| `GH_PAT` | GitHub | [GitHub Personal Access Token](https://github.com/settings/tokens) — `repo`, `read:org` 권한 |
| `ATLASSIAN_EMAIL` | Atlassian | Atlassian 계정 이메일 |
| `ATLASSIAN_API_TOKEN` | Atlassian | [Atlassian API 토큰 발급](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `SLACK_BOT_TOKEN` | Slack | 아래 참고 (`xoxb-` 형식) |
| `DATADOG_MCP_TOKEN` | Datadog | 아래 참고 (JSON 형식) |
| `FIGMA_ACCESS_TOKEN` | Figma | [Figma Personal Access Token](https://www.figma.com/developers/api#access-tokens) |

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

1. https://id.atlassian.com/manage-profile/security/api-tokens 에서 API 토큰 발급
2. `ATLASSIAN_EMAIL`: Atlassian 로그인 이메일
3. `ATLASSIAN_API_TOKEN`: 발급한 API 토큰
4. `mcp-config.json`의 `your-domain.atlassian.net` → 실제 도메인으로 수정

---

## Datadog 설정

`DATADOG_MCP_TOKEN`은 JSON 형식입니다:

```json
{"client_id": "YOUR_CLIENT_ID", "refresh_token": "YOUR_REFRESH_TOKEN"}
```

1. **API Key**: https://app.datadoghq.com/organization-settings/api-keys
2. **Application Key**: https://app.datadoghq.com/organization-settings/application-keys

---

## Figma 설정

1. Figma → 우측 상단 프로필 → **Settings**
2. **Security** 탭 → **Personal access tokens** → **Generate new token**
3. Secret 이름: `FIGMA_ACCESS_TOKEN`
