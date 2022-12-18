<template>
  <div class="flex justify-center items-center h-full">
    <v-card width="500px">
      <v-card-title>
        <h1 class="text-3xl m-3">Register</h1>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-text-field
            v-model="username"
            label="Username"
            required
          ></v-text-field>
          <v-text-field
            v-model="password"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="passwordRules"
            :type="showPassword ? 'text' : 'password'"
            label="Password"
            required
            @click:append="showPassword = !showPassword"
          ></v-text-field>
          <v-text-field
            v-model="confirmPassword"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="passwordRules"
            :type="showPassword ? 'text' : 'password'"
            label="Confirm your Password"
            required
            @click:append="showPassword = !showPassword"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions class="flex justify-end">
        <v-btn
          color="secondary"
          class="mr-4"
          :disabled="!valid"
          @click="register"
          size="large"
          outlined
          :loading="loading"
        >Register</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'RegisterView',
  data: () => ({
    username: '',
    password: '',
    confirmPassword: '',
    showPassword: false,
    valid: false,
    loading: false
  }),
  methods: {
    redirectLogin () {
      this.$router.push('/login')
    },
    register () {
      this.loading = true
      if (this.password === this.confirmPassword) {
        this.axios.post(`${process.env.VUE_APP_API_URL}/register`, {
          username: this.username,
          password: this.password
        }).then((response) => {
          this.axios.defaults.headers.common.Authorization = `Bearer ${this.username}`
          this.$cookies.set('user', this.username)
          setTimeout(() => {
            this.loading = false
            this.$router.push({ name: 'home' })
          }, 2000)
        }).catch((error) => {
          this.loading = false
          this.$toast.error(error.response.data)
        })
      } else {
        setTimeout(() => {
          this.loading = false
          this.$toast.error('Passwords do not match')
        }, 2000)
      }
    }
  }
}
</script>

<style>
</style>
