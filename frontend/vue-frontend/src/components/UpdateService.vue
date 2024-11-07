<template>
    <div class="container">
      <form @submit.prevent="submitForm">
        <fieldset class="form-group">
          <legend class="border-bottom mb-4">{{ legend }}</legend>
  
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>
  
          <div class="form-group">
            <label for="name" class="form-control-label">Name</label>
            <input
              v-model="form.name"
              type="text"
              id="name"
              :class="['form-control', 'form-control-lg', { 'is-invalid': errors.name }]"
            />
            <div v-if="errors.name" class="invalid-feedback">
              <span v-for="error in errors.name" :key="error">{{ error }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <label for="price" class="form-control-label">Price</label>
            <input
              v-model="form.price"
              type="number"
              id="price"
              :class="['form-control', 'form-control-lg', { 'is-invalid': errors.price }]"
            />
            <div v-if="errors.price" class="invalid-feedback">
              <span v-for="error in errors.price" :key="error">{{ error }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <label for="description" class="form-control-label">Description</label>
            <textarea
              v-model="form.description"
              id="description"
              :class="['form-control', 'form-control-lg', { 'is-invalid': errors.description }]"
              rows="4"
            ></textarea>
            <div v-if="errors.description" class="invalid-feedback">
              <span v-for="error in errors.description" :key="error">{{ error }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Update Service</button>
          </div>
        </fieldset>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        legend: 'Update Service',
        form: {
          name: '',
          price: '',
          description: '',
        },
        errors: {},
        errorMessage: '',
        successMessage: '',
      };
    },
    created() {
      this.fetchServiceDetails();
    },
    methods: {
      async fetchServiceDetails() {
        try {
          const { data } = await axios.get(`/service/${this.$route.params.service_id}`);
          this.form = data.service;
        } catch (error) {
          this.errorMessage = 'Failed to load service details.';
        }
      },
      async submitForm() {
        try {
          this.errors = {};
          const response = await axios.post(`/service/${this.$route.params.service_id}/update`, this.form);
          this.successMessage = response.data.message;
        } catch (error) {
          if (error.response && error.response.data.errors) {
            this.errors = error.response.data.errors;
          }
          if (error.response && error.response.data.message) {
            this.errorMessage = error.response.data.message;
          }
        }
      },
    },
  };
  </script>
  
  <style>
  .container {
    max-width: 600px;
  }
  </style>
  