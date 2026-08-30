# T02 — 안전한 자료 수집

상태: DONE
실행: T03, T05와 병렬 가능
선행: T01

## 명령

```bash
persona inspect-inbox
persona ingest-inbox --approve
```

`inspect-inbox`는 쓰지 않는 검사를 수행한다. `--approve`가 있어야 raw로 복사하며 ZIP slip, symlink, 실행 파일, 과도한 압축률, 비밀/PII 패턴을 차단한다. PDF 추출은 `ingest` extra가 설치된 경우에만 수행한다.

로컬 체크아웃은 원본을 복제하지 않고 출처 레지스트리의 `local_path`로 참조한다. 선별한 공개 문서만 inbox 승인 절차를 거쳐 snapshot으로 보존한다.
