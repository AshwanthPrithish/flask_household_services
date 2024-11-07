<template>
  <div class="container">
    <div class="media">
      <img :src="fullProfilePictureUrl" alt="Profile Picture" />
      <div class="media-body">
        <h4>{{ form.username }}</h4>
        <p>{{ form.email }}</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            {{ successMessage }}
          </div>

    <form @submit.prevent="updateSPAccount" enctype="multipart/form-data">
      <fieldset>
        <legend>Account Info</legend>

        <div class="form-group">
          <label for="UserName" class="form-control-label">UserName</label>
          <input
            type="text"
            v-model="form.username"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.username && errors.username.length }"
            id="username"
          />
          <div v-if="errors.username && errors.username.length" class="invalid-feedback">
            <span v-for="error in errors.username" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="Email" class="form-control-label">Email</label>
          <input
            type="email"
            v-model="form.email"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.email && errors.email.length }"
            id="email"
          />
          <div v-if="errors.email && errors.email.length" class="invalid-feedback">
            <span v-for="error in errors.email" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="ServiceType" class="form-control-label">Service Type</label>
          <select
            v-model="form.serviceType"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.serviceType && errors.serviceType.length }"
            id="serviceType"
          >
            <option value="" disabled>Select a service type</option>
            <option v-for="type in serviceTypes" :key="type.id" :value="type.id">{{ type.name }}</option>
          </select>
          <div v-if="errors.serviceType && errors.serviceType.length" class="invalid-feedback">
            <span v-for="error in errors.serviceType" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="Description" class="form-control-label">Description</label>
          <textarea
            v-model="form.description"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.description && errors.description.length }"
            id="description"
            rows="4"
          ></textarea>
          <div v-if="errors.description && errors.description.length" class="invalid-feedback">
            <span v-for="error in errors.description" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="Experience" class="form-control-label">Experience</label>
          <input
            type="text"
            v-model="form.experience"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.experience && errors.experience.length }"
            id="experience"
          />
          <div v-if="errors.experience && errors.experience.length" class="invalid-feedback">
            <span v-for="error in errors.experience" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="picture" class="form-control-label">Profile Picture</label>
          <hr />
          <input
            style="margin-left: 10%;"
            type="file"
            @change="onFileChange"
            class="form-control-file"
            :class="{ 'is-invalid': errors.picture && errors.picture.length }"
            id="picture"
          />
          <hr />
          <div v-if="errors.picture && errors.picture.length" class="invalid-feedback">
            <span v-for="error in errors.picture" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <button type="submit" class="btn btn-outline-info">Submit</button>
        </div>
      </fieldset>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      profilePictureUrl: '',
      serviceTypes: [],
      form: {
        username: '',
        email: '',
        description: '',
        serviceType: '', 
        experience: '',
        picture: null,
      },
      successMessage: '',
      errorMessage: '',
      errors: {}
    };
  },
  created() {
    this.loadAccountData();
  },
  computed: {
    fullProfilePictureUrl() {
      return this.profilePictureUrl ? `${axios.defaults.baseURL}/media/${this.profilePictureUrl}` : '';
    }
  },
  methods: {
    async loadAccountData() {
      try {
        const response1 = await axios.get('/fetch-services'); 
        this.serviceTypes = response1.data;
        
        const response = await axios.get('sp-account');
        const data = response.data;
        this.form.username = data.username || '';
        this.form.email = data.email || '';
        this.form.description = data.description || '';
        this.form.experience = data.experience || '';
        this.profilePictureUrl = data.profilePictureUrl || '';
        this.form.serviceType = data.service?.id || '';
      } catch (error) {
        console.error('Failed to load account data:', error);
      }
    },
    onFileChange(event) {
      this.form.picture = event.target.files[0];
    },
    async updateSPAccount() {
      const formData = new FormData();
      formData.append('username', this.form.username);
      formData.append('email', this.form.email);
      formData.append('experience', this.form.experience);
      formData.append('description', this.form.description);
      formData.append('service_id', this.form.serviceType); 
      if (this.form.picture) formData.append('picture', this.form.picture);

      try {
        const response = await axios.post('sp-account', formData);
        this.successMessage = response.data.message;
      } catch (error) {
        this.errors = error.response?.data?.errors || {};
        if (error.response.data.message) {
            this.errorMessage = error.response.data.message;
          }
      }
    }
  }
};
</script>
