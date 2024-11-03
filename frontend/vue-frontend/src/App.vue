<template>
  <div id="app">
    <NavBar msg="Hello"/>
    <router-view />
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import router from './router'

export default {
  name: 'App',
  components: {
    NavBar
  },
  router
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
