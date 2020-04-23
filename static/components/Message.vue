<!--
An alert message using Django or Bootstrap message levels

props:
  variant: debug, info, success, warning or error

"debug" is mapped to Boostrap secondary color.
"error" is mapped to Boostrap danger color.
-->

<template>
  <b-alert
    :variant="variant"
    dismissible
    show
    fade
  >
    <slot></slot>
  </b-alert>
</template>

<!--
Many modern browsers implement an optimization for <style> tags either cloned
from a common node or that have identical text, to allow them to share a single
backing stylesheet. With this optimization the performance of external and
internal styles should be similar.
From https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_shadow_DOM

So it is not a problem to import all Boostrap here.
-->
<style lang="sass">
@import '~bootstrap'
@import '~bootstrap-vue'
</style>

<script>
import Vue from "vue";
import { BAlert } from "bootstrap-vue";
Vue.component("b-alert", BAlert);

export default {
  name: "Message",
  props: ["tags"],
  computed: {
    variant: function() {
      switch (this.tags) {
        case "error":
          return "danger";
        case "debug":
          return "secondary";
        default:
          return this.tags;
      }
    }
  }
};
</script>
