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
- MCP 서버 (mcp-config.json에 설정된 경우): GitHub, Atlassian, Slack, Figma, Datadog 등

## 사용 불가 도구

- 브라우저, GUI 관련 도구

## 하지 말아야 할 것

- `.claude/settings.json` 생성 또는 수정 금지 — 이 환경에서는 불필요
- `workspace/` 외부 경로 수정 금지

## 작업 완료 규칙

- 변경사항은 반드시 커밋 또는 PR로 제출
- 작업 결과를 요약 코멘트로 남길 것 (가능하면 이슈/PR에)
- 오류 발생 시 중단하지 말고 가능한 범위까지 진행 후 결과 보고
