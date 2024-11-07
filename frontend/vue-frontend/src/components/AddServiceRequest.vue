<template>
    <div class="container">
      <form @submit.prevent="submitRequest">
        <fieldset class="form-group">
          <legend class="border-bottom mb-4">Request this Service</legend>
  
          <div class="form-group">
            <label for="date_of_request" class="form-control-label">Date of Request</label>
            <input
              type="date"
              id="date_of_request"
              v-model="form.date_of_request"
              :class="['form-control', 'form-control-lg', errors.date_of_request ? 'is-invalid' : '']"
            />
            <div v-if="errors.date_of_request" class="invalid-feedback">
              <span>{{ errors.date_of_request }}</span>
            </div>
          </div>
  
          <div class="form-group">
            <label for="request_duration" class="form-control-label">Request Duration</label>
            <input
              type="text"
              id="request_duration"
              v-model="form.request_duration"
              :class="['form-control', 'form-control-lg', errors.request_duration ? 'is-invalid' : '']"
            />
            <div v-if="errors.request_duration" class="invalid-feedback">
              <span>{{ errors.request_duration }}</span>
            </div>
          </div>
  
          <button type="submit" class="btn btn-outline-info">Submit</button>
        </fieldset>
        
        <div v-if="flashMessage" :class="`alert alert-${flashType}`" role="alert">
          {{ flashMessage }}
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    props: ['service_id'],
    data() {
      return {
        form: {
          date_of_request: '',
          request_duration: ''
        },
        errors: {},
        flashMessage: '',
        flashType: ''
      };
    },
    methods: {
        async submitRequest() {
            if (this.form.date_of_request) {
            const date = new Date(this.form.date_of_request);
            const formattedDate = `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;

            const requestData = {
                date_of_request: formattedDate,
                request_duration: this.form.request_duration,
            };

            try {
                const response = await axios.post(`/service/${this.service_id}/request_service`, requestData);
                this.flashMessage = response.data.message;
                this.formErrors = {}; 
            } catch (error) {
                if (error.response && error.response.data.errors) {
                this.formErrors = error.response.data.errors;
                } else if (error.response && error.response.data.flash) {
                this.flashMessage = error.response.data.flash;
                } else {
                console.error('Error submitting form:', error);
                }
            }
            }
        },
        }

  };
  
  </script>
  
  <style scoped>
  .container {
    margin-bottom: 20px;
  }
  </style>
  