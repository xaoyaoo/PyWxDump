<script setup lang="ts">

import {defineProps, ref, watch} from "vue";
import http from "@/utils/axios.js";
import DateTimeSelect from "@/components/utils/DateTimeSelect.vue";

const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});
watch(() => props.wxid, (newVal: string, oldVal: String) => {
  console.log(newVal);
});
// 上述代码是监听props.wxid的变化，当props.wxid变化时，会打印新值。

const datetime = ref([]);
const Result = ref("");

const requestExport = async () => {
  Result.value = "正在处理中...";
  try {
    Result.value = await http.post('/api/rs/export_html', {
      'wxid': props.wxid,
      // 'datetime': datetime.value,
    });
  } catch (error) {
    console.error('Error fetching data msg_count:', error);
    Result.value = "请求失败\n" + error;
    return [];
  }
}

// 处理时间选择器的数据
const handDatetimeChildData = (val: any) => {
  datetime.value = val;
}

</script>

<template>
  <div>
<!--    <div>-->
<!--      <strong>时间(默认全部)：</strong>-->
<!--      <DateTimeSelect @datetime="handDatetimeChildData"/>-->
<!--    </div>-->
    <span>使用说明：（1）根据 https://blog.csdn.net/meser88/article/details/130229417 进行设置</span><br/>
    <span>（2）打开导出的文件夹位置，使用（1）设置的浏览器打开 index.html 文件</span>
    <div style="position: relative;">
      <el-button type="primary" @click="requestExport()">导出</el-button>
    </div>
    <el-divider/>
    <!-- 结果显示   -->
    <el-input type="textarea" :rows="6" readonly placeholder="" v-model="Result"
              style="width: 100%;"></el-input>
  </div>
</template>

<style scoped>

</style>