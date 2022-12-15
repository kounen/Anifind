<template>
  <div>
    <div class="flex flex-row justify-around">
      <v-card width="30%" style="margin: 2em">
        <v-card-title>My stats</v-card-title>
        <p>
          Number of anime rated: {{ratingNbr}}
        </p>
      </v-card>
      <v-card style="margin: 2em">
        <v-card-title>How's your experience with Anifind ?</v-card-title>
        <div class="flex flex-column justify-center align-center">
          <p>Fill our survey !</p>
          <a href="https://docs.google.com/forms/d/e/1FAIpQLSe-hrEHYzys53EAtllToSSwvvuIdzkXivSf5kDJe28sP2FRhg/viewform?usp=sf_link" target="_blank" rel="noopener noreferrer">
            <v-btn style="margin: 1em" color="primary">
              <v-icon>mdi-google</v-icon>
            </v-btn>
          </a>
        </div>
      </v-card>
      <v-card style="margin: 2em">
        <v-card-title>Import all your MyAnimeList ratings !</v-card-title>
        <div class="flex flex-column justify-center align-center">
          <p>Click right here !</p>
          <v-btn @click="oauth2MAL" style="margin: 1em" color="primary">
            <v-icon>mdi-database-import</v-icon>
          </v-btn>
        </div>
      </v-card>
    </div>
    <v-table>
    <thead>
      <tr>
        <th class="text-left">
          Name
        </th>
        <th class="text-left">
          Your Rating
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="item in ratings"
        :key="item.anime"
      >
        <td>{{ item.anime }}</td>
        <td>
          <v-rating
            v-model="item.rating"
            hover
            half-increments
            @input="rateAnime(item)"
          ></v-rating>
        </td>
      </tr>
    </tbody>
  </v-table>
  </div>
</template>

<script>
export default {
  name: 'ProfilePage',
  data () {
    return {
      favoriteGenre: '',
      ratings: [],
      ratingNbr: 0,
      headers: [
        {
          text: 'Anime',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        { text: 'Your rating', value: 'rating' }
      ]
    }
  },
  created () {
    this.axios.get(`${process.env.VUE_APP_API_URL}/ratings?username=${this.$cookies.get('user')}`).then((response) => {
      this.ratings = response.data.map((rating) => {
        return {
          anime: rating.anime,
          rating: rating.rating / 2
        }
      })
      this.ratingNbr = response.data.length
    })
    this.favoriteGenre = 'Action'
  },
  methods: {
    rateAnime (anime) {
      this.axios.post(`${process.env.VUE_APP_API_URL}/ratings`, {
        username: this.$cookies.get('user'),
        ratings: {
          rating: anime.rating * 2,
          anime: anime.anime
        }
      }).then((response) => {
        console.log(response)
      })
    },
    oauth2MAL () {
      this.axios.get(`${process.env.VUE_APP_API_URL}/mal-auth-url?env=prod`).then((response) => {
        const params = new Proxy(new URLSearchParams(response.data), {
          get: (searchParams, prop) => searchParams.get(prop)
        })
        this.$cookies.set('code_challenge', params.code_challenge)
        window.location.href = response.data
      })
    }
  }
}
</script>
