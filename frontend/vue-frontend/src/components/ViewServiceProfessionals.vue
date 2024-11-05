<template>
    <div>   
        <h1>View All Service Professionals</h1>
        <div v-if="service_professionals.length === 0">No Professionals available.</div>
        <div v-else>
            <div v-for="(data, index) in service_professionals" :key="index" class="container">
                <b>Professional Name:</b> {{ data.username }}<br />
                <b>Email:</b> {{ data.email }}<br />
                <b>Description:</b> {{ data.description }}<br />
                <b>Experience:</b> {{ data.experience }}<br />
                <b>Date Created:</b> {{ data.date_created }}<br />
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
            service_professionals: []  
        };
    },
    mounted() {
        this.fetchServiceProfessionals();  
    },
    methods: {
        async fetchServiceProfessionals() {
            try {
                const response = await axios.get('http://localhost:5001/view-service-professionals');
                this.service_professionals = response.data;  
            } catch (error) {
                console.error('Error fetching professionals:', error);  
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
