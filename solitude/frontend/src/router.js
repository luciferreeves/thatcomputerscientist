import { createRouter, createWebHistory } from 'vue-router';
import Home from './components/Home.vue';
import Page from './components/Page.vue';

// Define route components
const routes = [
  { path: '/', component: Home },
  { path: '/page', component: Page },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes, // short for `routes: routes`
});

export default router;