<template>
  <div class="recommandation">
    <h1 class="text-2xl">For you</h1>
    <CustomSwiper @showInfo="showInfo" :data="anime"/>
    <AnimeModal :data="data" ref="modal"/>
  </div>
</template>

<script>
import CustomSwiper from '@/components/CustomSwiper.vue'
import AnimeModal from '@/components/AnimeModal.vue'

export default {
  name: 'HomePage',
  data () {
    return {
      anime: [
        {
          title: 'One Piece',
          episodes: 12,
          score: 8.5,
          type: 'Shonen'
        },
        {
          title: 'Naruto',
          episodes: 12,
          score: 8.5,
          type: 'Shonen'
        },
        {
          title: 'Bleach',
          episodes: 12,
          score: 8.5,
          type: 'Shonen'
        },
        {
          title: 'Dragon Ball',
          episodes: 12,
          score: 8.5,
          type: 'Shonen'
        }
      ],
      dialog: false,
      data: {}
    }
  },
  components: {
    CustomSwiper,
    AnimeModal
  },
  methods: {
    showInfo (data) {
      this.data = data
      this.$refs.modal.openModal()
    }
  }
}
</script>

<style>
.recommandation {
  margin: 2rem 0;
}
</style>
