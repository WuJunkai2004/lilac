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
                  if (typeof url === 'string' && (url.startsWith('/api/') || url.startsWith('/image/')) && !url.startsWith('http')) {
                    return BASE + url;
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
                // 3. 拦截 <img> 标签
                const descriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
                if (descriptor) {
                  Object.defineProperty(HTMLImageElement.prototype, 'src', {
                    get: function() { return descriptor.get.call(this); },
                    set: function(value) { descriptor.set.call(this, prefixUrl(value)); }
                  });
                }
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
