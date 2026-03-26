# Frontend UI Layer

## Purpose

`src/frontend/shared/ui/` is the only primitive and composed UI boundary for the
frontend application layer.

It exists to:

- keep app/pages/features code on stable component contracts;
- stop raw HTML and local styling systems from spreading across route code;
- make migration to `ww-ui-kit` a wrapper swap instead of a page rewrite.

## Temporary Nature

The local `App*` components are intentionally temporary implementations, not a
product UI system.

Their job is to preserve stable interfaces now so that later the implementation
can point to `ww-ui-kit` with minimal change.

## Stable Surface

Current stable primitives and composed components:

- `AppContainer`
- `AppStack`
- `AppInline`
- `AppSurface`
- `AppText`
- `AppTitle`
- `AppButton`
- `AppDivider`
- `AppCard`
- `AppSection`
- `StatusBadge`
- `EmptyState`

## Usage Rules

- app/pages/features import UI only from `@/shared/ui`;
- pages remain route-level composition only;
- features remain reusable slices composed from `shared/ui`, `entities`, and `shared/api`;
- semantic props such as `variant`, `tone`, `size`, `align`, `padding`, and `radius` are preferred over local class names;
- styling lives in `shared/ui/styles/*`, not in page-level `<style>` blocks.

## Forbidden Patterns

- raw HTML tags in `pages/` and `features/` instead of `shared/ui` components;
- local `<style>` blocks in `pages/` and `features/`;
- inline `style=` and page-local utility classes as a substitute for primitive props;
- direct DOM access through `document` or `window` inside pages/features;
- cross-layer relative imports between `app`, `pages`, `features`, `entities`, and `shared`.

## Migration To `ww-ui-kit`

Safe migration path:

1. Keep `shared/ui` as the only UI surface imported by app/pages/features.
2. Preserve the local `App*` prop and slot interfaces.
3. Replace local implementations behind `shared/ui` with adapters to `ww-ui-kit`.
4. Tune tokens and semantic tones at the adapter layer, not in route code.

If migration requires editing pages or features, the local UI boundary was not
strict enough and must be corrected before adoption.
