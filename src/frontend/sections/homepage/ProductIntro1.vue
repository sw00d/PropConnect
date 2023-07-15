<template>
  <div class="bg-primary text-white">
    <v-container class="d-flex justify-space-between align-center py-10">
      <v-row>
        <v-col>
          <div class="d-flex flex-column justify-center h-100">
            <div class="font-weight-black font-40">
              Straight-forward
              <div class="pl-md-16">
                Communication
              </div>
            </div>
            <div class="font-weight-medium opacity-7 text-h6 mt-11">
              Take a step back from the constant juggle between tenants, vendors, and landlords. Our solution brings
              efficiency
              to your role by facilitating direct text-based communication between tenant and vendor. With in depth
              oversight,
              you're
              free
              from mundane tasks, empowering you to focus on expanding your portfolio or simply enjoying your
              well-deserved
              downtime.
            </div>
          </div>
        </v-col>
        <v-col cols="12" md="3" class="d-flex justify-center justify-md-end mt-10 mt-md-0">
          <v-sheet height="415px" width="225px" max-width="100%" class="bg-transparent relative">
            <v-img :src="iphoneOutline"/>

            <v-img
              :src="textBubble1"
              class="absolute right text-bubble one mb-2"
              :style="{bottom: `${200 + bottomBase}px`, opacity: showFirst ? 1 : 0}"
            />
            <v-img
              :src="textBubble3"
              class="absolute left text-bubble two mb-2"
              :style="{bottom: `${150 + bottomBase}px`, opacity: showSecond ? 1 : 0}"
            />
            <v-img
              :src="textBubble2"
              class="absolute right text-bubble three"
              :style="{bottom: `${100 + bottomBase}px`, opacity: showThird ? 1 : 0}"
            />
            <v-img
              :src="textBubble4"
              class="absolute left text-bubble four mb-1"
              :style="{bottom: `${50 + bottomBase}px`, opacity: showFourth ? 1 : 0}"
            />
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>

  </div>
</template>

<script setup lang="ts">
import iphoneOutline from "assets/public-site/iphoneOutline.png"
import textBubble1 from "assets/public-site/texting-bubbles/text-bubble1.png"
import textBubble2 from "assets/public-site/texting-bubbles/text-bubble2.png"
import textBubble3 from "assets/public-site/texting-bubbles/text-bubble3.png"
import textBubble4 from "assets/public-site/texting-bubbles/text-bubble4.png"
import {onMounted, onUnmounted, ref} from "vue";
// Imports

// Data
const bottomBase = ref(-150)
const showFirst = ref(false)
const showSecond = ref(false)
const showThird = ref(false)
const showFourth = ref(false)

// Lifecycle
onMounted(() => {
  runAnimation()
})

// Methods
const runAnimation = () => {
  setTimeout(() => {
    bottomBase.value += 50
    showFirst.value = true
  }, 1000)

  setTimeout(() => {
    bottomBase.value += 50
    showSecond.value = true
  }, 2000)

  setTimeout(() => {
    bottomBase.value += 50
    showThird.value = true
  }, 3000)

  setTimeout(() => {
    bottomBase.value += 50
    showFourth.value = true
  }, 4000)
}
// Hooks
</script>

<style scoped lang="stylus">
.text-bubble
  width: 120px;
  opacity 0;

.text-bubble.one, .text-bubble.three {
  right: 24px
}

.text-bubble.two, .text-bubble.four {
  left: 24px;
}

/* Apply a general style to all text bubbles */
.text-bubble {
  position: absolute;
  transition: all 1s; /* Adjust this to make the animation faster or slower */
}

</style>
