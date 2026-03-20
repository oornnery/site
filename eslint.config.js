import js from "@eslint/js";

export default [
    js.configs.recommended,
    {
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                window: "readonly",
                document: "readonly",
                console: "readonly",
                localStorage: "readonly",
                requestAnimationFrame: "readonly",
                addEventListener: "readonly",
                removeEventListener: "readonly",
                scrollY: "readonly",
                innerHeight: "readonly",
                location: "readonly",
                matchMedia: "readonly",
                setInterval: "readonly",
                clearInterval: "readonly",
                setTimeout: "readonly",
                clearTimeout: "readonly",
                HTMLElement: "readonly",
                MutationObserver: "readonly",
                IntersectionObserver: "readonly",
            },
        },
        rules: {
            "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
            "no-console": "warn",
        },
    },
];
