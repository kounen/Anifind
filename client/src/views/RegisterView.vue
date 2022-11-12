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
    valid: false
  }),
  methods: {
    register () {
      this.$toast.info('register')
    }
  }
}
</script>

<style>
</style>
