<template>
    <div>   
        <h1>View All Service Requests</h1>
        <div v-if="past_services.length === 0">No Past Services available.</div>
        <div v-else>
            <div v-for="(data, index) in past_services" :key="index" class="container">
                <div v-if="role === 'customer'">
                     <b>Service Professional Name:</b> {{ data.service_professional_name }}<br />
                </div>
                <div v-else>
                    <b>Customer Name:</b> {{ data.customer_name }}<br />
                </div>
                <b>Service Name:</b> {{ data.service_name }}<br />
                <b>Date of Request:</b> {{ data.date_of_request }}<br />
                <b>Date of Completion:</b> {{ data.date_of_completion }}<br />
                <br/>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';

export default {
    data() {
        return {
            past_services: []  
        };
    },
    mounted() {
        this.fetchPastServices();  
    },
    computed: {
    ...mapState(['role'])
  },
    methods: {
        async fetchPastServices() {
            try {
                const response = await axios.get('http://localhost:5001/past-services');
                this.past_services = response.data;
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
</style>
