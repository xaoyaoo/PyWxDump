<script setup lang="ts">
import {ref} from "vue";
import http from '@/utils/axios.js';

const wxdbPath = ref<string>('');
const key = ref<string>('');
const outPath = ref<string>('');
const decryptResult = ref<string>('');

const decrypt = async () => {
  try {
    decryptResult.value = await http.post('/api/ls/decrypt', {
      wxdbPath: wxdbPath.value,
      key: key.value,
      outPath: outPath.value
    });
  } catch (error) {
    decryptResult.value = 'Error fetching data: \n' + error;
    console.error('Error fetching data:', error);
    return [];
  }

};

</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: grid; place-items: center; ">
    <div style="background-color: #fff; width: 70%; height: 70%; border-radius: 10px; padding: 20px; overflow: auto;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 20px; font-weight: bold;">解密-微信数据库</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <!--          <el-button style="margin-right: 10px;" @click="exportData">导出</el-button>-->
        </div>
      </div>
      <div style="margin-top: 20px;">
        <label>密钥（key）: </label>
        <el-input placeholder="请输入密钥（key）" v-model="key" style="width: 82%;"></el-input>
        <br>
        <label>微信数据库路径: </label>
        <el-input placeholder="请输入微信数据库路径" v-model="wxdbPath" style="width: 80%;"></el-input>
        <br>
        <label>解密后输出文件夹路径: </label>
        <el-input placeholder="请输入解密后输出文件夹路径" v-model="outPath" style="width: 75%;"></el-input>
        <br>

        <el-button style="margin-top: 10px;width: 50%;" type="success" @click="decrypt">解密</el-button>
        <!--    分割线    -->
        <el-divider></el-divider>
        <!--    分割线    -->
        <el-input type="textarea" :rows="10" readonly placeholder="解密后数据库路径" v-model="decryptResult"
                  style="width: 100%;"></el-input>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>