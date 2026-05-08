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
    ],
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
      rollupOptions: {
        plugins: [
          {
            name: "replace-api-url",
            transform(code) {
              // 在打包阶段将代码中的相对路径替换为绝对地址，实现零代码改动穿透
              let updatedCode = code.replace(
                /(['"])\/api\//g,
                "$1http://120.26.125.50:18000/api/"
              );
              updatedCode = updatedCode.replace(
                /(['"])\/image\//g,
                "$1http://120.26.125.50:18000/image/"
              );
              return {
                code: updatedCode,
                map: null,
              };
            },
          },
        ],
      },
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
