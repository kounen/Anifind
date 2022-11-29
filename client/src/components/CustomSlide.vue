<template>
  <div class="slide" :style="{'background-image': 'url(' + backgroundSrc + ')', 'background-size': 'cover'}">
    <div class="overlay">
      <div class="w-full">
        <h3>
          {{anime.name}}
        </h3>
      </div>
      <div class="overlay-info">
        <div class="flex flex-row">
          <div class="flex flex-col mr-4">
            <p class="text-sm">Episodes</p>
            <p class="text-sm">Score</p>
            <p class="text-sm">Type</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm">{{anime.episodes}}</p>
            <p class="text-sm">{{anime.score}}</p>
            <p class="text-sm">{{anime.type}}</p>
          </div>
        </div>
        <div class="flex justify-between">
          <v-rating
            v-model="anime.rating"
            hover
            half-increments
            @input="rateAnime"
          ></v-rating>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CustomSlide',
  props: {
    data: Object
  },
  created () {
    this.axios.get('https://api.giphy.com/v1/gifs/search?api_key=fx26DNUVWn72F2aiHCKiCiFnanqZbJ4f&limit=1&q=' + this.data.name.split(' ').slice(0, 2).join(' ') + ' anime').then((response) => {
      this.backgroundSrc = response.data.data[0].images.original.url
    })
  },
  data () {
    return {
      anime: this.data,
      backgroundSrc: ''
    }
  },
  methods: {
    rateAnime (rate) {
      this.axios.post(`${process.env.VUE_APP_API_URL}/ratings`, {
        username: this.$cookies.get('user'),
        ratings: {
          rating: rate.target.value * 2,
          anime: this.anime.name
        }
      }).then((response) => {
        console.log(response)
      })
    }
  }
}
</script>

<style>
.slide {
  border: black solid 1px;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  font-weight: bold;
  font-size: 22px * 1.6;
  color: black;
}
.overlay {
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  width: 100%;
  height: 45%;
  display: flex;
  flex-direction: column;
  font-weight: bold;
  padding: 1rem 1rem;
  font-size: 22px * 1.6;
}
.overlay-info {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>
