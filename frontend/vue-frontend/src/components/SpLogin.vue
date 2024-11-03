<template>
    <div class="container">
      <form @submit.prevent="login">
        <div v-if="generalError" class="badge badge-danger">{{ generalError }}</div>
        <fieldset class="form-group">
          <legend class="border-bottom mb-4">Log In</legend>
          
          <div v-if="emailError" class="badge badge-danger">{{ emailError }}</div>
          <div class="form-group">
            <label for="email" class="form-control-label">Email</label>
            <input
              type="email"
              v-model="email"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': emailError }"
              id="email"
            />
          </div>


          <div v-if="passwordError" class="badge badge-danger">{{ passwordError }}</div>
          <div class="form-group">
            <label for="password" class="form-control-label">Password</label>
            <input
              type="password"
              v-model="password"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': passwordError }"
              id="password"
            />
            <div v-if="passwordError" class="invalid-feedback">
              <span>{{ passwordError }}</span>
            </div>
          </div>
  
          <div class="form-check">
            <input
              type="checkbox"
              v-model="remember"
              class="form-check-input"
              id="remember"
            />
            <label class="form-check-label" for="remember">Remember me</label>
          </div>
  
          <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Log In</button>
          </div>
        </fieldset>
        <small class="text-muted ml-2"><a href="#">Forgot Password?</a></small>
      </form>
      <div class="border-top pt-3">
        <small class="text-muted">
          Need an Account?
          <a class="ml-2" href="/register">Sign up</a>
        </small>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { mapState } from 'vuex';
  
  export default {
    data() {
      return {
        email: '',
        password: '',
        role: 'customer',
        remember: false,
        emailError: null,
        passwordError: null,
        generalError: null,
      };
    },
    computed: {
    ...mapState(['csrf'])
  },
    methods: {
      async login() {
        this.emailError = null;
        this.passwordError = null;
        this.generalError = null;
        try {
          const response = await axios.post('http://localhost:5001/sp-login', {
            
            email: this.email,
            password: this.password,
            role: this.role,
            remember: `${this.remember}`,
            
          },);
          
    if (response.data.success && response.data.token) {
      this.$store.commit('SET_AUTH', response.data);
      this.$router.push('/sp-dash');
    }  else {
            this.generalError = response.data.message;
          }
        } catch (error) {
          if (error.response && error.response.data) {
            if (error.message && error.message=='Request failed with status code 401') {
              this.generalError = "Invalid Credentials";
              this.clearErrorAfterDelay('generalError');
            }
           
          } else {
            this.generalError = 'An unexpected error occurred.';
            this.clearErrorAfterDelay('generalError');
          }
        }
      },
      clearErrorAfterDelay(errorType) {
        setTimeout(() => {
          this[errorType] = null;
        }, 5000); // Clear error after 5 seconds
      },
    }
  };
  </script>
  
  <style scoped>
  .container {
    margin-top: 20px;
  }
  .is-invalid {
    border-color: red;
  }
  .invalid-feedback {
    color: red;
  }
  .badge-danger {
  background-color: red;
  color: white;
  padding: 0.5em;
  border-radius: 0.25em;
  display: inline-block;
  margin: 0.5em 0;
}
  </style>
  