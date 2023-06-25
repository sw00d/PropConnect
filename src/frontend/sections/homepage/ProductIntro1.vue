<template>
  <div class="bg-primary text-white">
    <div class="content-container d-flex justify-space-between align-center py-10">
      <v-row>
        <v-col>
          <div class="d-flex flex-column justify-center h-100">
            <div class="font-weight-bold font-40">
              Streamlining Tenant Communication
            </div>
            <div class="font-weight-medium opacity-7 font-24 mt-11">
              Take a step back from the constant juggle between tenants, vendors, and landlords. Our solution brings
              efficiency
              to your role by facilitating direct communication between tenant and vendor. With in depth oversight,
              you're
              free
              from mundane tasks, empowering you to focus on expanding your portfolio or simply enjoying your
              well-deserved
              downtime.
            </div>
          </div>
        </v-col>
        <v-col cols="3" class="d-flex justify-end">
          <v-sheet height="415px" width="225px" class="bg-transparent relative">
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
    </div>

  </div>
</template>

<script setup lang="ts">
import AOS from 'aos'
import 'aos/dist/aos.css'

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
  AOS.init({
    startEvent: 'DOMContentLoaded', // name of the event dispatched on the document, that AOS should initialize on
    initClassName: false, // class applied after initialization
    animatedClassName: 'aos-animate', // class applied on animation
    useClassNames: false, // if true, will add content of `data-aos` as classes on scroll
  });

  document.addEventListener('aos:in', ({detail}) => {
    console.log('animated element:', detail);
    if (detail.getAttribute('data-aos-id') === 'myElement') {
      // Call your function here
      alert('firing')

    }
  });

  onUnmounted(() => {
    document.removeEventListener('aos:in', runAnimation);
  })

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

//
//
///* Keyframes for the "scroll-up" animation for the first bubble */
//@keyframes scrollUpOne {
//  0%, 20% { /* Keep at bottom for the first 20% of the time */
//    bottom: 0;
//    opacity: 0;
//  }
//  20%, 40% { /* Move up to 50px and fade in between 20% and 40% of the time */
//    bottom: 50px;
//    opacity: 1;
//  }
//  60%, 80% { /* Move up to 100px between 60% and 80% of the time */
//    bottom: 100px;
//  }
//  100% { /* Move up to 150px at the end of the time */
//    bottom: 150px;
//  }
//}
//
///* Keyframes for the "scroll-up" animation for the second bubble */
//@keyframes scrollUpTwo {
//  0%, 40% { /* Keep at bottom and hidden for the first 40% of the time */
//    bottom: 0;
//    opacity: 0;
//  }
//  40%, 60% { /* Move up to 50px and fade in between 40% and 60% of the time */
//    bottom: 50px;
//    opacity: 1;
//  }
//  80%, 100% { /* Move up to 100px between 80% and 100% of the time */
//    bottom: 100px;
//  }
//}
//
///* Keyframes for the "scroll-up" animation for the third bubble */
//@keyframes scrollUpThree {
//  0%, 80% { /* Keep at bottom and hidden for the first 80% of the time */
//    bottom: 0px;
//    opacity: 0;
//  }
//  80%, 100% { /* Move up to 50px and fade in between 80% and 100% of the time */
//    bottom: 50px;
//    opacity: 1;
//  }
//}
//
///* Apply the animations to the text bubbles */
//.text-bubble.one {
//  animation: scrollUpOne 10s ease-in-out forwards; /* Total animation time is 10 seconds */
//}
//
//.text-bubble.two {
//  animation: scrollUpTwo 10s ease-in-out forwards; /* Total animation time is 10 seconds */
//}
//
//.text-bubble.three {
//  animation: scrollUpThree 10s ease-in-out forwards; /* Total animation time is 10 seconds */
//}


</style>
