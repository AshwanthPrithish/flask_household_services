<template>
    <div>   
        <h1>View Remarks of Services</h1>
        <div v-if="remarks.length === 0">No remarks available.</div>
        <div v-else>
            <div v-for="(data, index) in remarks" :key="index" class="container">
                <b>Service Name:</b> {{ data.service_name }}<br />
                <b>Service Professional Name:</b> {{ data.service_professional_name }}<br />
                <b>Remarks:</b> {{ data.remark }}<br />
                <b>Remark provided by:</b> {{ data.customer_name }}<br />
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
            remarks: []  
        };
    },
    mounted() {
        this.fetchRemarks();  
    },
    methods: {
        async fetchRemarks() {
            try {
                const response = await axios.get('http://localhost:5001/remarks');
                this.remarks = response.data;  
            } catch (error) {
                console.error('Error fetching remarks:', error);  
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
