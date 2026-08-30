---
name: fe-api
description: 프론트엔드 API 함수 - fetch, axios, 타입 정의
compatibility: opencode
---

# API 함수 생성

## 위치
`src/features/{feature}/api/{name}Api.ts`

## 템플릿

```typescript
export async function getUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}
```

## 체크리스트
- [ ] async/await
- [ ] 타입 정의
- [ ] export 문

## 응답 케이스 유의사항
- API 응답은 middleware를 통해 camelCase로 변환되어 반환됨
- 프론트 타입/필드는 camelCase 기준으로 정의 (예: canClaimReward, rewardClaimedAt)
- 백엔드 serializer가 snake_case여도 프론트는 camelCase를 사용
