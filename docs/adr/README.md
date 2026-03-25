# ADR

Каталог ADR разделён на три независимые категории:

- [architecture/](./architecture/README.md) - архитектурные решения и инженерные принципы, которые не должны зависеть от названия продукта.
- [product/](./product/README.md) - доменные и продуктовые решения, которые описывают модель предметной области, жизненные циклы и правила платформы.
- [engineering/](./engineering/README.md) - template-level и repository-governance решения, которые описывают self-validation, metadata, CI symmetry и инженерный baseline.

Перед изменением кода, CI, контрактов, runtime topology или самих ADR сначала нужно прочитать [INDEX.md](./INDEX.md). Этот файл является обязательной картой чтения для людей и ИИ-агентов.

## Принципы оформления

- один ADR = одно решение;
- ADR фиксирует решение, а не бэкграунд обсуждения;
- если решение меняется, создаётся новый ADR, а старый получает связь через `Supersedes` или `Superseded by`;
- language-specific coding conventions не должны автоматически становиться ADR, если это не архитектурное решение.

## Нумерация

- `0000-0999` - architecture ADR;
- `1000-1999` - product ADR;
- `2000-2999` - engineering ADR.

## Статусы

- `Proposed`
- `Accepted`
- `Rejected`
- `Deprecated`
- `Superseded`

## Шаблон

Каждый ADR использует единый формат:

- `Status`
- `Date`
- `Deciders`
- `Supersedes`
- `Superseded by`
- `Context`
- `Decision`
- `Consequences`
- `Alternatives considered`
- `Follow-up work`

## Правило нейтральности

Архитектурные ADR должны быть написаны без привязки к бренду, имени продукта или текущему маркетинговому позиционированию. Формулировки должны описывать архитектурные принципы, ограничения, роли компонентов и эксплуатационные требования.
