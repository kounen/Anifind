<template>
  <div>
    <div class="recommandation">
      <h1 class="text-2xl">For you</h1>
      <CustomSwiper :data="suggestions"/>
    </div>
    <div>
      <h1 class="text-2xl">Animes by genre</h1>
      <v-select
      label="Genre"
      :items="genres"
      v-model="selectedGenre"
      ></v-select>
      <CustomSwiper :data="animes"/>
    </div>
  </div>
</template>

<script>
import CustomSwiper from '@/components/CustomSwiper.vue'

export default {
  name: 'HomePage',
  data () {
    return {
      suggestions: [{
        name: 'Vive',
        researchName: 'France',
        score: 0,
        type: '',
        episodes: 0
      },
      {
        name: 'la',
        researchName: 'mbappe',
        score: 0,
        type: '',
        episodes: 0
      },
      {
        name: 'France',
        researchName: 'France trophy',
        score: 0,
        type: '',
        episodes: 0
      }],
      animes: [],
      genres: [
        'All',
        'Action',
        'Adventure',
        'Cars',
        'Comedy',
        'Dementia',
        'Demons',
        'Mystery',
        'Drama',
        'Ecchi',
        'Fantasy',
        'Game',
        'Hentai',
        'Historical',
        'Horror',
        'Kids',
        'Magic',
        'Martial Arts',
        'Mecha',
        'Music',
        'Parody',
        'Samurai',
        'Romance',
        'School',
        'Sci-Fi',
        'Shoujo',
        'Shoujo Ai',
        'Shounen',
        'Shounen Ai',
        'Space',
        'Sports',
        'Super Power',
        'Vampire',
        'Yaoi',
        'Yuri',
        'Harem',
        'Slice of Life',
        'Supernatural',
        'Military',
        'Police',
        'Psychological',
        'Thriller',
        'Seinen',
        'Josei'
      ],
      selectedGenre: 'All'
    }
  },
  created () {
    if (!this.$cookies.get('user')) {
      this.$router.push('/login')
    }
    this.getAnimesByGenre('All')
  },
  watch: {
    selectedGenre: function (newVal, oldVal) {
      this.getAnimesByGenre(newVal)
    }
  },
  components: {
    CustomSwiper
  },
  methods: {
    getAnimesByGenre (genre) {
      let url = `${process.env.VUE_APP_API_URL}/animesGenre?Genre=${genre}`
      this.animes = []
      if (genre === 'All') {
        url = `${process.env.VUE_APP_API_URL}/animes`
      }
      this.axios.get(url).then((response) => {
        let animes = response.data.filter((anime) => {
          return anime.Score > 8.5
        })
        if (animes.length < 10) {
          animes = response.data.filter((anime) => {
            return anime.Score > 8
          })
        }
        const shuffled = [...animes].sort(() => 0.5 - Math.random())
        this.animes = shuffled.slice(0, 10)
        this.animes = this.animes.map((anime) => {
          return {
            name: anime['English name'] === 'Unknown' ? anime.Name : anime['English name'],
            researchName: anime.Name,
            score: anime.Score === 'Unknown' ? 0 : anime.Score,
            type: anime.Genres,
            episodes: anime.Episodes
          }
        })
      })
    }
  }
}
</script>

<style>
.recommandation {
  margin: 2rem 0;
}
</style>
