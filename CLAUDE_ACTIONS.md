# GitHub Actions 실행 지침

> GitHub Actions 환경에서 Claude Code가 참고하는 지침입니다.
> 로컬 CLAUDE.md와 충돌하는 경우 **이 파일을 우선합니다.**

## 실행 환경

| 항목 | 내용 |
|------|------|
| 실행 방식 | 비대화형 — 사용자 확인 없이 작업 완료 |
| 작업 디렉토리 | `workspace/` (대상 레포를 별도 checkout한 경우) |
| 사용 불가 | 브라우저, GUI 관련 도구 |

---

## 서비스별 사용 방식 (빠른 참조)

| 서비스 | 방식 | 비고 |
|--------|------|------|
| GitHub | `gh` CLI | GitHub Actions 실행 시 `GITHUB_TOKEN` 자동 제공 |
| Atlassian (Confluence/Jira) | MCP 우선 → curl 폴백 | `mcp-atlassian` 패키지 |
| Slack | curl | MCP 사용 금지 |
| Datadog | MCP | HTTP MCP 서버 |
| Figma | MCP 우선 → curl 폴백 | `figma-developer-mcp` 패키지 |

---

## GitHub — `gh` CLI

> Ubuntu runner에 `gh` CLI가 기본 내장되어 있어 MCP보다 빠르고 안정적임.
> `GITHUB_TOKEN`은 GitHub Actions 실행 시 자동 생성·주입되는 임시 토큰으로, 별도 인증 설정 없이 org 내 모든 레포에 접근 가능.

```bash
gh api repos/socar-inc/some-repo/contents/path/to/file \
  --jq '.content' | base64 -d
```

> 📖 https://cli.github.com/manual/

---

## Atlassian — MCP 우선, 없으면 REST API curl

> `mcp-atlassian` pip 패키지로 실행됨.
> **툴명은 snake_case** — `getConfluencePage` 같은 camelCase 이름은 없음.
> `mcp__atlassian__fetchAtlassian` 호출 금지 — 없는 툴임, curl로 대체.

### Confluence MCP

| 작업 | 툴 |
|------|-----|
| 페이지 조회 | `confluence_get_page` |
| 페이지 검색 | `confluence_search` — CQL 쿼리 |
| 스페이스 목록 | `confluence_search` — CQL: `space.type=global` |
| 페이지 생성 | `confluence_create_page` |
| 페이지 수정 | `confluence_update_page` |
| 사용자 검색 | `confluence_search_user` |

> ⚠️ `type=space` CQL은 동작하지 않음.

**페이지 수정 순서:** `confluence_get_page` (storage/adf) → 내용 수정 → `confluence_update_page`

### Jira MCP

| 작업 | 툴 |
|------|-----|
| 이슈 조회 | `jira_get_issue` |
| 이슈 검색 | `jira_search` — JQL 쿼리 |
| 이슈 생성 | `jira_create_issue` |
| 이슈 수정 | `jira_update_issue` |
| 프로젝트 이슈 목록 | `jira_get_project_issues` |
| 사용자 프로필 | `jira_get_user_profile` — 이메일 또는 accountId |

### Atlassian REST API (curl 폴백)

인증: Basic Auth

```bash
curl -sf "https://socarcorp.atlassian.net/..." \
  -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" \
  -H "Accept: application/json"
```

| 서비스 | 작업 | 엔드포인트 |
|--------|------|-----------|
| Jira | 현재 사용자 | `GET /rest/api/3/myself` |
| Jira | 이슈 조회 | `GET /rest/api/3/issue/{issueKey}` |
| Jira | JQL 검색 | `GET /rest/api/3/search?jql={jql}&maxResults=50` |
| Jira | 이메일로 사용자 | `GET /rest/api/3/user/search?query={email}` |
| Confluence | 현재 사용자 | `GET /wiki/rest/api/user/current` |
| Confluence | 페이지 조회 | `GET /wiki/rest/api/content/{pageId}?expand=body.storage,version` |
| Confluence | CQL 검색 | `GET /wiki/rest/api/content/search?cql={cql}&limit=10` |

> 📖 [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) · [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/)

---

## Slack — curl

> MCP 툴(`mcp__slack__*`) 호출 금지. 워크스페이스 규모가 커서 목록 조회 응답이 수십만 자를 초과함.

인증: `Authorization: Bearer $SLACK_BOT_TOKEN`

| 작업 | 메서드 | API |
|------|--------|-----|
| 메시지 전송 | POST | `chat.postMessage` |
| 메시지 수정 | POST | `chat.update` |
| 스레드 답글 | POST | `chat.postMessage` + `thread_ts` |
| 채널 히스토리 | GET | `conversations.history` |
| 스레드 조회 | GET | `conversations.replies` |
| 이메일로 사용자 | GET | `users.lookupByEmail` |
| 사용자 정보 | GET | `users.info` |
| 리액션 추가 | POST | `reactions.add` |

base URL: `https://slack.com/api/`

```bash
curl -sf -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel": "<채널 ID>", "text": "메시지 내용"}'
```

> 채널 ID: Slack URL `https://socar.slack.com/archives/CXXXXXXXXXX` 에서 추출
> 📖 https://api.slack.com/methods

---

## Datadog — MCP (`mcp__datadog__`)

> HTTP MCP 서버 (`https://mcp.datadoghq.com`).
> `DATADOG_MCP_TOKEN` → `DATADOG_ACCESS_TOKEN` 자동 교환 후 주입됨.

| 카테고리 | 툴 |
|----------|-----|
| 모니터 | `search_datadog_monitors` |
| 대시보드 | `search_datadog_dashboards` |
| 로그 | `search_datadog_logs` · `analyze_datadog_logs` |
| 메트릭 | `search_datadog_metrics` · `get_datadog_metric` · `get_datadog_metric_context` |
| 인시던트 | `search_datadog_incidents` · `get_datadog_incident` |
| 이벤트 | `search_datadog_events` |
| 인프라 | `search_datadog_hosts` · `search_datadog_services` · `search_datadog_service_dependencies` |
| APM | `get_datadog_trace` · `search_datadog_spans` |
| RUM | `search_datadog_rum_events` |
| 노트북 | `search_datadog_notebooks` · `get_datadog_notebook` |
| 설정 확인 | `check_datadog_mcp_setup` |

---

## Figma — MCP 우선, 없으면 REST API curl

> `figma-developer-mcp` 패키지를 통해 MCP로 제공됨. `FIGMA_ACCESS_TOKEN` (PAT) 기반.

### Figma MCP

| 작업 | 툴 |
|------|-----|
| 파일 데이터 조회 | `mcp__figma__get_figma_data` — `fileKey` 필수 |
| 이미지 다운로드 | `mcp__figma__download_figma_images` — `fileKey` 필수 |

> file_key: Figma URL `figma.com/design/{file_key}/...` 에서 추출
> 계정 정보(whoami) 조회 툴은 제공되지 않음

### Figma REST API (curl 폴백)

인증: `X-Figma-Token: $FIGMA_ACCESS_TOKEN`

| 작업 | 메서드 | API |
|------|--------|-----|
| 내 계정 정보 | GET | `https://api.figma.com/v1/me` |
| 파일 조회 | GET | `https://api.figma.com/v1/files/{file_key}` |
| 노드 조회 | GET | `https://api.figma.com/v1/files/{file_key}/nodes?ids={node_ids}` |
| 컴포넌트 목록 | GET | `https://api.figma.com/v1/files/{file_key}/components` |
| 스타일 목록 | GET | `https://api.figma.com/v1/files/{file_key}/styles` |
| 변수(토큰) 조회 | GET | `https://api.figma.com/v1/files/{file_key}/variables/local` |
| 이미지 URL | GET | `https://api.figma.com/v1/images/{file_key}?ids={node_ids}` |
| 댓글 조회/작성 | GET/POST | `https://api.figma.com/v1/files/{file_key}/comments` |

> 📖 https://www.figma.com/developers/api

---

## 작업 완료 규칙

- 변경사항은 반드시 커밋 또는 PR로 제출
- 작업 결과를 요약 코멘트로 남길 것 (가능하면 이슈/PR에)
- 오류 발생 시 중단하지 말고 가능한 범위까지 진행 후 결과 보고
