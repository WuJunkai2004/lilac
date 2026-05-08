import { fileURLToPath, URL } from "node:url";

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

import Components from "unplugin-vue-components/vite";
import { PrimeVueResolver } from "@primevue/auto-import-resolver";

export default defineConfig(({ mode }) => {
  let config = {
    css: {
      devSourcemap: false, // 关闭 CSS source map
    },
    plugins: [
      vue(),
      Components({
        resolvers: [PrimeVueResolver()],
      }),
      mode === "production" && {
        name: "inject-runtime-interceptor",
        transformIndexHtml(html) {
          // 注入全局运行时拦截器，处理动态获取的 API 和图片路径
          const interceptor = `
            <script>
              (function() {
                const BASE = 'http://120.26.125.50:18000';
                const prefixUrl = (url) => {
                  if (typeof url !== 'string' || url.startsWith('http') || url.startsWith('blob:') || url.startsWith('data:')) {
                    return url;
                  }
                  
                  // 更加宽松的匹配：支持 api, image, images (带或不带前导斜杠)
                  const patterns = ['/api/', 'api/', '/image/', 'image/', '/images/', 'images/'];
                  const isMatch = patterns.some(p => url.startsWith(p));
                  
                  if (isMatch) {
                    const normalizedUrl = url.startsWith('/') ? url : '/' + url;
                    const fullUrl = BASE + normalizedUrl;
                    console.log('[Interceptor] Prefixing URL:', url, '->', fullUrl);
                    return fullUrl;
                  }
                  return url;
                };

                // 1. 拦截 fetch
                const _fetch = window.fetch;
                window.fetch = function(url, options) {
                  return _fetch(prefixUrl(url), options);
                };

                // 2. 拦截 XHR
                const _open = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function() {
                  arguments[1] = prefixUrl(arguments[1]);
                  return _open.apply(this, arguments);
                };

                // 3. 拦截 <img> 标签的 src 属性
                const descriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
                if (descriptor && descriptor.configurable) {
                  Object.defineProperty(HTMLImageElement.prototype, 'src', {
                    configurable: true,
                    enumerable: true,
                    get: function() {
                      return descriptor.get ? descriptor.get.call(this) : this.getAttribute('src');
                    },
                    set: function(value) {
                      const prefixed = prefixUrl(value);
                      if (descriptor.set) {
                        descriptor.set.call(this, prefixed);
                      } else {
                        this.setAttribute('src', prefixed);
                      }
                    }
                  });
                }

                // 4. 拦截 setAttribute 作为一个备选方案
                const _setAttribute = Element.prototype.setAttribute;
                Element.prototype.setAttribute = function(name, value) {
                  if (name === 'src' && (this.tagName === 'IMG' || this.tagName === 'SOURCE')) {
                    value = prefixUrl(value);
                  }
                  return _setAttribute.call(this, name, value);
                };
              })();
            </script>
          `;
          return html.replace("</head>", `${interceptor}</head>`);
        },
      },
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        "#": fileURLToPath(new URL("./src/utils", import.meta.url)),
      },
    },
    build: {
      minify: "rolldown",
      cssMinify: true,
      sourcemap: false,
      reportCompressedSize: false,
      chunkSizeWarningLimit: 2000,
    },
    esbuild: {
      drop: ["console", "debugger"],
    },
  };
  if (mode === "debug") {
    const env = loadEnv(mode, process.cwd(), "dev_");
    if (!env.dev_backend) {
      throw new Error("请在 .env 文件中设置 dev_backend 环境变量");
    }
    config["server"] = {
      proxy: {
        "/api": {
          target: env.dev_backend,
          changeOrigin: true,
        },
        "/image": {
          target: env.dev_backend,
          changeOrigin: true,
        },
      },
    };
  }
  return config;
});
