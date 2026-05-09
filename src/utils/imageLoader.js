/**
 * 图片缓存工具类
 * 利用 IndexedDB 实现图片的本地持久化存储（支持非安全上下文 http）
 */

const DB_NAME = "lilac-image-db";
const STORE_NAME = "images";

// 用于存储已创建的 blob URL，避免重复创建
const blobUrlCache = new Map();

// 初始化数据库
const dbPromise = new Promise((resolve) => {
  if (!window.indexedDB) {
    console.warn("IndexedDB not supported");
    resolve(null);
    return;
  }
  const request = indexedDB.open(DB_NAME, 1);
  request.onupgradeneeded = () => {
    const db = request.result;
    if (!db.objectStoreNames.contains(STORE_NAME)) {
      db.createObjectStore(STORE_NAME);
    }
  };
  request.onsuccess = () => resolve(request.result);
  request.onerror = () => {
    console.error("IndexedDB open failed");
    resolve(null);
  };
});

const imageLoader = {
  /**
   * 获取图片的本地 URL
   */
  getCachedImage: async (url) => {
    if (!url) return "";

    // 如果已经有创建好的 blob URL，直接返回
    if (blobUrlCache.has(url)) {
      return blobUrlCache.get(url);
    }

    // 如果不是网络图片，直接返回
    if (
      !url.startsWith("http") &&
      !url.startsWith("/image") &&
      !url.startsWith("/api")
    ) {
      return url;
    }

    try {
      const db = await dbPromise;
      if (!db) return url;

      // 1. 尝试从 IndexedDB 读取
      const cachedBlob = await new Promise((resolve) => {
        const transaction = db.transaction(STORE_NAME, "readonly");
        const store = transaction.objectStore(STORE_NAME);
        const request = store.get(url);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => resolve(null);
      });

      if (cachedBlob instanceof Blob) {
        const blobUrl = URL.createObjectURL(cachedBlob);
        blobUrlCache.set(url, blobUrl);
        return blobUrl;
      }

      // 2. 缓存没有，发起请求
      const response = await fetch(url);
      if (!response.ok) throw new Error("Network response was not ok");
      const blob = await response.blob();

      // 3. 存入 IndexedDB
      const transaction = db.transaction(STORE_NAME, "readwrite");
      transaction.objectStore(STORE_NAME).put(blob, url);

      const blobUrl = URL.createObjectURL(blob);
      blobUrlCache.set(url, blobUrl);
      return blobUrl;
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
   */
  preloadImages: async (urls) => {
    const db = await dbPromise;
    if (!db) return;

    urls.forEach(async (url) => {
      try {
        // 先检查是否已存在
        const exists = await new Promise((resolve) => {
          const transaction = db.transaction(STORE_NAME, "readonly");
          const request = transaction.objectStore(STORE_NAME).get(url);
          request.onsuccess = () => resolve(!!request.result);
          request.onerror = () => resolve(false);
        });

        if (!exists) {
          const response = await fetch(url);
          if (response.ok) {
            const blob = await response.blob();
            const transaction = db.transaction(STORE_NAME, "readwrite");
            transaction.objectStore(STORE_NAME).put(blob, url);
          }
        }
      } catch (e) {
        console.error("Preload failed for:", url, e);
      }
    });
  },

  /**
   * 清除所有图片缓存
   */
  clearCache: async () => {
    // 释放所有已创建的 blob URL
    blobUrlCache.forEach((url) => URL.revokeObjectURL(url));
    blobUrlCache.clear();

    const db = await dbPromise;
    if (!db) return;
    return new Promise((resolve) => {
      const transaction = db.transaction(STORE_NAME, "readwrite");
      const request = transaction.objectStore(STORE_NAME).clear();
      request.onsuccess = () => resolve(true);
      request.onerror = () => resolve(false);
    });
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
          (originalSrc.startsWith("http") ||
            originalSrc.startsWith("/api") ||
            originalSrc.startsWith("/image"))
        ) {
          const cachedUrl = await imageLoader.getCachedImage(originalSrc);
          if (cachedUrl !== originalSrc) {
            img.src = cachedUrl;
          }
        }
      });
    },
    updated: async (el) => {
      const images = el.querySelectorAll("img");
      images.forEach(async (img) => {
        const originalSrc = img.getAttribute("src");
        if (
          originalSrc &&
          (originalSrc.startsWith("http") ||
            originalSrc.startsWith("/api") ||
            originalSrc.startsWith("/image"))
        ) {
          const cachedUrl = await imageLoader.getCachedImage(originalSrc);
          if (cachedUrl !== originalSrc) {
            img.src = cachedUrl;
          }
        }
      });
    },
  },
};

export default imageLoader;
