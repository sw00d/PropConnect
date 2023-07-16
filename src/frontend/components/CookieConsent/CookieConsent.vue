<template>
  <v-slide-x-reverse-transition>
    <v-sheet width="300" class="pa-4" v-if="!accepted">
      <div class="weight-600 opacity-7">
        This website uses cookies to ensure you get the best experience navigating our site!
      </div>
      <v-btn
        class="text-uppercase rounded-0 mt-1"
        height="42px"
        width="101px"
        variant="tonal"
        color="primary"
        @click="accept_cookie"
      >
        Got it!
      </v-btn>
    </v-sheet>
  </v-slide-x-reverse-transition>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'banner-consent-cookie',
  setup() {
    const accepted = ref(true);
    const name = 'banner-consent-cookie';

    const accept_cookie = () => {
      //sets cookie that expires in 364 days
      const date = new Date();
      date.setTime(date.getTime() + (364 * 24 * 60 * 60 * 1000));
      const expires = "; expires=" + date.toUTCString();
      document.cookie = `${name}=1;${expires}; path=/`;
      accepted.value = true;
    };

    const already_accepted = () => {
      const cookies = document.cookie;
      return cookies.includes(`${name}=`);
    };

    onMounted(() => {
      if (!already_accepted()) {
        accepted.value = false;
      }
    });

    return { accepted, accept_cookie };
  },
}
</script>

<style scoped lang="stylus">
.v-sheet
  border 1px solid black
  width: 300px;
  position: fixed;
  z-index: 9999;
  right: 20px;
  bottom: 20px;
</style>

