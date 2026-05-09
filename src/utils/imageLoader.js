/**
 * 图片缓存工具类
 * 利用 Cache API 实现图片的本地持久化存储
 */

const CACHE_NAME = "lilac-image-cache-v1";

const imageLoader = {
  /**
   * 获取图片的本地 URL
   * 如果缓存中存在，则返回缓存的 URL
   * 如果缓存中不存在，则下载图片并存入缓存，然后返回 URL
   * @param {string} url 原始网络图片 URL
   * @returns {Promise<string>} 本地可用的图片 URL (Blob URL 或 原始 URL)
   */
  getCachedImage: async (url) => {
    if (!url) return "";

    // 如果不是网络图片，直接返回
    if (!url.startsWith("http") && !url.startsWith("/image")) {
      return url;
    }

    try {
      const cache = await caches.open(CACHE_NAME);
      const cachedResponse = await cache.match(url);

      if (cachedResponse) {
        // 从缓存中读取
        const blob = await cachedResponse.blob();
        return URL.createObjectURL(blob);
      }

      // 缓存中没有，发起请求
      const response = await fetch(url);
      if (!response.ok) throw new Error("Network response was not ok");

      // 将响应存入缓存 (注意：我们需要克隆响应，因为 response.blob() 会消费掉它)
      await cache.put(url, response.clone());

      const blob = await response.blob();
      return URL.createObjectURL(blob);
    } catch (error) {
      console.warn(
        "Image caching failed, falling back to original URL:",
        error,
      );
      return url;
    }
  },

  /**
   * 预加载图片
   * @param {string[]} urls
   */
  preloadImages: async (urls) => {
    const cache = await caches.open(CACHE_NAME);
    const promises = urls.map(async (url) => {
      try {
        const cachedResponse = await cache.match(url);
        if (!cachedResponse) {
          const response = await fetch(url);
          if (response.ok) {
            await cache.put(url, response);
          }
        }
      } catch (e) {
        console.error("Preload failed for:", url, e);
      }
    });
    await Promise.all(promises);
  },

  /**
   * 清除所有图片缓存
   */
  clearCache: async () => {
    return await caches.delete(CACHE_NAME);
  },

  /**
   * Vue 指令：自动缓存并替换元素下的所有图片
   */
  directive: {
    mounted: async (el) => {
      const images = el.querySelectorAll("img");
      images.forEach(async (img) => {
        const originalSrc = img.src;
        if (
          originalSrc &&
          (originalSrc.startsWith("http") || originalSrc.startsWith("/api"))
        ) {
          try {
            const cachedUrl = await imageLoader.getCachedImage(originalSrc);
            if (cachedUrl !== originalSrc) {
              img.src = cachedUrl;
            }
          } catch (e) {
            console.error("Directive cache failed:", e);
          }
        }
      });
    },
    updated: async (el) => {
      // 当内容更新时再次检查
      const images = el.querySelectorAll("img");
      images.forEach(async (img) => {
        const originalSrc = img.getAttribute("src");
        // 如果已经是 blob: 或者是 data:，说明已经处理过或不需要处理
        if (
          originalSrc &&
          (originalSrc.startsWith("http") || originalSrc.startsWith("/api"))
        ) {
          try {
            const cachedUrl = await imageLoader.getCachedImage(originalSrc);
            if (cachedUrl !== originalSrc) {
              img.src = cachedUrl;
            }
          } catch (e) {
            console.error("Directive cache failed:", e);
          }
        }
      });
    },
  },
};

export default imageLoader;
