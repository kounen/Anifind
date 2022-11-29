<template>
  <div>
    <v-card width="30%" style="margin: 2em">
      <v-card-title>My stats</v-card-title>
      <p>
        Number of anime rated: {{ratingNbr}}
      </p>
      <p>
        Favorite genre: {{favoriteGenre}}
      </p>
    </v-card>
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
        :key="item.name"
      >
        <td>{{ item.name }}</td>
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
      response.data[0].anime.forEach((anime, index) => {
        this.ratings.push({
          name: anime,
          rating: response.data[0].rating[index] / 2
        })
      })
      console.log(this.ratings)
      this.ratingNbr = response.data[0].anime.length
    })
    this.favoriteGenre = 'Action'
  },
  methods: {
    rateAnime (anime) {
      this.axios.post(`${process.env.VUE_APP_API_URL}/ratings`, {
        username: this.$cookies.get('user'),
        ratings: {
          rating: anime.rating * 2,
          anime: anime.name
        }
      }).then((response) => {
        console.log(response)
      })
    }
  }
}
</script>
