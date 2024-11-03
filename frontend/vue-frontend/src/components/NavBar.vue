<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-body">
      <div class="container-fluid">
        <ul class="navbar-nav">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/about">About Us</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/remarks">Remarks</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/contact">Contact</router-link>
          </li>
          <template v-if="isAuthenticated">
            <template v-if="role === 'customer'">
              <li class="nav-item">
                <router-link class="nav-link" to="/customer-dash">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/graph">View Customer Graphs</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/customer-requests">View Requested Services</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/past-services">View Past Services</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/account">Account</router-link>
              </li>
            </template>
            <template v-else-if="role === 'service_professional'">
              <li class="nav-item">
                <router-link class="nav-link" to="/sp-dash">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/graph">View Service Professional Graphs</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/pending-requests">Pending Requests</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/past-services">View Past Services</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/account">Account</router-link>
              </li>
            </template>
            <template v-else>
              <li class="nav-item">
                <router-link class="nav-link" to="/new-service">New Service</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/view-customers">View All Customers</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/view-service-professionals">View All Service Professionals</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/view-service-requests">View All Service Requests</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/graph">View Admin Graphs</router-link>
              </li>
            </template>
            <li class="nav-item">
              <router-link class="nav-link" to="/services">Services</router-link>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Customer Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Customer Register</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/sp-login">Service Professional Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/sp-register">Service Professional Register</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin-login">Admin Login</router-link>
            </li>
          </template>
        </ul>
      </div>
    </nav>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  computed: {
    ...mapState(['isAuthenticated', 'role']),
  },
  methods: {
    ...mapActions(['fetchAuthStatus']),
    async logout() {
    await this.$store.dispatch('logout');
  },
  },
  created() {
    this.fetchAuthStatus();
  }
};
</script>

<style scoped>
/* Add your custom styles here */
</style>
