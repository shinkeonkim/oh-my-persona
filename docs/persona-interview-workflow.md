# 김신건 직접 답변 데이터 증강

`data/questionnaires/persona-questions.jsonl`의 50개 질문에 로컬에서 답한다. 답변 파일은
example과 같은 JSONL이며 `question_id`, `answer`, `answered_at`, `visibility`,
`evidence_urls`를 기록한다.

- 공개 가능한 답변만 `visibility: public`으로 둔다.
- 날짜가 확실하면 일·월·연도 정확도를 유지하고, 기억에 의존하면 답변에 그 사실을 적는다.
- 회사·군·커뮤니티의 비공개 정보와 제3자 개인정보는 넣지 않는다.
- 답변은 `data/answers/persona-answers.jsonl`에 두고 다음 명령으로 검증·승격한다.

```bash
persona build-answers --answers data/answers/persona-answers.jsonl
persona chunk
persona audit
persona evaluate
```

승격 결과는 `data/curated/persona-interview-answers.md`와 문서 레지스트리에 생성된다.
`private` 또는 빈 답변은 승격되지 않는다.
