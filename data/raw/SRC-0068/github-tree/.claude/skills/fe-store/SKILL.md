---
name: fe-store
description: Zustand store - 상태 관리, create 함수
compatibility: opencode
---

# Zustand store 생성

## 위치
`src/features/{feature}/model/store.ts`

## 템플릿

```typescript
import { create } from "zustand";

interface UserStore {
  user: User | null;
  setUser: (user: User) => void;
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
```

## 체크리스트
- [ ] create 함수
- [ ] interface 정의
- [ ] export 문