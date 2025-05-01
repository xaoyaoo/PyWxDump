<script setup lang="ts">
import {ref, defineProps, nextTick, watch, type Ref} from 'vue';
import ChatRecprdsHeader from "@/components/chat/ChatRecprdsHeader.vue";
import DateTimeSelect from "@/components/utils/DateTimeSelect.vue";
import http from '@/utils/axios.js';
import {type Action, ElMessage, ElMessageBox} from "element-plus";
import ExportENDB from "@/components/chatBackup/ExportENDB.vue";
import ExportDEDB from "@/components/chatBackup/ExportDEDB.vue";
import ExportCSV from "@/components/chatBackup/ExportCSV.vue";
import ExportJSON from "@/components/chatBackup/ExportJSON.vue";
import ExportHTML from "@/components/chatBackup/ExportHTML.vue";
import ExportPDF from "@/components/chatBackup/ExportPDF.vue";
import ExportDOCX from "@/components/chatBackup/ExportDOCX.vue";
import ExportJSONMini from './ExportJSONMini.vue';

const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});

watch(() => props.wxid, (newVal: string, oldVal: String) => {
  console.log(newVal);
});

const exportType: Ref<string> = ref(''); // 导出类型
const result = ref(''); // 用于显示返回值


const setting = {
  'endb': {
    brief: '加密文件',
    detail: "导出的内容为微信加密数据库。可还原回微信,但会覆盖微信后续消息。(全程不解密，所以数据安全)",
  },
  'dedb': {
    brief: '解密文件',
    detail: "导出的文件为解密后的sqlite数据库，并且会自动合并msg和media数据库为同一个，但是无法还原回微信。",
  },
  'csv': {
    brief: 'csv',
    detail: "只包含文本，但是可以用excel软件（wps，office）打开。",
  },
  'json': {
    brief: 'json',
    detail: "只包含文本，可用于数据分析，情感分析等方面。",
  },
  'json-mini': {
    brief: 'json-mini',
    detail: "只包含文本，只有最小化的json格式。支持选择时间，注意不要选择太多时间，会导致导出数据过大影响AI分析。",
  },
  'html': {
    brief: 'html-测试中',
    detail: "主要用于浏览器可视化查看。",
  },
  'pdf': {
    brief: 'pdf-开发中',
    detail: "pdf版本。",
  },
  'docx': {
    brief: 'docx-开发中',
    detail: "docx版本。",
  },
};

</script>

<template>
  <div id="chat_export" style="background-color: #d2d2fa;padding:0;">

    <!--      分割线 -->
    <el-main style="overflow-y: auto; height: calc(100vh - 65px);padding: 0">
      <div style="background-color: #d2d2fa;height: calc(100vh - 65px); display: grid; place-items: center; ">
        <div
            style="background-color: #fff; width: 70%; height: 70%; border-radius: 10px; padding: 20px; overflow: auto;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 20px; font-weight: bold;">导出与备份(未完待续...）</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <!--          <el-button style="margin-right: 10px;" @click="exportData">导出</el-button>-->
            </div>
          </div>
          <div style="margin-top: 20px;">
            导出类型:
            <el-select placeholder="请选择导出类型" style="width: 50%;" v-model="exportType">
              <el-option :label="value.brief" :value="index" v-for="(value,index) in setting" :key="index">
                {{ value.brief }}
              </el-option>
            </el-select>
            <br/><br/>
            <span v-if="exportType">
              {{ setting[exportType].detail }}
            </span>
          </div>
          <el-divider/>
          <ExportENDB v-if="exportType=='endb'" :wxid="props.wxid"/>
          <ExportDEDB v-if="exportType=='dedb'" :wxid="props.wxid"/>
          <ExportCSV v-if="exportType=='csv'" :wxid="props.wxid"/>
          <ExportJSON v-if="exportType=='json'" :wxid="props.wxid"/>
          <ExportJSONMini v-if="exportType=='json-mini'" :wxid="props.wxid"/>
          <ExportHTML v-if="exportType=='html'" :wxid="props.wxid"/>
          <ExportPDF v-if="exportType=='pdf'" :wxid="props.wxid"/>
          <ExportDOCX v-if="exportType=='docx'" :wxid="props.wxid"/>
        </div>
      </div>
    </el-main>
  </div>
</template>

<style scoped>

</style>