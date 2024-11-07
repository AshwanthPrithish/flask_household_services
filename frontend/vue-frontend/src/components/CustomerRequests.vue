<!-- CustomerRequests.vue -->
<template>
    <div>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>
      <h1>My Requests</h1>
      <div v-for="request in requests" :key="request.request_id" class="container">
        <div v-if="request.service_status === 'assigned'">
          <button 
            type="button" 
            class="btn btn-secondary btn-sm m-1" 
            @click="openModal(request.request_id, 'complete')">
            Mark Request as Complete
          </button>
        </div>
        <div v-else-if="request.service_status === 'requested'">
          <button 
            type="button" 
            class="btn btn-secondary btn-sm m-1" 
            @click="openModal(request.request_id, 'cancel')">
            Cancel Service Request
          </button>
        </div>
        <div>
          <b>Service Name:</b> {{ request.service_name }}<br />
          <b>Customer Name:</b> {{ request.customer_name }}<br />
          <div v-if="request.service_professional_name"><b>Service Professional Name:</b> {{ request.service_professional_name }}<br /></div>
          <b>Service Status:</b> {{ request.service_status }}<br />
          <b>Date of Request:</b> {{ request.date_of_request }}<br />
          <b>Date of Completion:</b> {{ request.date_of_completion }}<br /><br />
        </div>
      </div>
  
      <Modal :isVisible="showCompleteModal" @close="showCompleteModal = false">
        <template v-slot:header>
          <h5>Mark Request As Complete?</h5>
        </template>
        <p>Mark Request As Complete <b>({{ selectedRequest.service_name }})</b></p>
        <template v-slot:footer>
          <button class="btn btn-secondary" @click="showCompleteModal = false">Close</button>
          <button class="btn btn-danger" @click="markAsComplete(selectedRequest.request_id, selectedRequest.customer_name, selectedRequest.service_name)">Proceed</button>
        </template>
      </Modal>
  
      <Modal :isVisible="showCancelModal" @close="showCancelModal = false">
        <template v-slot:header>
          <h5>Cancel Request?</h5>
        </template>
        <p>Cancel Request <b>({{ selectedRequest.service_name }})</b></p>
        <template v-slot:footer>
          <button class="btn btn-secondary" @click="showCancelModal = false">Close</button>
          <button class="btn btn-danger" @click="cancelRequest(selectedRequest.request_id)">Proceed</button>
        </template>
      </Modal>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Modal from './ModalComponent.vue';
  
  export default {
    components: {
      Modal,
    },
    data() {
      return {
        errorMessage:'',
        successMessage:'',
        requests: [],
        selectedRequest: {},
        showCompleteModal: false,
        showCancelModal: false,
      };
    },
    async mounted() {
      await this.fetchRequests();
    },
    methods: {
      async fetchRequests() {
        try {
          const response = await axios.get('/customer-requests');
          this.requests = response.data.services;
        } catch (error) {
          console.error('Error fetching customer requests:', error);
        }
      },
      openModal(requestId, action) {
        this.selectedRequest = this.requests.find(req => req.request_id === requestId);
        if (action === 'complete') {
          this.showCompleteModal = true;
        } else if (action === 'cancel') {
          this.showCancelModal = true;
        }
      },
      async markAsComplete(requestId, customerName, serviceName) {
        try {
          const response = await axios.post(`/complete-request/${requestId}`);
          this.successMessage = response.data.message;
          this.showCompleteModal = false;
          await this.fetchRequests();
          this.$router.push({ name: 'submit-remark', params: { request_id: requestId, customer_name: customerName, service_name: serviceName } });
        } catch (error) {
            if (error.response && error.response.data.error) {
                 this.errorMessage = error.response.data.error;
            }
          console.error('Error marking request as complete:', error);
        }
      },
      async cancelRequest(requestId) {
        try {
          const response = await axios.post(`/cancel/${requestId}`);
          this.successMessage = response.data.message;
          this.showCancelModal = false;
          await this.fetchRequests();
        } catch (error) {
            if (error.response && error.response.data.error) {
                 this.errorMessage = error.response.data.error;
            }
          console.error('Error canceling request:', error);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .container {
    margin-bottom: 20px;
  }
  </style>
  