<template>
  <v-text-field
    :value="local_value"
    @input="set_local_value($event.target.value)"
    data-input="phone"
    outlined
    :placeholder="placeholder || 'Phone number'"
    :label="label"
    :error="!!error"
    :error-messages="error"
  >
    <template #prepend-inner>
      +1
    </template>
  </v-text-field>
</template>

<script>
import { ref, watch } from "vue";

export default {
  props: {
    value: String,
    placeholder: String,
    label: String,
    error: String,
  },
  setup(props, { emit }) {
    const local_value = ref('');

    const set_local_value = (incoming_value, bypass) => {
      if (incoming_value === local_value.value && !bypass) return;

      let new_val = incoming_value;
      if (new_val + ')' === local_value.value) {
        new_val = new_val.slice(0, -1);
      }
      const cleaned = clean(new_val); // remove anything but digits

      if (is_number(cleaned)) { // check for number validity
        const formatted = format(cleaned); // format phone number (xxx) xxx - xxxx
        let formatted_value = formatted;
        if (formatted === '()') {
          formatted_value = ''; // reset to empty str if no numbers
        }
        local_value.value = formatted_value;
      }

      const element = document.querySelector("[data-input='phone']");
      if (element) {
        // faking event input to update input's value
        element.value = local_value.value;
        element.dispatchEvent(new Event('input'));
      }
    };

    const is_number = (str) => {
      if (!str) return true;
      if (typeof str != "string") return false; // we only process strings!
      return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
        !isNaN(parseFloat(str)); // ...and ensure strings of whitespace fail
    };

    const format = (number) => {
      const area_code = number.substring(0, 3);
      const first_three = number.substring(3, 6);
      const last_four = number.substring(6, 10);
      // Number format is determined here
      return `(${area_code})${first_three ? ` ${first_three}` : ''}${last_four ? ` - ${last_four}` : ''}`;
    };

    const clean = (val = '') => {
      if (!val) return '';
      return val.slice()
        .trim()
        .replace(/ /g, '') //remove whitespace
        .replace(/\(|\)|-|/g, ''); //remove characters
    };

    watch(() => props.value, (newVal) => {
      if (local_value.value !== newVal) {
        local_value.value = newVal;
        set_local_value(newVal, true);
      }
    }, { immediate: true });

    watch(local_value, (newVal) => {
      const cleaned = clean(newVal);
      if (cleaned !== props.value) {
        emit('input', cleaned);
      }
    });

    return { local_value, set_local_value };
  },
};
</script>

<style scoped lang="stylus">
</style>
