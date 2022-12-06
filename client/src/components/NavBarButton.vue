<template>
  <div>
    <router-link :to="href" replace>
      <button @click="clickBtn" v-if="active" class="
        bg-white
        hover:text-black
        rounded-lg
        px-4
        py-2
        font-semibold
        transition
        duration-200
        ease-in-out
        focus:outline-none
        focus:ring-2
        focus:ring-white
        focus:ring-opacity-50
        ">
        <slot></slot>
      </button>
      <button @click="clickBtn" v-else class="
        text-gray-100
        bg-white-100
        hover:text-black
        rounded-lg
        px-4
        py-2
        font-semibold
        transition
        duration-200
        ease-in-out
        focus:outline-none
        focus:ring-2
        focus:ring-white
        focus:ring-opacity-50
        ">
        <slot></slot>
      </button>
    </router-link>
  </div>
</template>

<script>
export default {
  props: {
    href: {
      type: String,
      required: true
    },
    active: {
      type: Boolean,
      required: false,
      default: false
    }
  }
}
</script>

<style>
button:hover {
  background-color: #ffffd8;
}
</style>
