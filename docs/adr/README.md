# ADR

В этом каталоге хранятся архитектурные решения проекта.

Формат ADR:
- статус решения;
- дата принятия;
- контекст;
- решение;
- последствия.

Новые ADR добавляются следующим порядковым номером и не переписывают историю уже принятых решений. Если решение меняется, создаётся новый ADR, который явно заменяет или уточняет старый.

Текущий набор решений:
- [0001-monorepo-structure.md](./0001-monorepo-structure.md) - целевая структура монорепозитория и правила размещения кода.
- [0002-spec-first-development.md](./0002-spec-first-development.md) - спецификация как источник истины для API и сообщений.
- [0003-python-backend-practices.md](./0003-python-backend-practices.md) - правила для Python/FastAPI backend.
- [0004-vue3-typescript-frontend-practices.md](./0004-vue3-typescript-frontend-practices.md) - правила для Vue 3 + TypeScript frontend.
