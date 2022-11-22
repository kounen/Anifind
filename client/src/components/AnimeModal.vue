<template>
  <div>
    <v-dialog v-model="showModal">
      <v-card>
        <v-card-title>{{anime.title}}</v-card-title>
        <v-card-text>
          {{anime.episode}}
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    data: Object
  },
  data () {
    return {
      anime: this.data,
      showModal: false
    }
  },
  methods: {
    openModal () {
      console.log('openmodal tkt')
      this.showModal = true
    }
  }
}
</script>
