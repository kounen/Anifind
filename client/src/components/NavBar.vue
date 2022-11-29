<template>
  <div class="navbar">
    <div class="title text-xl flex align-center">
      <Navbar-button href="/" :active="activePage == '/'">Anifind</Navbar-button>
    </div>
    <div class="navbar__menu" v-if="!connected">
      <Navbar-button href="/register" :active="activePage == '/register'">Sign In</Navbar-button>
      <Navbar-button href="/login" :active="activePage == '/login'">Login</Navbar-button>
    </div>
    <div class="navbar__menu" v-else>
      <Navbar-button href="/profile" :active="activePage == '/profile'">Profile</Navbar-button>
    </div>
  </div>
</template>

<script>
import NavbarButton from './NavBarButton.vue'

export default {
  components: {
    NavbarButton
  },
  watch: {
    $route () {
      this.activePage = this.$route.path
    }
  },
  mounted () {
    const interval = setInterval(() => {
      if (this.$cookies.get('user')) {
        this.connected = true
        clearInterval(interval)
      }
    }, 1000)
  },
  data () {
    return {
      activePage: '',
      connected: false
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: #fec421;
  display: flex;
  justify-content: space-between;
}

.navbar__menu {
  display: flex;
  align-items: center;
  margin: 10px 20px;
}
.title {
  margin: 10px 20px;
}
</style>
