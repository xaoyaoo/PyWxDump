<script setup lang="ts">
import {ref} from "vue";
import http from '@/utils/axios.js';

const mobile = ref<string>('');
const name = ref<string>('');
const account = ref<string>('');
const key = ref<string>('');
const wxdbPath = ref<string>('');

const result = ref<string>(''); // 结果

const decrypt = async () => {
  try {
    // key与wxdbPath二选一
    if (key.value === '' && wxdbPath.value === '') {
      result.value = 'key与wxdbPath必须填写一个';
      return;
    }
    result.value = await http.post('/api/ls/biasaddr', {
      mobile: mobile.value,
      name: name.value,
      account: account.value,
      key: key.value,
      wxdbPath: wxdbPath.value
    });
    result.value = "{版本号:昵称,账号,手机号,邮箱,KEY}\n"+result.value;
  } catch (error) {
    result.value = 'Error fetching data: \n' + error;
    console.error('Error fetching data:', error);
    return [];
  }

};
</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: grid; place-items: center; ">
    <div style="background-color: #fff; width: 70%; height: 70%; border-radius: 10px; padding: 20px; overflow: auto;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 20px; font-weight: bold;">基址偏移</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <!--          <el-button style="margin-right: 10px;" @click="exportData">导出</el-button>-->
        </div>
      </div>
      <div style="margin-top: 20px;">
        <label>手机号: </label>
        <el-input placeholder="请输入手机号" v-model="mobile" style="width: 80%;"></el-input>
        <br>
        <label>昵称: </label>
        <el-input placeholder="请输入昵称" v-model="name" style="width: 80%;"></el-input>
        <br>
        <label>微信账号: </label>
        <el-input placeholder="请输入微信号" v-model="account" style="width: 80%;"></el-input>
        <br>
        <label>密钥（key）: </label>
        <el-input placeholder="请输入密钥（key）（可选）" v-model="key" style="width: 80%;"></el-input>
        <br>
        <label>微信数据库路径: </label>
        <el-input placeholder="请输入微信数据库路径（可选）" v-model="wxdbPath" style="width: 75%;"></el-input>
        <br>
        <el-button style="margin-top: 10px;width: 50%;" type="success" @click="decrypt">偏移</el-button>
        <!--    分割线    -->
        <el-divider></el-divider>
        <!--    分割线    -->
        <el-input type="textarea" :rows="10" readonly placeholder="输出结果" v-model="result"
                  style="width: 100%;color: #00bd7e;"></el-input>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>