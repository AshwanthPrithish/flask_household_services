<template>
    <div>
        <h1>HouseHold Services Hub - Service Professional {{ username }} Dashboard</h1>

        <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>

        <div class="container">
            <form @submit.prevent="searchService">
                <fieldset class="form-group">
                    <legend class="border-bottom mb-4">Search Service</legend>
                    
                    <div class="form-group">
                        <label for="service">Enter the service to search for:</label>
                        <input type="text" v-model="service" class="form-control" :class="{'is-invalid': serviceError}" />
                        <div v-if="serviceError" class="invalid-feedback">{{ serviceError }}</div>
                    </div>
                    
                    <div class="form-group">
                        <button type="submit" class="btn btn-outline-info">Search</button>
                    </div>
                </fieldset>
            </form>
        </div>

        <div class="container">
            <form @submit.prevent="searchServiceProfessional">
                <fieldset class="form-group">
                    <legend class="border-bottom mb-4">Search Service Professional</legend>
                    
                    <div class="form-group">
                        <label for="serviceProfessional">Enter the service professional to search for:</label>
                        <input type="text" v-model="serviceProfessional" class="form-control" :class="{'is-invalid': serviceProfessionalError}" />
                        <div v-if="serviceProfessionalError" class="invalid-feedback">{{ serviceProfessionalError }}</div>
                    </div>
                    
                    <div class="form-group">
                        <button type="submit" class="btn btn-outline-info">Search</button>
                    </div>
                </fieldset>
            </form>
        </div>

        <div class="container">
            <form @submit.prevent="triggerExport">
                <fieldset class="form-group">
                    <legend class="border-bottom mb-4">Trigger CSV Export</legend>
                    
                    <div class="form-group">
                        <button type="submit" class="btn btn-outline-info">Trigger</button>
                    </div>
                </fieldset>
            </form>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import axios from 'axios';

export default {
    data() {
        return {
            username: '',
            service: '',
            serviceError: '', 
            serviceProfessional: '',
            serviceProfessionalError: '',
            successMessage: '',
        };
    },
    computed: {
        ...mapState(['isAuthenticated', 'role']),
    },
    methods: {
        ...mapActions(['fetchAuthStatus', 'setSearchResults']),
        
        async searchService() {
            this.serviceError = '';
            if (!this.service) {
                this.serviceError = 'Service is required.';
                return;
            }
            try {
               const response = await axios.post('http://localhost:5001/search-results-service', { service: this.service });
               this.setSearchResults(response.data); 
               this.$router.push({ name: 'SearchResultsService' });
            } catch (error) {
                console.error('Error searching for service:', error);
            }
        },

        async searchServiceProfessional() {
            this.serviceProfessionalError = '';
            if (!this.serviceProfessional) {
                this.serviceProfessionalError = 'Service professional is required.';
                return;
            }
            try {
                const response = await axios.post('http://localhost:5001/search-results-service-professional', { service_professional: this.serviceProfessional });
                this.setSearchResults(response.data);
                this.$router.push({ name: 'SearchResultsServiceProfessional' });
            } catch (error) {
                console.error('Error searching for service professional:', error);
            }
        },
        async triggerExport(){
            try {
                const response = await axios.get('http://localhost:5001/export_csv');
                this.successMessage = response.data.message;
            } catch (error) {
                console.error('Error triggering export:', error);
            }
        }
    },
    created() {
        this.fetchAuthStatus();
        axios.get('http://localhost:5001/sp-dash')
            .then(response => {
                this.username = response.data.username;
            })
            .catch(error => {
                console.error('Error fetching admin dashboard data:', error);
            });
    }
}
</script>

<style scoped>
.container {
    margin-bottom: 20px; 
}
</style>
