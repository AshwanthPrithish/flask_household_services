<template>
  <div class="container">
    <div class="media">
      <!-- Use the computed fullProfilePictureUrl -->
      <img :src="fullProfilePictureUrl" alt="Profile Picture" />
      <div class="media-body">
        <h4>{{ form.username }}</h4>
        <p>{{ form.email }}</p>
      </div>
    </div>

    <form @submit.prevent="updateCustomerAccount" enctype="multipart/form-data">
      <fieldset>
        <legend>Account Info</legend>

        <!-- Form Fields Here (Username, Email, Address, etc.) -->

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
          <label for="Address" class="form-control-label">Address</label>
          <textarea
            v-model="form.address"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.address && errors.address.length }"
            id="address"
            rows="4"
          ></textarea>
          <div v-if="errors.address && errors.address.length" class="invalid-feedback">
            <span v-for="error in errors.address" :key="error">{{ error }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="Contact" class="form-control-label">Contact</label>
          <input
            type="text"
            v-model="form.contact"
            class="form-control form-control-lg"
            :class="{ 'is-invalid': errors.contact && errors.contact.length }"
            id="email"
          />
          <div v-if="errors.contact && errors.contact.length" class="invalid-feedback">
            <span v-for="error in errors.contact" :key="error">{{ error }}</span>
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
      profilePictureUrl: '', // The image URL
      form: {
        username: '',
        email: '',
        address: '',
        contact: '',
        picture: null, // File data for the picture
      },
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
        const response = await axios.get('customer-account');
        const data = response.data;
        this.form.username = data.username;
        this.form.email = data.email;
        this.form.address = data.address;
        this.form.contact = data.contact;
        this.profilePictureUrl = data.profilePictureUrl; // Assuming the URL is relative
      } catch (error) {
        console.error('Failed to load account data:', error);
      }
    },
    onFileChange(event) {
      this.form.picture = event.target.files[0];
    },
    async updateCustomerAccount() {
      const formData = new FormData();
      formData.append('username', this.form.username);
      formData.append('email', this.form.email);
      formData.append('address', this.form.address);
      formData.append('contact', this.form.contact);
      if (this.form.picture) formData.append('picture', this.form.picture);

      try {
        await axios.post('customer-account', formData);
        alert('Account updated successfully!');
      } catch (error) {
        this.errors = error.response.data.errors || {};
      }
    }
  }
};
</script>
