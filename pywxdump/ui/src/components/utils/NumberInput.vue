<script setup lang="ts">
import {ref} from "vue";

const props = defineProps<{
  n: Number,
  step: Number
}>();

const value = ref(props.n);

const updateNumber = (val: bigint) => {
  emit('updateNumber', val);
}
const emit = defineEmits(['updateNumber']);

</script>

<template>
  <el-input-number v-model="value" @change="updateNumber" size="small" :step="step"
                   style="width: 100px;"></el-input-number>
</template>

<style scoped>

</style>