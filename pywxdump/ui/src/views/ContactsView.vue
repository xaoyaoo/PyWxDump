<script setup lang="ts">
import http from '@/utils/axios.js';
import {onMounted, ref} from "vue";
import {apiVersion} from "@/api/base";

const version = ref(''); // 用于显示返回值

const getVersion = () => {
  apiVersion().then((data: string) => {
    version.value = data;
  }).catch((error: string) => {
    console.error('Error fetching API version:', error);
  });
}
onMounted(getVersion);

</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: grid; place-items: center; ">
    <h2 style="text-align: center">欢迎使用<a href="https://github.com/xaoyaoo/PyWxDump.git">PyWxDump</a>聊天记录查看工具!
      <p style="text-align: center">当前版本：{{ version }}</p>
    </h2>
  </div>
</template>

<style scoped>

</style>