<template>
  <div>
    <div class="recommandation">
      <h1 class="text-2xl">For you</h1>
      <div class="flex justify-center align-center" style="height: 20rem">
        <CustomSwiper :data="suggestions" v-if="suggestions.length != 0"/>
        <div v-else>
          <span class="loader" v-if="!haveToRate"></span>
          <p v-else>
            Please rate some animes to get recommendations
          </p>
        </div>
      </div>
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
      suggestions: [],
      animes: [],
      watchAnimes: [],
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
      selectedGenre: 'All',
      userId: '',
      haveToRate: false
    }
  },
  created () {
    if (!this.$cookies.get('user')) {
      this.$router.push('/login')
    }
    this.axios.post(`${process.env.VUE_APP_API_URL}/getId`, {
      username: this.$cookies.get('user')
    }).then((res) => {
      this.userId = res.data
      this.axios.get(`${process.env.VUE_APP_API_URL}/rs?user_id=${this.userId}`).then((res) => {
        this.suggestions = []
        this.suggestions = res.data.map((anime) => {
          return {
            name: anime['English name'] === 'Unknown' ? anime.Name : anime['English name'],
            researchName: anime.Name,
            score: anime.Score === 'Unknown' ? 0 : anime.Score,
            type: anime.Genres,
            episodes: anime.Episodes
          }
        })
        this.haveToRate = false
      }).catch(() => {
        this.haveToRate = true
      })
    })
    this.getRatedAnimes()
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
    getRatedAnimes () {
      this.axios.get(`${process.env.VUE_APP_API_URL}/ratings?username=${this.$cookies.get('user')}`).then((response) => {
        this.watchAnimes = response.data.map((rating) => rating.anime)
      })
    },
    getAnimesByGenre (genre) {
      let url = `${process.env.VUE_APP_API_URL}/animesGenre?Genre=${genre}`
      this.animes = []
      if (genre === 'All') {
        url = `${process.env.VUE_APP_API_URL}/animes`
      }
      this.axios.get(url).then((response) => {
        let animes = response.data.filter((anime) => !this.watchAnimes.includes(anime.Name))
        let minScore = 8.5
        animes = response.data.filter((anime) => {
          return anime.Score > minScore
        })
        for (minScore = 8.5; animes.length < 10 && minScore > 0; minScore -= 0.5) {
          animes = response.data.filter((anime) => {
            return anime.Score > minScore
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
