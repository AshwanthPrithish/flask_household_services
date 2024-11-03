<template>
    <div class="container">
      <form @submit.prevent="submitForm">
        <fieldset class="form-group">
          <legend class="border-bottom mb-4">Join Today</legend>
  
          <!-- Error Alert -->
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
  
          <div class="form-group">
            <label for="username" class="form-control-label">Username</label>
            <input
              type="text"
              v-model="username"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': errors.username && errors.username.length }"
              id="username"
            />
            <div v-if="errors.username && errors.username.length" class="invalid-feedback">
            <span v-for="(error, index) in errors.username" :key="index">{{ error }}</span>
            </div>

          </div>
  
          <div class="form-group">
            <label for="email" class="form-control-label">Email</label>
            <input
              type="email"
              v-model="email"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': errors.email && errors.email.length }"
              id="email"
            />
            <div v-if="errors.email && errors.email.length" class="invalid-feedback">
              <span v-for="error in errors.email" :key="error">{{ error }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="description" class="form-control-label">Description</label>
            <textarea
                v-model="description"
                class="form-control form-control-lg"
                :class="{ 'is-invalid': errors.description && errors.description.length }"
                id="description"
                rows="4" 
            ></textarea>
            <div v-if="errors.description && errors.description.length" class="invalid-feedback">
                <span v-for="error in errors.description" :key="error">{{ error }}</span>
            </div>
            </div>


          <div class="form-group">
            <label for="experience" class="form-control-label">Experience</label>
            <input
              type="text"
              v-model="experience"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': errors.experience && errors.experience.length }"
              id="contact"
            />
            <div v-if="errors.experience && errors.experience.length" class="invalid-feedback">
              <span v-for="error in errors.experience" :key="error">{{ error }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="services" class="form-control-label">Services</label>
            <select
                v-model="selectedService"
                class="form-control form-control-lg"
                :class="{ 'is-invalid': errors.services && errors.services.length }"
                id="services"
            >
                <option value="" disabled>Select a service</option>
                <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
                </option>
            </select>
            <div v-if="errors.services && errors.services.length" class="invalid-feedback">
                <span v-for="error in errors.services" :key="error">{{ error }}</span>
            </div>
            </div>
  
          <div class="form-group">
            <label for="password" class="form-control-label">Password</label>
            <input
              type="password"
              v-model="password"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': errors.password && errors.password.length }"
              id="password"
            />
            <div v-if="errors.password && errors.password.length" class="invalid-feedback">
              <span v-for="error in errors.password" :key="error">{{ error }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <label for="confirm_password" class="form-control-label">Confirm Password</label>
            <input
              type="password"
              v-model="confirmPassword"
              class="form-control form-control-lg"
              :class="{ 'is-invalid': errors.confirm_password && errors.confirm_password.length }"
              id="confirm_password"
            />
            <div v-if="errors.confirm_password && errors.confirm_password.length" class="invalid-feedback">
              <span v-for="error in errors.confirm_password" :key="error">{{ error }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Register</button>
          </div>
        </fieldset>
      </form>
  
      <div class="border-top pt-3">
        <small class="text-muted">Already Have an Account? <router-link to="/sp-login">Sign In</router-link></small>
      </div>
    </div>
  </template>
  
  <script>
  import { mapState } from 'vuex';
  import axios from 'axios';
  export default {
    data() {
      return {
        username: '',
        email: '',
        password: '',
        description: '',
        experience: '',
        confirmPassword: '',
        selectedService: '',
        services: [],
        errors: {
          username: [],
          email: [],
          contact: [],
          address: [],
          password: [],
          confirm_password: [],
          services: [],
        },
        errorMessage: '' 
      };
    },
    computed: {
    ...mapState(['csrf'])
  },
    methods: {
        async fetchServices() {
          const response = await axios.get('http://localhost:5001/fetch-services');
          this.services = response.data;
        },
      async submitForm() {
        this.errors = { username: [], email: [], password: [], confirmPassword: [],address: [], contact: []};
        this.errorMessage = ''; 
        try {
          await axios.post('http://localhost:5001/sp-register', {
            username: this.username,
            email: this.email,
            password: this.password,
            description: this.description,
            experience: this.experience,
            service: this.selectedService+'',
            confirm_password: this.confirmPassword,
            csrf_token: this.csrf
          });
          this.$router.push({ name: 'sp-login' });
        } catch (error) {
          if (error.response && error.response.data.errors) {
            this.errors = error.response.data.errors;
          }
          if (error.response && error.response.data.message) {
            this.errorMessage = error.response.data.message;
          }
        }
      }
    },
    mounted() {
        this.fetchServices();
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
    display: block;
  }
  .alert {
    margin-top: 20px;
  }
  </style>
  