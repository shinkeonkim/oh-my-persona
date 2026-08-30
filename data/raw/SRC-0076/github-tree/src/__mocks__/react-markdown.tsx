import type { ReactNode } from "react";

export type Components = Record<string, unknown>;

export default function ReactMarkdown({ children }: { children?: ReactNode }) {
  const text = typeof children === "string" ? children : "";
  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, idx) => {
        const headingMatch = /^(#{1,6})\s+(.*)$/.exec(line);
        if (headingMatch) {
          const level = headingMatch[1].length;
          const content = headingMatch[2];
          const Tag = `h${level}` as "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
          return <Tag key={idx}>{content}</Tag>;
        }
        if (line.trim() === "") return null;
        return <p key={idx}>{line}</p>;
      })}
    </>
  );
}
