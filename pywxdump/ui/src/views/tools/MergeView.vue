<script setup lang="ts">
import {ref} from "vue";
import http from '@/utils/axios.js';

const dbPath = ref<string>('');
const outPath = ref<string>('');
const Result = ref<string>('');

const decrypt = async () => {
  try {
    Result.value = await http.post('/api/ls/merge', {
      dbPath: dbPath.value,
      outPath: outPath.value
    });
  } catch (error) {
    Result.value = 'Error fetching data: \n' + error;
    console.error('Error fetching data:', error);
    return [];
  }

};
</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: grid; place-items: center; ">
    <div style="background-color: #fff; width: 70%; height: 70%; border-radius: 10px; padding: 20px; overflow: auto;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 20px; font-weight: bold;">合并-微信数据库</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <!--          <el-button style="margin-right: 10px;" @click="exportData">导出</el-button>-->
        </div>
      </div>
      <div style="margin-top: 20px;">
        <label>数据库路径: </label>
        <el-input placeholder="数据库路径（文件夹，并且确保文件夹下的db文件已经解密）：" v-model="dbPath" style="width: 80%;"></el-input>
        <br>
        <label>微信数据库路径: </label>
        <el-input placeholder="输出合并后的数据库路径" v-model="outPath" style="width: 80%;"></el-input>
        <br>
        <el-button style="margin-top: 10px;width: 50%;" type="success" @click="decrypt">合并</el-button>
        <!--    分割线    -->
        <el-divider></el-divider>
        <!--    分割线    -->
        <el-input type="textarea" :rows="10" readonly placeholder="合并后数据库路径" v-model="Result"
                  style="width: 100%;"></el-input>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>