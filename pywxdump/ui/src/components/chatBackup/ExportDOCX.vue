<script setup lang="ts">

import {defineProps, watch} from "vue";

const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});

watch(() => props.wxid, (newVal: string, oldVal: String) => {
  console.log(newVal);
});

const requestExport = () => {
  console.log('requestExport');
}

</script>

<template>
  <div>
    <span>{{props.wxid}}</span><br>
    <el-button type="primary" @click="requestExport()">导出</el-button>
  </div>
</template>

<style scoped>

</style>