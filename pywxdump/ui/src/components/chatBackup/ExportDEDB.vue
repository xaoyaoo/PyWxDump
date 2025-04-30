<script setup lang="ts">

import {defineProps, ref, watch} from "vue";
import http from "@/utils/axios.js";

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

const wx_path = ref("");
const key = ref("");
const Result = ref("");

const requestExport = async () => {
  Result.value = "正在处理中...";
  try {
    Result.value = await http.post('/api/rs/export_dedb', {
      'key': key.value,
      'wx_path': wx_path.value,
    });
  } catch (error) {
    console.error('Error fetching data msg_count:', error);
    Result.value = "请求失败\n" + error;
    return [];
  }

}

</script>

<template>
  <div>
    密钥(可选)：
    <el-input placeholder="密钥[可为空,空表示使用默认的，无默认会报错]"
              v-model="key"
              style="width: 75%;"></el-input>
    <br><br>
    微信文件夹路径(可选)：
    <el-input placeholder="微信文件夹路径[可为空,空表示使用默认的，无默认会报错](eg: C:\****\WeChat Files\wxid_**** )"
              v-model="wx_path"
              style="width: 70%;"></el-input>
    <br><br>

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