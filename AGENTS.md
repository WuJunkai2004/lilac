# lilac echoes

AI psychological healing & generative public art mobile app. Vue 3 + PrimeVue (Fuchsia/Aura theme) + PrimeFlex + Vite 8 + Capacitor 8 (Android). Node `^20.19.0 || >=22.12.0` required.

## Commands

- `npm run dev` — dev server with HMR (no backend proxy)
- `npm run debug` — dev server with backend proxy (requires `dev_backend` in `.env`)
- `npm run build` — production build (Vite + rolldown minifier, drops console/debugger)
- `npm run preview` — preview production build on port 5400
- `node script/gen_docs.js` — fetch backend OpenAPI spec and generate `api.md` (also requires `dev_backend` in `.env`)

No lint, typecheck, or test commands are configured.

## Path Aliases

- `@` → `src/`
- `#` → `src/utils/`
- `~` → `src/animations/`

## Fetch Convention

Always chain `resCheck` then `authCheck` from `#/check`. Do NOT use axios.

```js
import { resCheck, authCheck } from '#/check';
fetch(url, options)
  .then(resCheck)   // throws on non-200 HTTP status, parses JSON
  .then(authCheck)  // checks JSON body { code: 401 } → redirects to /login
  .then(data => { /* ... */ })
  .catch(error => { /* ... */ });
```

Note: `authCheck` inspects the **JSON response body** `code` field, not the HTTP status code.

## Auth Token Pattern

Token is stored via Capacitor Preferences through `#/storage`:

```js
import storage from '#/storage';
const token = await storage.get('token');        // read
await storage.set('token', token, 7 * 24);       // write (7 days TTL, hours unit)
```

Pass in fetch headers as `Authorization: Bearer ${token}`. User info and avatar are also in storage (keys `"user"`, `"avatar"`, TTL `0` = never expires).

## PrimeVue

Components are auto-imported via `unplugin-vue-components` + `PrimeVueResolver` (no manual imports needed). Prefer PrimeVue components and PrimeFlex classes for UI consistency. `ConfirmationService` and `ToastService` are registered globally. Theme uses a Fuchsia preset built on Aura.

## Images

Use `<CachedImage>` from `@/components/CachedImage.vue` instead of raw `<img>`. It handles caching via **IndexedDB** (`lilac-image-db`) and provides loading/error states.

For HTML content containing `<img>` tags (e.g. markdown-rendered AI responses), use the `v-cached-images` directive (registered globally in `main.js`) on the container element — it automatically caches all child images via the same IndexedDB store.

## Animations (`~/`)

Animations use **Three.js** (orthographic camera + WebGL renderer for 2D effects). Architecture:

- `~/core/SceneManager.js` — creates Three.js scene/camera/renderer, manages effect lifecycle and render loop
- `~/core/Effect.js` — abstract base class with `init()`, `update(time, dimensions)`, `onResize()`, `dispose()` lifecycle hooks
- `~/effects/` — concrete effects (e.g. `CloudEffect`, `DandelionEffect`, `ThunderCloudEffect`) extending `Effect`

Usage: instantiate `SceneManager` with a `<canvas>`, call `addEffect(name, EffectClass, config)`, then `start()`. Call `dispose()` on unmount to release WebGL resources.

## Key Utilities (`#/`)

- `#/storage` — Capacitor Preferences wrapper with expiry support (`set(key, value, hours)`, `get`, `remove`, `clear`)
- `#/alert` — `useAlert()` composable: `shows()` for toasts, `alerts()` for confirm dialogs, `awaitAlert()` for async confirm that returns boolean
- `#/markdown` — `markdown(text)` renders markdown via markdown-it + DOMPurify sanitization
- `#/mood` — `moodTypes` array with color/icon/quote per mood; helpers: `getMoodColor`, `getMoodIcon`, `getMoodQuote`
- `#/debounce` — simple debounce function
- `#/imageLoader` — IndexedDB image cache (`getCachedImage`, `preloadImages`, `clearCache`); also provides the `v-cached-images` directive

## SFC Order

Use `<script>` → `<template>` → `<style>` in single-file components.

## Production Build Quirk

In production mode, Vite injects a runtime interceptor into `index.html` that monkey-patches `fetch`, `XMLHttpRequest.open`, `HTMLImageElement.src`, and `Element.setAttribute` to prefix all `api/`, `image/`, `images/` URLs with a **hardcoded backend base URL** (set in `vite.config.js`). Relative API/image paths work in production without explicit base URL. To change the backend target, edit the `BASE` constant in `vite.config.js`.

## Android / Capacitor

- `capacitor.config.json`: appId `com.lilac.echoes`, webDir `dist`, hostname `lilac.app`, scheme `http`
- Android build flow: `npm run build` → `npx cap sync android` → `cd android && ./gradlew assembleRelease`
- CI (`.github/workflows/android.yml`) uses Node 24 + JDK 21, triggers on `VERSION.txt` changes, produces signed APK + AAB + debug APK as GitHub Release
- Version is read from `VERSION.txt`; `__APP_VERSION__` global appends git short hash

## Backend

Backend is a separate Python service. API paths are `/api/...`, image paths are `/image/...` or `/images/...`. The `.env` file (gitignored) must define `dev_backend` for both `npm run debug` proxy mode and `node script/gen_docs.js`.
