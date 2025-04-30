<template>
  <div class="about">
    <h1 id="-center-pywxdump-center-" style="text-align: center">
      PyWxDump<a @click="check_update" target="_blank" style="float: right; margin-right: 30px;">检查更新</a>
    </h1>
    <!--  在右上角添加按钮， “检查更新”  -->

    <Markdown :source="source" style="background-color: #d2d2fa;"/>
  </div>
</template>

<script setup lang="ts">
import Markdown from 'vue3-markdown-it';
import http from '@/utils/axios.js';
import {type Action, ElMessage, ElMessageBox} from "element-plus";
import {onMounted, ref} from "vue";

const check_update = async () => {
  try {

    const body_data = await http.post('/api/rs/check_update');
    const latest_version = body_data.latest_version;
    const msg = body_data.msg;
    const url = body_data.latest_url;
    const showtext = `${msg}：${latest_version} \n ${url || ''}`;

    ElMessageBox.alert(showtext, 'info', {
      confirmButtonText: '确认',
      callback: (action: Action) => {
        ElMessage({
          type: 'info',
          message: `action: ${action}`,
        })
      },
    })
  } catch (error) {
    // console.error('Error fetching data:', error);
    return [];
  }
}

const source = ref("# 加载中")

const get_readme_md = async () => {
  try {

    const body_data = await http.post('/api/rs/get_readme');
    source.value = body_data;
  } catch (error) {
    // console.error('Error fetching data:', error);
    return [];
  }
}

onMounted(() => {
  get_readme_md()
})


</script>

<style>
.about {
  background-color: #d2d2fa;
  height: 100%;
}
</style>