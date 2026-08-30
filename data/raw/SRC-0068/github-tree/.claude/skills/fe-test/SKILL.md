---
name: fe-test
description: Jest 컴포넌트 테스트 - @testing-library/react, describe
compatibility: opencode
---

# Jest 테스트 생성

## 위치
`src/features/{feature}/ui/__tests__/{Component}.test.tsx`

## 템플릿

```tsx
import { render, screen } from "@testing-library/react";
import { Button } from "./Button";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>클릭</Button>);
    expect(screen.getByText("클릭")).toBeInTheDocument();
  });
});
```

## 체크리스트
- [ ] @testing-library/react
- [ ] describe/it 구조
- [ ] export 문