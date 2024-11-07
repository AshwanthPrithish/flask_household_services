<template>
    <div>
      <h1>Feedback on {{ service_name }} Service from user {{ customer_name }}</h1>
      <div class="container">
        <form @submit.prevent="submitRemark">
          <fieldset class="form-group">
  
            <div class="form-group">
              <label for="remark" class="form-control-label">Remark</label>
              <textarea
                v-model="remark"
                id="remark"
                :class="['form-control', 'form-control-lg', { 'is-invalid': errors.remark }]"
              ></textarea>
              <div v-if="errors.remark" class="invalid-feedback">
                <span v-for="error in errors.remark" :key="error">{{ error }}</span>
              </div>
            </div>
  
            <div class="form-group">
              <button type="submit" class="btn btn-outline-info">Submit</button>
            </div>
          </fieldset>
        </form>
  
        <div v-if="successMessage" class="alert alert-success" role="alert">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    props: ['request_id', 'customer_name', 'service_name'],
    data() {
      return {
        remark: '',
        errors: {},
        successMessage: '',
        errorMessage: ''
      };
    },
    methods: {
      async submitRemark() {
        this.clearMessages();
  
        try {
          const response = await axios.post(`/submit-remarks/${this.request_id}`, {
            remark: this.remark
          });
  
          this.successMessage = response.data.message;
          this.remark = ''; 
        } catch (error) {
          if (error.response && error.response.status === 400) {
            this.errors = error.response.data.errors;
          } else {
            this.errorMessage = 'An error occurred while submitting your remark.';
          }
        }
      },
      clearMessages() {
        this.errors = {};
        this.successMessage = '';
        this.errorMessage = '';
      }
    }
  };
  </script>
  
  <style scoped>
  .container {
    margin-top: 20px;
  }
  .form-control.is-invalid {
    border-color: #dc3545;
  }
  .invalid-feedback {
    color: #dc3545;
  }
  </style>
  