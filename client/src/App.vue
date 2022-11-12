<template>
  <v-app>
    <NavBar />
    <router-view/>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar
  },
  data: () => ({
    //
  })
}
</script>

<style>
@font-face {
  font-family: KronaOne;
  src: url('./assets/fonts/KronaOne-Regular.ttf');
}
body {
  font-family: KronaOne;
}
</style>
