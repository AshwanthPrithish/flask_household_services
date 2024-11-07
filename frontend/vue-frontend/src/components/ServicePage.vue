<template>
    <div>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>
      <h1>Service Details</h1>
      <div class="container">
        <div v-if="role === 'admin'">
          <button class="btn btn-secondary btn-sm m-1" @click="updateService">Update Service</button>
          <button class="btn btn-danger btn-sm m-1" @click="showDeleteModal = true">Delete Service</button>
        </div>
  
        <b>Service Name:</b> {{ service.name }}<br />
        <b>Price:</b> {{ service.price }}<br />
        <b>Description:</b> {{ service.description }}<br />
        
        <div v-if="role === 'customer'">
              <button class="btn btn-secondary btn-sm m-1" @click="requestService()">Request This Service</button>
            </div>
        <h3>Professionals in {{ service.name }} Service</h3>
        <div v-if="offeredByProfessionals.length > 0" class="container">
          <div v-for="professional in offeredByProfessionals" :key="professional.email" class="container">
            <b>Name:</b> {{ professional.name }}<br />
            <b>Email:</b> {{ professional.email }}<br />
            <b>Description:</b> {{ professional.description }}<br />
            <b>Experience:</b> {{ professional.experience }} years<br />
            <b>Date Created:</b> {{ professional.date_created }}<br />
          </div>
        </div>
      </div>
  
      <!-- Using the custom Modal component -->
      <modal :isVisible="showDeleteModal" @close="showDeleteModal = false">
        <template v-slot:header>
          <h5>Delete Service?</h5>
        </template>
        <p>Warning! Deleting the service will delete all professional details associated with it!</p>
        <template v-slot:footer>
          <button class="btn btn-secondary" @click="showDeleteModal = false">Close</button>
          <button class="btn btn-danger" @click="deleteService">Delete</button>
        </template>
      </modal>
    </div>
  </template>
  
  <script>
  import { mapState } from 'vuex';
  import axios from 'axios';
  import Modal from './ModalComponent.vue';
  
  export default {
    components: {
      Modal,
    },
    props: ['service_id'],
    data() {
      return {
        service: {},
        offeredByProfessionals: [],
        showDeleteModal: false,
        successMessage: '',
        errorMessage: ''
      };
    },
    computed: {
      ...mapState(['role']),
    },
    async mounted() {
      await this.fetchServiceDetails();
    },
    methods: {
      async fetchServiceDetails() {
        try {
          const response = await axios.get(`/service/${this.service_id}`);
          this.service = response.data.service;
          this.offeredByProfessionals = response.data.offered_by_professionals;
        } catch (error) {
          console.error('Error fetching service details:', error);
        }
      },
      updateService() {
        this.$router.push({ name: 'UpdateService', params: { serviceId: this.service.id } });
      },
      async deleteService() {
        try {
          const response = await axios.post(`/service/${this.service.id}/delete`);
          this.showDeleteModal = false;
          this.successMessage = response.data.message;
          this.$router.push({ name: 'services' });
        } catch (error) {
            if (error.response.data.message) {
            this.errorMessage = error.response.data.message;
          }
          console.error('Error deleting service:', error);
        }
      },
      requestService() {
        this.$router.push({ name: 'AddServiceRequest', params: { serviceId: this.service.id } });
      },
    },
  };
  </script>
  
  <style scoped>
  .container {
    margin-bottom: 20px;
  }
  </style>
  