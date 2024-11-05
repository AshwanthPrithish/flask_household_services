<template>
    <div container>   
        <div class="media">
            <img v-if="fullGraphUrlOne" :src="fullGraphUrlOne" alt="Graph One" class="graph-pic" :style="{ width: graphWidth }" />
            <img v-if="fullGraphUrlTwo" :src="fullGraphUrlTwo" alt="Graph Two" class="graph-pic" :style="{ width: graphWidth }" />
            <img v-if="fullGraphUrlThree" :src="fullGraphUrlThree" alt="Graph Three" class="graph-pic" :style="{ width: graphWidth }" />
        </div>
    </div>
</template>

<script>
import axios from 'axios';
    export default{
        data() {
            return {
                    graphOneUrl: '', 
                    graphTwoUrl: '', 
                    graphThreeUrl: '', 
                    graphOneError: '',
                    graphTwoError: '',
                    graphThreeError: ''
               }
        },
        created() {
            this.loadAccountData();
        },
        computed:{
            fullGraphUrlOne() {
                return this.graphOneUrl ? `${axios.defaults.baseURL}/media/${this.graphOneUrl}` : '';
            },
            fullGraphUrlTwo() {
                return this.graphTwoUrl ? `${axios.defaults.baseURL}/media/${this.graphTwoUrl}` : '';
            },
            fullGraphUrlThree() {
                return this.graphThreeUrl ? `${axios.defaults.baseURL}/media/${this.graphThreeUrl}` : '';
            },
            graphWidth() {
            const images = [this.fullGraphUrlOne, this.fullGraphUrlTwo, this.fullGraphUrlThree];
            const availableImages = images.filter(Boolean).length;
            return availableImages > 0 ? `${100 / availableImages}%` : '100%';
            }
        },
        methods: {
            async loadAccountData() {
                    try {
                        const response = await axios.get('http://localhost:5001/admin-graphs');
                        const data = response.data;
                        this.graphOneUrl = data.one;
                        this.graphTwoUrl = data.two;
                        this.graphThreeUrl = data.three;
                    } catch (error) {
                        console.error('Failed to load account data:', error);
                    }
            },
        }
    }
</script>

<style scoped>

.media {
  display: flex;
  gap: 10px;
}

.graph-pic {
  height: 60%;
  object-fit: cover;
  border-radius: 5px;
}

</style>