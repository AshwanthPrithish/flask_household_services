import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import router from './router';

Vue.use(Vuex);


axios.defaults.baseURL = 'http://localhost:5001';
axios.defaults.withCredentials = true;

export default new Vuex.Store({
  state: {
    isAuthenticated: false,
    role: null,
    email: '',
    username:'',
    token: null,
    csrf: '',
    id:''
  },
  mutations: {
    SET_AUTH(state, content) {
     state.csrf = content.csrf;
     axios.defaults.headers.common["X-CSRFToken"] = content.csrf;
      if(content.token){
        const decoded = jwtDecode(content.token);
        state.isAuthenticated = true;
        state.role = decoded.role;
      }
      else{
        state.isAuthenticated = (content.isAuthenticated == 'True') ? true : false;
        state.role = content.role;
        state.username = content.username,
        state.email=content.email,
        state.id=content.id;
      }
    },
    LOGOUT(state){
      state.isAuthenticated = false;
      state.role = null;
      state.token = null;
    }
  },
  actions: {
    async fetchAuthStatus({ commit }) {
      try {
        const response = await axios.get('/auth_status');
        commit('SET_AUTH', response.data);
      } catch (error) {
        console.error('Error fetching auth status:', error);
      }
    },
    async logout({ commit,dispatch }) {
      try {
        await dispatch('fetchAuthStatus');
        const response = await axios.post('/logout');
        if (response.data.message === "Successfully logged out") {
          commit('LOGOUT');
          if (router.currentRoute.name !== 'home') {
            router.push({ name: 'home' });
          }
        }
      } catch (error) {
        console.error('Error logging out:', error);
      }
    }
}
});
