import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import './assets/tailwind.css'
import Toaster from '@meforma/vue-toaster'
import axios from 'axios'
import VueAxios from 'vue-axios'
import VueCookies from 'vue3-cookies'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .use(Toaster, {
    position: 'bottom'
  })
  .use(VueAxios, axios)
  .use(VueCookies)
  .mount('#app')
