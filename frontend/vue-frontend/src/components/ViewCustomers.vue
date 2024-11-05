<template>
    <div>   
        <h1>View All Customers</h1>
        <div v-if="customers.length === 0">No Customers available.</div>
        <div v-else>
            <div v-for="(data, index) in customers" :key="index" class="container">
                <b>Customer Name:</b> {{ data.username }}<br />
                <b>Email:</b> {{ data.email }}<br />
                <b>Address:</b> {{ data.address }}<br />
                <b>Contact:</b> {{ data.contact }}<br />
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
            customers: []  
        };
    },
    mounted() {
        this.fetchCustomers();  
    },
    methods: {
        async fetchCustomers() {
            try {
                const response = await axios.get('http://localhost:5001/view-customers');
                this.customers = response.data;  
            } catch (error) {
                console.error('Error fetching customers:', error);  
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
