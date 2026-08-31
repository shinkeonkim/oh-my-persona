# 김신건 직접 답변 데이터 증강

먼저 현재 corpus가 각 질문을 얼마나 답할 수 있는지 분석한다.

```bash
uv run persona knowledge-gaps
```

이 명령은 `data/processed/knowledge-gaps.json`에 질문별 상태와 근거 URL을 기록하고,
`data/questionnaires/persona-answers.todo.jsonl`에 답변 초안을 만든다.

- `empty`: 인용 가능한 자료가 없다. 가장 먼저 직접 답변하거나 추가 자료를 찾는다.
- `single_source`: 한 출처에만 의존한다. 직접 답변과 독립 근거를 보강한다.
- `indirect_evidence`: 관련 자료는 있지만 질문에 대한 본인의 직접 답이 없다.
- `direct_answer`: 이미 직접 답변이 있다. 관점이나 날짜가 바뀐 경우에만 갱신한다.

검색 결과가 없다는 사실만으로 실제 경험이 없다고 결론 내리지 않는다. 공백 보고서는
“현재 corpus가 모른다”는 뜻이며, AI가 사실을 만들어 채우는 입력으로 사용하지 않는다.

`data/questionnaires/persona-questions.jsonl`의 50개 질문에 로컬에서 답한다. 답변 파일은
example과 같은 JSONL이며 `question_id`, `answer`, `answered_at`, `visibility`,
`evidence_urls`를 기록한다.

- 공개 가능한 답변만 `visibility: public`으로 둔다.
- 날짜가 확실하면 일·월·연도 정확도를 유지하고, 기억에 의존하면 답변에 그 사실을 적는다.
- 회사·군·커뮤니티의 비공개 정보와 제3자 개인정보는 넣지 않는다.
- 답변은 `data/answers/persona-answers.jsonl`에 두고 다음 명령으로 검증·승격한다.
- 권장 순서는 `empty → single_source → indirect_evidence`이며, 답변에는 `상황/시점 → 판단
  이유 → 행동 → 결과 → 현재 관점`을 포함한다.
- 공개 URL이 없는 기억은 직접 진술로 저장할 수 있지만, 수치·날짜는 확실한 범위만 적고
  `evidence_urls`를 비워 둔다. 이후 이력서, 회고, GitHub issue/PR로 교차 검증한다.

```bash
persona build-answers --answers data/answers/persona-answers.jsonl
persona chunk
persona audit
persona evaluate
persona knowledge-gaps
```

승격 결과는 `data/curated/persona-interview-answers.md`와 문서 레지스트리에 생성된다.
`private` 또는 빈 답변은 승격되지 않는다.

마지막 `knowledge-gaps`를 다시 실행했을 때 해당 항목이 `direct_answer`로 바뀌는지 확인한다.
추천 질문은 공백 우선순위 상위 항목에서 가져오되, 민감정보 질문과 검증되지 않은 제3자
정보는 공개 UI에 노출하지 않는다.
