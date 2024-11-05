<template>
    <div class="container">
      <div class="media">
        <img :src="profilePictureUrl" alt="Profile Picture" />
        <div class="media-body">
          <h4>{{ username }}</h4>
          <p>{{ email }}</p>
        </div>
      </div>
      <form @submit.prevent="updateSPAccount" enctype="multipart/form-data">
        <fieldset>
          <legend>Account Info</legend>
  
          <input-field label="Username" v-model="form.username" :errors="errors.username" />
          <input-field label="Email" type="email" v-model="form.email" :errors="errors.email" />
          <input-field label="Description" v-model="form.description" :errors="errors.description" />
          <input-field label="Experience" v-model="form.experience" :errors="errors.experience" />
  
          <div>
            <label>Service</label>
            <select v-model="form.service">
              <option v-for="service in services" :key="service.id" :value="service.name">
                {{ service.name }}
              </option>
            </select>
          </div>
  
          <div>
            <label>Profile Picture</label>
            <input type="file" @change="onFileChange" />
          </div>
  
          <button type="submit">Update Account</button>
        </fieldset>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        profilePictureUrl: '', // The image URL
        form: {
          username: '',
          email: '',
          description: '',
          experience: '',
          service: '',
          picture: null, // File data for the picture
        },
        services: [],
        errors: {}
      };
    },
    created() {
      this.loadAccountData();
      this.loadServices();
    },
    methods: {
      async loadAccountData() {
        try {
          const response = await axios.get('/api/account/service_professional');
          const data = response.data;
          this.form.username = data.username;
          this.form.email = data.email;
          this.form.description = data.description;
          this.form.experience = data.experience;
          this.form.service = data.service;
          this.profilePictureUrl = data.profilePictureUrl;
        } catch (error) {
          console.error('Failed to load account data:', error);
        }
      },
      async loadServices() {
        try {
          const response = await axios.get('/api/services');
          this.services = response.data;
        } catch (error) {
          console.error('Failed to load services:', error);
        }
      },
      onFileChange(event) {
        this.form.picture = event.target.files[0];
      },
      async updateSPAccount() {
        const formData = new FormData();
        formData.append('username', this.form.username);
        formData.append('email', this.form.email);
        formData.append('description', this.form.description);
        formData.append('experience', this.form.experience);
        formData.append('service', this.form.service);
        if (this.form.picture) formData.append('picture', this.form.picture);
  
        try {
          await axios.post('/api/account/service_professional', formData);
          alert('Account updated successfully!');
        } catch (error) {
          this.errors = error.response.data.errors || {};
        }
      }
    }
  };
  </script>
  