<template>
  <div id="app">
    <el-container>
      <header-vue />
      <main-vue />
    </el-container>
  </div>
</template>

<script>
import HeaderVue from './components/HeaderVue';
import MainVue from './components/MainVue';
import axios from 'axios' // eslint-disable-line no-unused-vars

export default {
  name: 'app',
  components: {
    HeaderVue,
    MainVue
  },
  data() {
    return {
    }
  },
  methods: {
  },
  
}
</script>

<style>
#app {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  font-family: sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: #36393f;
  margin: 0;
  overflow-y: scroll;
}
</style>
