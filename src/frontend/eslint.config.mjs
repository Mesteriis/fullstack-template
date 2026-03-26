import js from "@eslint/js";
import globals from "globals";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import pluginVue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";
import vueParser from "vue-eslint-parser";

const parentRelativePatterns = [
  "../*",
  "../../*",
  "../../../*",
  "../../../../*",
  "../../../../../*",
];

function restrictedImports(patterns = []) {
  return [
    "error",
    {
      patterns: [...parentRelativePatterns, ...patterns],
    },
  ];
}

export default [
  {
    ignores: ["dist/**", "coverage/**", "node_modules/**"],
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx,vue}"],
    plugins: {
      "simple-import-sort": simpleImportSort,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "no-restricted-globals": [
        "error",
        {
          name: "document",
          message: "Direct DOM access is forbidden in the frontend template layers.",
        },
        {
          name: "window",
          message: "Direct global window usage is forbidden in the frontend template layers.",
        },
      ],
      "simple-import-sort/exports": "error",
      "simple-import-sort/imports": "error",
    },
  },
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: "latest",
        sourceType: "module",
        extraFileExtensions: [".vue"],
      },
    },
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
  {
    files: ["app/**/*.{ts,tsx,vue}"],
    rules: {
      "no-restricted-imports": restrictedImports(),
    },
  },
  {
    files: ["pages/**/*.{ts,tsx,vue}"],
    rules: {
      "no-restricted-imports": restrictedImports(["@/app/*"]),
    },
  },
  {
    files: ["features/**/*.{ts,tsx,vue}"],
    rules: {
      "no-restricted-imports": restrictedImports(["@/app/*", "@/pages/*"]),
    },
  },
  {
    files: ["entities/**/*.{ts,tsx,vue}"],
    rules: {
      "no-restricted-imports": restrictedImports(["@/app/*", "@/pages/*", "@/features/*"]),
    },
  },
  {
    files: ["shared/**/*.{ts,tsx,vue}"],
    rules: {
      "no-restricted-imports": restrictedImports(["@/app/*", "@/pages/*", "@/features/*", "@/entities/*"]),
    },
  },
];
