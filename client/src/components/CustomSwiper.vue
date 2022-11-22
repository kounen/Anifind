<template>
  <swiper
      class="swiper"
      :modules="modules"
      :slides-per-view="3"
      :space-between="30"
      :navigation="true"
      :loop="true"
      >
      <swiper-slide v-for="element in data" :key="element">
        <CustomSlide @showInfo="showInfo" :data="element"/>
      </swiper-slide>
    </swiper>
</template>

<script>
import { Pagination, Navigation, Autoplay } from 'swiper'
import { Swiper, SwiperSlide } from 'vue-awesome-swiper'
import CustomSlide from '@/components/CustomSlide.vue'
import 'swiper/css'
import 'swiper/css/navigation'

export default {
  name: 'CustomSwiper',
  props: {
    data: Array
  },
  components: {
    Swiper,
    SwiperSlide,
    CustomSlide
  },
  setup () {
    return {
      modules: [Pagination, Navigation, Autoplay]
    }
  },
  methods: {
    showInfo (data) {
      this.$emit('showInfo', data)
    }
  }
}
</script>

<style>
.swiper {
  width: 100%;
  height: 15rem;
  border: 1px solid red;
}
</style>
