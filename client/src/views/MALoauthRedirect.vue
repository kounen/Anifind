<template>
  <div class="m-auto">
    <span class="loader"></span>
  </div>
</template>

<script>
export default {
  name: 'MALoauthRedirect',
  data () {
    return {
      code: ''
    }
  },
  created () {
    this.axios.post(`${process.env.VUE_APP_API_URL}/mal-anime-list`, {
      code: this.$route.query.code,
      code_verifier: this.$cookies.get('code_challenge'),
      username: this.$cookies.get('user'),
      env: 'prod'
    }).then((response) => {
      this.$router.push('/profile')
      console.log(response.data)
    })
  }
}
</script>

<style>
.loader {
  width: 48px;
  height: 48px;
  border: 3px solid #000;
  border-radius: 50%;
  display: inline-block;
  position: relative;
  box-sizing: border-box;
  animation: rotation 1s linear infinite;
}
.loader::after {
  content: '';
  box-sizing: border-box;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-bottom-color: #FF3D00;
}

@keyframes rotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
