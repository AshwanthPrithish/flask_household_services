import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';

import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import 'bootstrap'; // 

Vue.config.productionTip = false;

store.dispatch('fetchAuthStatus').then(() => {
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app');
}).catch(() => {
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app');
});