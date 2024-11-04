<template>
  <div>
      <h1>Search Results for Service Professionals</h1>
      <div v-if="searchResults && searchResults.length">
          <div v-for="professional in searchResults" :key="professional.id" class="professional-result">
              <b>Name:</b> {{ professional.name }} <br />
              <b>Email:</b> {{ professional.email }} <br />
              <b>Description:</b> {{ professional.description }} <br />
              <b>Experience:</b> {{ professional.experience }} <br />
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
  }
}
</script>