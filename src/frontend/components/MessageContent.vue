<template>
  <div>
    <div
      v-for="(media, i) in message.media_message_contents"
      :key="i"
      class="my-2"
    >
      <!--      <v-img-->
      <!--        :src="media.media_url"-->
      <!--        width="500px"-->
      <!--      />-->

      <a :href="media.media_url" target="_blank" rel="noreferrer" class="">
        <v-btn v-if="media.media_url">
          View Media
          <span v-if="message.media_message_contents?.length > 1" class="ml-1">
            ({{ i + 1 }})
          </span>
        </v-btn>
      </a>
    </div>
    {{ message.message_content }}
  </div>
</template>

<script setup lang="ts">
// Imports

// Data
defineProps({
  message: {
    type: Object,
    required: true
  }
})
// Lifecycle

// Methods

// Hooks
</script>

<style scoped lang="stylus">

</style>
