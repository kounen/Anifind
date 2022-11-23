<template>
  <div class="recommandation">
    <h1 class="text-2xl">For you</h1>
    <CustomSwiper @showInfo="showInfo" :data="anime"/>
    <v-dialog v-model="dialog">
      <v-card>
        <v-card-title>{{animeModal.title}}</v-card-title>
        <v-card-text>
          {{animeModal.episode}}
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import CustomSwiper from '@/components/CustomSwiper.vue'

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
      animeModal: {}
    }
  },
  components: {
    CustomSwiper
  },
  methods: {
    showInfo (data) {
      this.animeModal = data
      this.dialog = true
    }
  }
}
</script>

<style>
.recommandation {
  margin: 2rem 0;
}
</style>
