import type { ReactNode } from "react";

const STRONG = /(\*\*[^*\n]+\*\*)/g;

/** Render the persona's limited Markdown without accepting arbitrary HTML. */
export function MarkdownText({ children }: { children: string }) {
  const nodes: ReactNode[] = children.split(STRONG).map((part, index) =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={index}>{part.slice(2, -2)}</strong>
      : part,
  );
  return <>{nodes}</>;
}
