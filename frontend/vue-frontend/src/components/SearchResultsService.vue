<template>
  <div>
      <h1>Search Results for Services</h1>
      <div v-if="searchResults && searchResults.length">
          <div v-for="service in searchResults" :key="service.id" class="service-result">
              <b>Name:</b> {{ service.name }} <br />
              <b>Price:</b> {{ service.price }} <br />
              <b>Description:</b> {{ service.description }} <br />
          </div>
      </div>
      <div v-else>
          <p>No results found.</p>
      </div>
  </div>
</template>
  
  <script>
  import { mapState } from 'vuex';
  
  export default {
    computed: {
        ...mapState(['searchResults'])
    },
  };
  </script>
  
  <style scoped>
  .container {
    margin-bottom: 20px;
  }
  </style>
  