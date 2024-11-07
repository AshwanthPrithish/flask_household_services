<template>
    <div>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>

      <h1>Pending Requests</h1>
  
      <div v-for="request in requests" :key="request.request_id" class="container mb-4">
        <div>
          <button class="btn btn-secondary btn-sm m-1" @click="openAcceptModal(request)">Accept Service Request</button>
          <button class="btn btn-danger btn-sm m-1" @click="openRejectModal(request)">Reject Request</button>
        </div>
  
        <b>Service Name:</b> {{ request.service_name }}<br />
        <b>Customer Name:</b> {{ request.customer_name }}<br />
        <b>Date of Request:</b> {{ request.date_of_request }}<br />
        <b>Date of Completion:</b> {{ request.date_of_completion }}<br />
  
        <!-- Accept Modal -->
        <Modal :isVisible="showAcceptModal && selectedRequest?.request_id === request.request_id" @close="showAcceptModal = false">
            <template v-slot:header>
            <h5>Accept Request</h5>
          </template>
          <p>Accept request <b>{{ request.service_name }}</b> from customer <b>{{ request.customer_name }}</b>?</p>
          <template v-slot:footer>
            <button class="btn btn-secondary" @click="showAcceptModal = false">Close</button>
            <button class="btn btn-danger" @click="acceptRequest(request.request_id)">Accept</button>
          </template>
        </Modal>
  
        <!-- Reject Modal -->
        <Modal :isVisible="showRejectModal && selectedRequest?.request_id === request.request_id" @close="showRejectModal = false">
            <template v-slot:header>
            <h5>Reject Request</h5>
          </template>
          <p>Reject request for service <b>{{ request.service_name }}</b> from customer <b>{{ request.customer_name }}</b>?</p>
          <template v-slot:footer>
            <button class="btn btn-secondary" @click="showRejectModal = false">Close</button>
            <button class="btn btn-danger" @click="rejectRequest(request.request_id)">Reject</button>
          </template>
        </Modal>
      </div>
    </div>
  </template>
  
  <script>
  import Modal from "./ModalComponent.vue"; 
  import axios from "axios";
  import { mapState } from 'vuex';
  
  export default {
    components: {
      Modal,
    },
    computed: {
    ...mapState(['id'])
  },
    data() {
      return {
        requests: [],
        showAcceptModal: false,
        showRejectModal: false,
        selectedRequest: null,
        successMessage: '',
        errorMessage: '',
      };
    },
    async created() {
      await this.fetchPendingRequests();
    },
    methods: {
      async fetchPendingRequests() {
        try {
          const response = await axios.get("/pending-requests");
          this.requests = response.data.pending_requests;
        } catch (error) {
          console.error("Error fetching pending requests:", error);
        }
      },
      openAcceptModal(request) {
        this.selectedRequest = request;
        this.showAcceptModal = true;
      },
      openRejectModal(request) {
        this.selectedRequest = request;
        this.showRejectModal = true;
      },
      async acceptRequest(requestId) {
        try {
          const response = await axios.post(`/accept-request/${requestId}/${this.id}`);
          this.successMessage = response.data.message;
          this.showAcceptModal = false;
          await this.fetchPendingRequests();
        } catch (error) {
            if (error.response.data.error) {
            this.errorMessage = error.response.data.error;
          }
        }
      },
      async rejectRequest(requestId) {
        try {
            const response = await axios.post(`/reject-request/${requestId}/${this.id}`);
            this.successMessage = response.data.message;
          this.showRejectModal = false;
          await this.fetchPendingRequests();
        } catch (error) {
            if (error.response.data.error) {
            this.errorMessage = error.response.data.error;
          }
          console.error("Error rejecting request:", error);
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
  