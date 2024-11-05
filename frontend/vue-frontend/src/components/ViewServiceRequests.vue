<template>
    <div>   
        <h1>View All Service Requests</h1>
        <div v-if="service_requests.length === 0">No Requests available.</div>
        <div v-else>
            <div v-for="(data, index) in service_requests" :key="index" class="container">
                <b>Customer Name:</b> {{ data.customer_name }}<br />
                <div v-if="data.service_professional_name && data.service_professional_name.length > 0">
                     <b>Service Professional Name:</b> {{ data.service_professional_name }}<br />
                </div>
                <b>Service Name:</b> {{ data.service_name }}<br />
                <b>Service Status:</b> {{ data.service_status }}<br />
                <b>Date of Request:</b> {{ data.date_of_request }}<br />
                <b>Date of Completion:</b> {{ data.date_of_completion }}<br />
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
            service_requests: []  
        };
    },
    mounted() {
        this.fetchServiceRequests();  
    },
    methods: {
        async fetchServiceRequests() {
            try {
                const response = await axios.get('http://localhost:5001/view-service-requests');
                this.service_requests = response.data;  
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
