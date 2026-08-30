---
name: fe-component
description: React 컴포넌트 생성 - TypeScript, React 19, Props
compatibility: opencode
---

# React 컴포넌트 생성

## 위치
`src/features/{feature}/ui/components/{Component}.tsx`

## 템플릿

```tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ children, onClick }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}
```

## 체크리스트
- [ ] 함수 컴포넌트
- [ ] Props interface
- [ ] export 문