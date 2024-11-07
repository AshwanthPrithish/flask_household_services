<template>
    <div>
      <h1>View All Services</h1>
      <div v-if="services.length === 0">No Services available.</div>
      <div v-else>
        <div v-for="(data, index) in services" :key="index" class="container">
          <b>Service Name:</b>
          <a :href="`/service/${data.id}`" class="article-title">{{ data.name }}</a><br />
          <b>Price:</b> {{ data.price }}<br />
          <b>Description:</b> {{ data.description }}<br />
          <br/>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        services: []
      };
    },
    mounted() {
      this.fetchServices();
    },
    methods: {
      async fetchServices() {
        try {
          const response = await axios.get('http://localhost:5001/services');
          this.services = response.data;
        } catch (error) {
          console.error('Error fetching requests:', error);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .container {
    margin-bottom: 20px;
  }
  .article-title {
    color: #007bff;
    text-decoration: none;
  }
  .article-title:hover {
    text-decoration: underline;
  }
  </style>
  