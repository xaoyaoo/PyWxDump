<script setup lang="ts">
import {ref} from "vue";

const color = ref('');
const updateColors = (val: string) => {
  emit('updateColors', val);
}

const emit = defineEmits(['updateColors']);

</script>

<template>
    <el-color-picker v-model="color" @change="updateColors" size="small"></el-color-picker>
</template>

<style scoped>

</style>