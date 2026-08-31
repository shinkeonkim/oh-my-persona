import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { MarkdownText } from "./MarkdownText";

describe("MarkdownText", () => {
  it("renders emphasis and escapes arbitrary html", () => {
    const html = renderToStaticMarkup(
      <MarkdownText>{"**중요한 내용**과 <script>alert(1)</script>"}</MarkdownText>,
    );
    expect(html).toContain("<strong>중요한 내용</strong>");
    expect(html).toContain("&lt;script&gt;");
    expect(html).not.toContain("<script>");
  });
});
