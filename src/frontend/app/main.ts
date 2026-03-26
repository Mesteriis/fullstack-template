import "@/shared/ui/styles/index.css";

import { createApp } from "vue";

import App from "@/app/App.vue";
import { createAppRouter } from "@/app/router";
import { appConfig } from "@/shared/config/env";
import { setupFrontendObservability } from "@/shared/observability";

const app = createApp(App);
const router = createAppRouter();

setupFrontendObservability(app, router, appConfig);
app.use(router);
app.mount("#app");
