<script setup lang="ts">
import ChatRecprdsHeader from '@/components/chat/ChatRecprdsHeader.vue';
import ChatRecordsMain from '@/components/chat/ChatRecordsMain.vue';
import {ref, defineProps, nextTick, onMounted, watch} from 'vue';
import http from "@/utils/axios.js";
import ChatExportMain from "@/components/chatBackup/ChatExportMain.vue";
import {apiMsgCount} from "@/api/chat";


const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});

// 导出聊天记录页面是否显示
const is_export = ref(false);
const onExport = (exporting: boolean) => {
  is_export.value = exporting;
}
// end 导出聊天记录页面是否显示

// start 监测wxid变化，初始化数据
const init = () => {
  is_export.value = false;
}
watch(() => props.wxid, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    init();
  }
});
onMounted(() => {
  init();
});
// end 监测wxid变化，初始化数据
</script>

<template>
  <el-container>
    <el-header style="height: 40px; max-height: 40px; width: 100%;background-color: #d2d2fa;padding-top: 5px;">
      <ChatRecprdsHeader :wxid="wxid" @exporting="onExport"/>
    </el-header>
    <el-main style="height: calc(100vh - 40px);padding: 0;margin: 0;background-color: #f5f5f5;">
        <ChatExportMain v-if="is_export" :wxid="wxid"/>
        <ChatRecordsMain v-else :wxid="wxid"/>
        
    </el-main>
  </el-container>
</template>

<style scoped>

</style>
