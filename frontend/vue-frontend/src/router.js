import Vue from 'vue';
import Router from 'vue-router';
import AdminDash from './components/AdminDash.vue';
import AdminLogin from './components/AdminLogin.vue';
import AboutPage from './components/AboutPage.vue';
import Account from './components/AccountPage.vue';
import ContactPage from './components/ContactPage.vue';
import CreateService from './components/CreateService.vue';
import CustomerAccount from './components/CustomerAccount.vue';
import CustomerDash from './components/CustomerDash.vue';
import CustomerRequests from './components/CustomerRequests.vue';
import Graph from './components/GraphView.vue';
import HomePage from './components/HomePage.vue';
import Login from './components/LoginPage.vue';
import PastServices from './components/PastServices.vue';
import PendingRequests from './components/PendingRequests.vue';
import Register from './components/CustomerRegister.vue';
import SearchResultsService from './components/SearchResultsService.vue';
import SearchResultsServiceProfessional from './components/SearchResultsServiceProfessional.vue';
import ServicePage from './components/ServicePage.vue';
import ServicesPage from './components/ServicesPage.vue';
import SpDash from './components/SpDash.vue';
import SpLogin from './components/SpLogin.vue';
import SpRegister from './components/SpRegister.vue';
import SubmitRemark from './components/SubmitRemark.vue';
import UpdateService from './components/UpdateService.vue';
import ViewCustomers from './components/ViewCustomers.vue';
import ViewRemarks from './components/ViewRemarks.vue';
import ViewServiceProfessionals from './components/ViewServiceProfessionals.vue';
import ViewServiceRequests from './components/ViewServiceRequests.vue';
import store from './store';

Vue.use(Router);

const routes = [
    { path: '/', name: 'home', component: HomePage },
    { path: '/about', component: AboutPage },
    { path: '/account', component: Account },
    { path: '/admin-dash', name: 'admin-dash', meta: { requiresAdminAuth: true }, component: AdminDash },
    { path: '/admin-login', name: 'admin-login', meta: { requiresGuest: true }, component: AdminLogin },
    { path: '/contact', component: ContactPage },
    { path: '/create-service', component: CreateService,meta: { requiresAdminAuth: true } },
    { path: '/customer-account', name: 'customer-account', meta: { requiresCustomerAuth: true }, component: CustomerAccount },
    { path: '/customer-dash', name: 'customer-dash', meta: { requiresCustomerAuth: true }, component: CustomerDash },
    { path: '/customer-requests', component: CustomerRequests,meta: { requiresCustomerAuth: true } },
    { path: '/graph', component: Graph },
    { path: '/login', name: 'login', meta: { requiresGuest: true }, component: Login },
    { path: '/past-services', component: PastServices,meta: { requiresCustomerOrSPAuth: true } },
    { path: '/pending-requests', component: PendingRequests,meta: { requiresServiceProfessionalAuth: true } },
    { path: '/register', name: 'register', meta: { requiresGuest: true }, component: Register },
    { path: '/remarks', component: ViewRemarks },
    {
      path: '/search-results-service/:data',
      name: 'SearchResultsService',
      component: SearchResultsService,
      props: true
    },
    {
      path: '/search-results-service-professional/:data',
      name: 'SearchResultsServiceProfessional',
      component: SearchResultsServiceProfessional,
      props: true
    },
    {
      path: '/service/:service_id',
      name: 'ServicePage',
      component: ServicePage,
      props: true,
    },
    { path: '/services', component: ServicesPage },
    { path: '/sp-dash', component: SpDash, meta:{ requiresServiceProfessionalAuth: true } },
    { path: '/sp-login', name: 'sp-login', meta: { requiresGuest: true }, component: SpLogin },
    { path: '/sp-register', name: 'sp-register', meta: { requiresGuest: true }, component: SpRegister },
    { path: '/submit-remark', component: SubmitRemark, meta:{ requiresCustomerAuth: true } },
    {
      path: '/update-service/:service_id',
      name: 'UpdateService',
      component: UpdateService,
      props: true, meta:{ requiresAdminAuth: true }
    },
    { path: '/view-customers', component: ViewCustomers, meta:{ requiresAdminAuth: true } },
    { path: '/view-remarks', component: ViewRemarks, meta:{ requiresAdminAuth: true } },
    { path: '/view-service-professionals', component: ViewServiceProfessionals, meta:{ requiresAdminAuth: true } },
    { path: '/view-service-requests', component: ViewServiceRequests, meta:{ requiresAdminAuth: true } },
  ];
  

const router = new Router({
    mode: 'history',
    routes,
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAdminAuth)) {
    if (store.state.isAuthenticated && store.state.role === 'admin') {
        next();
    } else {
        next({ name: 'home' });
    }
  }
  else if(to.matched.some(record => record.meta.requiresCustomerAuth)){
        if (store.state.isAuthenticated && store.state.role === 'customer') {
            next();
         } else {
            next({ name: 'home' }); 
        }
  } 
  else if(to.matched.some(record => record.meta.requiresServiceProfessionalAuth)){
    if (store.state.isAuthenticated && store.state.role === 'service_professional') {
        next();
        } else {
        next({ name: 'home' }); 
        }
    } 
    else if(to.matched.some(record => record.meta.requiresCustomerOrSPAuth)){
        if (store.state.isAuthenticated && (store.state.role === 'service_professional' || store.state.role === 'service_professional')) {
             next(); 
            } else {
             next({ name: 'home' }); 
            }
        }
  else if (to.matched.some(record => record.meta.requiresGuest)) {
    if (store.state.isAuthenticated) {
      next({ name: 'home' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
