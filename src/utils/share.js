import { toPng } from "html-to-image";

/**
 * 传入一个元素，生成其图片的 dataURL
 * @param {HTMLElement} element
 * @returns {Promise<string>}
 */
export const share = (element) => {
  if (!element) {
    return Promise.reject("Invalid element");
  }

  return toPng(element, {
    cacheBust: true,
    backgroundColor: "#ffffff",
    filter: (node) => {
      return !(node.classList && node.classList.contains("no-share"));
    },
  });
};
