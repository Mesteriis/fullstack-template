from __future__ import annotations

import ast
from collections import defaultdict
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = ROOT / "src" / "backend"
BACKEND_DIRS = ("api", "apps", "core", "runtime")
BACKEND_IMPORT_PREFIXES = tuple(f"{name}." for name in BACKEND_DIRS)
CONTEXT_LAYERS = {"api", "application", "contracts", "domain", "infrastructure"}
ALLOWED_SAME_CONTEXT_IMPORTS: dict[str, set[str]] = {
    "api": {"api", "application", "contracts", "domain"},
    "application": {"application", "contracts", "domain"},
    "contracts": {"contracts"},
    "domain": {"domain"},
    "infrastructure": {"application", "contracts", "domain", "infrastructure"},
}
DECLARATIVE_NODES = (ast.Assign, ast.AnnAssign, ast.Import, ast.ImportFrom, ast.Pass, ast.TypeAlias)


def module_parts_for(path: Path) -> list[str]:
    return list(path.relative_to(BACKEND_ROOT).with_suffix("").parts)


def parse_imported_modules(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.module is None:
            return []
        return [node.module]
    return []


def is_backend_import(imported: str) -> bool:
    return imported in BACKEND_DIRS or imported.startswith(BACKEND_IMPORT_PREFIXES)


def is_docstring_expr(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def is_type_checking_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"


def validate_absolute_imports(tree: ast.AST, errors: list[str], path: Path) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            errors.append(
                f"{path.relative_to(ROOT)} uses relative import at line {node.lineno}; "
                "backend modules must use absolute imports only"
            )


def allowed_reexport_scope(parts: list[str]) -> str:
    if parts and parts[0] == "apps" and len(parts) >= 2:
        return ".".join(parts[:2])
    if parts:
        return parts[0]
    return ""


def validate_illegal_reexports(parts: list[str], tree: ast.AST, errors: list[str], path: Path) -> None:
    if path.name != "__init__.py":
        return

    reexport_scope = allowed_reexport_scope(parts)
    if not reexport_scope:
        return

    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue
        imported_module = node.module
        if not is_backend_import(imported_module):
            continue
        if imported_module == reexport_scope or imported_module.startswith(f"{reexport_scope}."):
            continue
        errors.append(
            f"{path.relative_to(ROOT)} re-exports '{imported_module}' outside its allowed boundary '{reexport_scope}'. "
            "Package exports may not leak other bounded contexts or top-level domains."
        )


def validate_context_imports(parts: list[str], imported: str, errors: list[str], path: Path) -> None:
    if len(parts) < 4 or parts[0] != "apps":
        return

    context_name = parts[1]
    layer_name = parts[2]

    if layer_name not in CONTEXT_LAYERS or not imported.startswith("apps."):
        return

    imported_parts = imported.split(".")
    if len(imported_parts) < 3:
        errors.append(
            f"{path.relative_to(ROOT)} imports incomplete app module '{imported}'. "
            "Cross-context dependencies must point to explicit bounded-context modules."
        )
        return

    imported_context = imported_parts[1]
    imported_layer = imported_parts[2]

    if imported_context == context_name:
        allowed = ALLOWED_SAME_CONTEXT_IMPORTS[layer_name]
        if imported_layer not in allowed:
            errors.append(
                f"{path.relative_to(ROOT)} violates same-context layer rule: "
                f"{layer_name} -> {imported_layer} via '{imported}'"
            )
        return

    if imported_layer != "contracts":
        errors.append(
            f"{path.relative_to(ROOT)} imports internal module of another context via '{imported}'. "
            "Only contracts may cross bounded-context boundaries."
        )


def validate_domain_rules(tree: ast.AST, errors: list[str], path: Path) -> None:
    for node in ast.walk(tree):
        for imported in parse_imported_modules(node):
            if imported in {"api", "application", "infrastructure"} or imported.startswith(
                ("api.", "application.", "infrastructure.")
            ):
                errors.append(
                    f"{path.relative_to(ROOT)} domain layer must not depend on transport or adapter modules via '{imported}'"
                )
            if imported.startswith("apps."):
                imported_parts = imported.split(".")
                if len(imported_parts) >= 3 and imported_parts[2] in {"api", "application", "infrastructure"}:
                    errors.append(
                        f"{path.relative_to(ROOT)} domain layer must not depend on {imported_parts[2]} via '{imported}'"
                    )


def validate_contract_block(
    nodes: list[ast.stmt],
    *,
    path: Path,
    errors: list[str],
    owner_name: str | None = None,
) -> None:
    for node in nodes:
        if is_docstring_expr(node) or isinstance(node, DECLARATIVE_NODES):
            continue

        if is_type_checking_guard(node):
            validate_contract_block(node.body, path=path, errors=errors, owner_name=owner_name)
            for else_node in node.orelse:
                errors.append(
                    f"{path.relative_to(ROOT)} contracts layer may not execute runtime logic in TYPE_CHECKING fallback blocks; "
                    f"found {else_node.__class__.__name__}"
                )
            continue

        if isinstance(node, ast.ClassDef):
            validate_contract_block(node.body, path=path, errors=errors, owner_name=node.name)
            continue

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            target = f"class '{owner_name}'" if owner_name is not None else "module scope"
            errors.append(
                f"{path.relative_to(ROOT)} contracts layer may not define executable methods or functions in {target}; "
                f"found {node.__class__.__name__} '{node.name}'"
            )
            continue

        target = f"class '{owner_name}'" if owner_name is not None else "module scope"
        errors.append(
            f"{path.relative_to(ROOT)} contracts layer may only contain declarative boundary objects in {target}; "
            f"found {node.__class__.__name__}"
        )


def validate_contract_rules(tree: ast.AST, errors: list[str], path: Path) -> None:
    validate_contract_block(list(tree.body), path=path, errors=errors)


def validate_domain_and_contract_rules(parts: list[str], tree: ast.AST, errors: list[str], path: Path) -> None:
    if len(parts) < 4 or parts[0] != "apps":
        return

    layer_name = parts[2]
    if layer_name == "domain":
        validate_domain_rules(tree, errors, path)
    if layer_name == "contracts" and path.name != "__init__.py":
        validate_contract_rules(tree, errors, path)


def validate_core_imports(parts: list[str], imported: str, errors: list[str], path: Path) -> None:
    if len(parts) < 2 or parts[0] != "core":
        return

    is_bootstrap = len(parts) >= 2 and parts[1] == "bootstrap"
    if is_bootstrap:
        return

    if imported == "api" or imported == "runtime" or imported == "apps":
        errors.append(
            f"{path.relative_to(ROOT)} uses forbidden dependency from core module via '{imported}'"
        )
        return

    if imported.startswith(("api.", "runtime.", "apps.")):
        errors.append(
            f"{path.relative_to(ROOT)} uses forbidden dependency from core module via '{imported}'"
        )


def validate_runtime_imports(parts: list[str], imported: str, errors: list[str], path: Path) -> None:
    if len(parts) < 2 or parts[0] != "runtime":
        return

    if imported == "api" or imported.startswith("api."):
        errors.append(f"{path.relative_to(ROOT)} must not import API layer via '{imported}'")


def collect_context_dependencies(parts: list[str], tree: ast.AST, context_graph: dict[str, set[str]]) -> None:
    if len(parts) < 4 or parts[0] != "apps":
        return

    current_context = f"apps.{parts[1]}"
    for node in ast.walk(tree):
        for imported in parse_imported_modules(node):
            if not imported.startswith("apps."):
                continue
            imported_parts = imported.split(".")
            if len(imported_parts) < 3:
                continue
            imported_context = f"apps.{imported_parts[1]}"
            if imported_context != current_context:
                context_graph[current_context].add(imported_context)


def validate_context_cycles(context_graph: dict[str, set[str]], errors: list[str]) -> None:
    visited: set[str] = set()
    stack: list[str] = []
    active: set[str] = set()

    def dfs(node: str) -> None:
        visited.add(node)
        active.add(node)
        stack.append(node)

        for dependency in sorted(context_graph[node]):
            if dependency not in visited:
                dfs(dependency)
                continue
            if dependency in active:
                cycle = stack[stack.index(dependency) :] + [dependency]
                errors.append("basic cross-context cycle detected: " + " -> ".join(cycle))

        active.remove(node)
        stack.pop()

    for context_name in sorted(context_graph):
        if context_name not in visited:
            dfs(context_name)


def validate_file(path: Path, context_graph: dict[str, set[str]], errors: list[str]) -> None:
    parts = module_parts_for(path)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    validate_absolute_imports(tree, errors, path)
    validate_illegal_reexports(parts, tree, errors, path)
    validate_domain_and_contract_rules(parts, tree, errors, path)
    collect_context_dependencies(parts, tree, context_graph)

    for node in ast.walk(tree):
        for imported in parse_imported_modules(node):
            if not is_backend_import(imported):
                continue
            validate_context_imports(parts, imported, errors, path)
            validate_core_imports(parts, imported, errors, path)
            validate_runtime_imports(parts, imported, errors, path)


def main() -> int:
    errors: list[str] = []
    context_graph: dict[str, set[str]] = defaultdict(set)

    for backend_dir in BACKEND_DIRS:
        for path in sorted((BACKEND_ROOT / backend_dir).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            validate_file(path, context_graph, errors)

    main_path = BACKEND_ROOT / "main.py"
    if main_path.is_file():
        validate_file(main_path, context_graph, errors)

    validate_context_cycles(context_graph, errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Backend architecture validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
