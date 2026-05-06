import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";

const md = new MarkdownIt({
  html: false, // 禁用原始 HTML 以增强安全
  linkify: true, // 自动识别链接
  breaks: true, // 将换行符转为 <br>
});

export function markdown(text) {
  if (!text) {
    return "";
  }
  const html = md.render(text);
  return DOMPurify.sanitize(html);
}
