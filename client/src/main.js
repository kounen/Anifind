import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import './assets/tailwind.css'
import Toaster from '@meforma/vue-toaster'
// import SwiperClass, { /* swiper modules... */ } from 'swiper'
// import VueAwesomeSwiper from 'vue-awesome-swiper'

// import 'swiper/css'

// SwiperClass.use([/* swiper modules... */])
loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .use(Toaster, {
    position: 'bottom'
  })
  // .use(VueAwesomeSwiper)
  .mount('#app')
