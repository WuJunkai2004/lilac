# lilac echoes

AI psychological healing & generative public art mobile app. Vue 3 + PrimeVue + PrimeFlex + Vite + Capacitor (Android).

## Commands

- `npm run dev` — dev server with HMR (no backend proxy)
- `npm run debug` — dev server with backend proxy (requires `dev_backend` in `.env`)
- `npm run build` — production build (Vite + rolldown, drops console/debugger)
- `npm run preview` — preview production build on port 5400
- `node script/gen_docs.js` — fetch backend OpenAPI spec and generate `api.md`

No lint, typecheck, or test commands are configured.

## Path Aliases

- `@` → `src/`
- `#` → `src/utils/`

## Fetch Convention

Always chain `resCheck` then `authCheck` from `#/check`. Do NOT use axios.

```js
import { resCheck, authCheck } from '#/check';
fetch(url, options)
  .then(resCheck)   // parses JSON, throws on non-200
  .then(authCheck)  // redirects to /login on 401
  .then(data => { /* ... */ })
  .catch(error => { /* ... */ });
```

## Auth Token Pattern

Token is stored via Capacitor Preferences through `#/storage`:

```js
import storage from '#/storage';
const token = await storage.get('token');        // read
await storage.set('token', token, 7 * 24);       // write (7 days TTL)
```

Pass in fetch headers as `Authorization: Bearer ${token}`. User info and avatar are also in storage (keys `"user"`, `"avatar"`, TTL 0 = never expires).

## PrimeVue

Components are auto-imported (no manual imports needed). Prefer PrimeVue components and PrimeFlex classes for UI consistency. `ConfirmationService` and `ToastService` are registered globally.

## Images

Use `<CachedImage>` from `@/components/CachedImage.vue` instead of raw `<img>`. It handles caching via Cache API and provides loading/error states.

For HTML content containing `<img>` tags (e.g. markdown-rendered AI responses), use the `v-cached-images` directive (registered globally in `main.js`) on the container element — it automatically caches all child images.

## Key Utilities (`#/`)

- `#/storage` — Capacitor Preferences wrapper with expiry support (`set(key, value, hours)`, `get`, `remove`, `clear`)
- `#/alert` — `useAlert()` composable: `shows()` for toasts, `alerts()` for confirm dialogs, `awaitAlert()` for async confirm that returns boolean
- `#/markdown` — `markdown(text)` renders markdown via markdown-it + DOMPurify sanitization
- `#/mood` — `moodTypes` array with color/icon/quote per mood; helpers: `getMoodColor`, `getMoodIcon`, `getMoodQuote`
- `#/debounce` — simple debounce function
- `#/imageLoader` — low-level Cache API image cache; also exposes `preloadImages(urls)` and `clearCache()`

## SFC Order

Use `<script>` → `<template>` → `<style>` in single-file components.

## Production Build Quirk

In production mode, Vite injects a runtime interceptor into `index.html` that prefixes all `api/`, `image/`, `images/` URLs with a hardcoded backend base URL. Relative API/image paths work in production without explicit base URL.

## Android / Capacitor

- `capacitor.config.json`: appId `com.lilac.echoes`, webDir `dist`
- Android build flow: `npm run build` → `npx cap sync android` → `./gradlew assembleRelease`
- CI (`.github/workflows/android.yml`) triggers on `VERSION.txt` changes
- Version is read from `VERSION.txt`; `__APP_VERSION__` global includes git short hash

## Backend

Backend is a separate Python service. API paths are `/api/...`, image paths are `/image/...` or `/images/...`. The `.env` file (gitignored) must define `dev_backend` for debug proxy mode.
