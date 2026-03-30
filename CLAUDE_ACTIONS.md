# GitHub Actions 실행 지침

> 이 파일은 GitHub Actions 환경에서 Claude Code가 참고하는 지침입니다.
> 로컬 CLAUDE.md와 충돌하는 경우 이 파일을 우선합니다.

## 실행 환경

- **비대화형**: 사용자 확인 없이 작업을 완료해야 함
- **작업 디렉토리**: `workspace/` (대상 레포)
- **인증**: `GITHUB_TOKEN`, `GH_PAT` 자동 주입됨

## 사용 가능한 도구

- `bash` — gh CLI, git 명령 실행
- `read` / `write` / `edit` — 파일 작업
- MCP 서버 (mcp-config.json에 설정된 경우): Atlassian, Datadog, Figma

## 사용 불가 도구

- 브라우저, GUI 관련 도구

---

## 서비스별 사용 방법

### GitHub — gh CLI 사용

> **GitHub MCP는 사용하지 말 것.**
> `gh` CLI가 이미 인증된 상태로 제공되므로 MCP보다 빠르고 안정적임.
> `GH_TOKEN` 또는 `GITHUB_TOKEN`이 자동 주입되어 별도 인증 불필요.
> 다른 레포 접근이 필요할 때는 `GH_PAT`을 사용.

#### 필수 명령 목록

| 작업 | 명령 |
|------|------|
| PR 생성 | `gh pr create --title "..." --body "..." --repo owner/repo` |
| PR 목록 조회 | `gh pr list --repo owner/repo` |
| PR 상태 확인 | `gh pr view <number> --repo owner/repo` |
| 이슈 생성 | `gh issue create --title "..." --body "..."` |
| 이슈 목록 조회 | `gh issue list --repo owner/repo` |
| 파일 조회 | `gh api repos/owner/repo/contents/path` |
| 릴리즈 조회 | `gh release list --repo owner/repo` |
| 워크플로우 실행 | `gh workflow run workflow.yml --repo owner/repo` |
| Actions 실행 결과 | `gh run list --repo owner/repo` |
| 코드 검색 | `gh search code "키워드" --repo owner/repo` |

> 📖 전체 CLI 레퍼런스: https://cli.github.com/manual/

#### 예시: 다른 레포 파일 읽기

```bash
export GH_TOKEN=$GH_PAT
gh api repos/org/some-repo/contents/path/to/file \
  --jq '.content' | base64 -d
```

---

### Atlassian — MCP 우선, 없으면 REST API curl 사용

pip 패키지 `mcp-atlassian`으로 실행됨.
**툴명은 반드시 snake_case** — `getConfluencePage` 같은 camelCase 이름은 존재하지 않음.

> ⚠️ `fetchAtlassian` 툴은 이 환경에 없음. MCP에 없는 기능은 아래 REST API를 curl로 직접 호출할 것.

#### Confluence MCP 툴

| 작업 | 툴 |
|------|-----|
| 페이지 조회 | `confluence_get_page` |
| 페이지 검색 | `confluence_search` — CQL 쿼리 사용 |
| 스페이스 목록 | `confluence_search` — CQL: `space.type=global` |
| 페이지 생성 | `confluence_create_page` |
| 페이지 수정 | `confluence_update_page` |
| 사용자 검색 | `confluence_search_user` |

> ⚠️ `type=space` CQL은 동작하지 않음.

> Confluence 페이지 수정 순서:
> 1. `confluence_get_page` (contentFormat: "storage" 또는 "adf") — 현재 내용 조회
> 2. 내용 수정
> 3. `confluence_update_page` — 저장

#### Jira MCP 툴

| 작업 | 툴 |
|------|-----|
| 이슈 조회 | `jira_get_issue` |
| 이슈 검색 | `jira_search` — JQL 쿼리 사용 |
| 이슈 생성 | `jira_create_issue` |
| 이슈 수정 | `jira_update_issue` |
| 프로젝트 이슈 목록 | `jira_get_project_issues` |
| 사용자 프로필 | `jira_get_user_profile` — 이메일 또는 accountId 필요 |

#### Atlassian REST API — MCP에 없는 기능은 curl로 직접 호출

인증: Basic Auth (`ATLASSIAN_EMAIL:ATLASSIAN_API_TOKEN`)

```bash
curl -sf "https://{your-domain}.atlassian.net/..." \
  -u "$ATLASSIAN_EMAIL:$ATLASSIAN_API_TOKEN" \
  -H "Accept: application/json"
```

**Jira REST API**

| 작업 | API |
|------|-----|
| 현재 사용자 조회 | `GET /rest/api/3/myself` |
| accountId로 사용자 조회 | `GET /rest/api/3/user?accountId={accountId}` |
| 이메일로 사용자 검색 | `GET /rest/api/3/user/search?query={email}` |
| 이슈 조회 | `GET /rest/api/3/issue/{issueKey}` |
| JQL 검색 | `GET /rest/api/3/search?jql={jql}&maxResults=50` |

**Confluence REST API**

| 작업 | API |
|------|-----|
| 현재 사용자 조회 | `GET /wiki/rest/api/user/current` |
| accountId로 사용자 조회 | `GET /wiki/rest/api/user?accountId={accountId}` |
| 페이지 조회 | `GET /wiki/rest/api/content/{pageId}?expand=body.storage,version` |
| CQL 검색 | `GET /wiki/rest/api/content/search?cql={cql}&limit=10` |

> 📖 Jira REST API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
> 📖 Confluence REST API: https://developer.atlassian.com/cloud/confluence/rest/v1/

---

### Slack — curl 사용

> **Slack MCP (`mcp__slack__`)는 사용하지 말 것.**
> 워크스페이스 채널·사용자 수가 많을 경우 목록 조회 시 응답이 수십만 자를 초과할 수 있음.
> **모든 Slack 작업은 `curl` + `SLACK_BOT_TOKEN`으로 직접 호출한다.**

#### 인증

```bash
-H "Authorization: Bearer $SLACK_BOT_TOKEN"
-H "Content-Type: application/json"
```

#### 필수 API 목록

| 작업 | 메서드 | API |
|------|--------|-----|
| 메시지 전송 | POST | `https://slack.com/api/chat.postMessage` |
| 메시지 수정 | POST | `https://slack.com/api/chat.update` |
| 스레드 답글 | POST | `https://slack.com/api/chat.postMessage` — `thread_ts` 포함 |
| 채널 히스토리 | GET | `https://slack.com/api/conversations.history` |
| 스레드 메시지 조회 | GET | `https://slack.com/api/conversations.replies` |
| 이메일로 사용자 조회 | GET | `https://slack.com/api/users.lookupByEmail` |
| 사용자 ID로 정보 조회 | GET | `https://slack.com/api/users.info` |
| 리액션 추가 | POST | `https://slack.com/api/reactions.add` |

> 📖 전체 API 레퍼런스: https://api.slack.com/methods

#### 예시: 메시지 전송

```bash
curl -sf -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel": "CHANNEL_ID", "text": "메시지 내용"}'
```

> 채널 ID 확인: Slack URL `https://your-workspace.slack.com/archives/CXXXXXXXXXX` 에서 추출

---

### Datadog — MCP 사용 (`mcp__datadog__`)

HTTP MCP 서버 (`https://mcp.datadoghq.com`).
access_token은 action.yml에서 `DATADOG_MCP_TOKEN` (refresh_token) → `DATADOG_ACCESS_TOKEN`으로 자동 교환 후 주입됨.

| 작업 | 툴 |
|------|-----|
| 모니터 검색 | `search_datadog_monitors` |
| 대시보드 검색 | `search_datadog_dashboards` |
| 로그 검색 | `search_datadog_logs` |
| 로그 분석 | `analyze_datadog_logs` |
| 메트릭 검색 | `search_datadog_metrics` |
| 메트릭 조회 | `get_datadog_metric` |
| 메트릭 컨텍스트 | `get_datadog_metric_context` |
| 인시던트 검색 | `search_datadog_incidents` |
| 인시던트 조회 | `get_datadog_incident` |
| 이벤트 검색 | `search_datadog_events` |
| 호스트 검색 | `search_datadog_hosts` |
| 서비스 검색 | `search_datadog_services` |
| 서비스 의존성 | `search_datadog_service_dependencies` |
| 트레이스 조회 | `get_datadog_trace` |
| 스팬 검색 | `search_datadog_spans` |
| RUM 이벤트 검색 | `search_datadog_rum_events` |
| 노트북 검색 | `search_datadog_notebooks` |
| 노트북 조회 | `get_datadog_notebook` |
| MCP 설정 확인 | `check_datadog_mcp_setup` |

---

### Figma — MCP 사용 (`mcp__figma__`)

`figma-developer-mcp` 패키지를 통해 MCP로 제공됨. `FIGMA_ACCESS_TOKEN` (Personal Access Token) 기반.

| 작업 | 툴 |
|------|-----|
| 파일 전체 데이터 조회 | `mcp__figma__get_figma_data` — `fileKey` 필수 |
| 이미지 다운로드 | `mcp__figma__download_figma_images` — `fileKey` 필수 |

> file_key: Figma URL `figma.com/design/{file_key}/...`에서 추출
> 계정 정보(whoami) 조회 툴은 제공되지 않음

---

## 하지 말아야 할 것

- `.claude/settings.json` 생성 또는 수정 금지 — 이 환경에서는 불필요
- `workspace/` 외부 경로 수정 금지
- GitHub MCP 툴 호출 금지 — `gh` CLI로 대체
- Slack MCP 툴(`mcp__slack__*`) 호출 금지 — curl로 대체
- `mcp__atlassian__fetchAtlassian` 호출 금지 — REST API curl로 대체

## 작업 완료 규칙

- 변경사항은 반드시 커밋 또는 PR로 제출
- 작업 결과를 요약 코멘트로 남길 것 (가능하면 이슈/PR에)
- 오류 발생 시 중단하지 말고 가능한 범위까지 진행 후 결과 보고
