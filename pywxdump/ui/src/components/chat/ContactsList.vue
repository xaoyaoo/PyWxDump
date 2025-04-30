<script setup lang="ts">
import {defineEmits, onMounted, ref} from 'vue';
import http from '@/utils/axios.js';
import {apiUserList, apiUserSessionList} from "@/api/chat";
import UserInfoShow from "@/components/chat/components/UserInfoShow.vue";
import {gen_show_name, type User} from "@/utils/common_utils";
import {api_img} from "@/api/base";

// "wxid": strUsrName, "nOrder": nOrder, "nUnReadCount": nUnReadCount, "strNickName": strNickName,
// "nStatus": nStatus, "nIsSend": nIsSend, "strContent": strContent, "nMsgLocalID": nMsgLocalID,
// "nMsgStatus": nMsgStatus, "nTime": nTime, "nMsgType": nMsgType, "nMsgSubType": nMsgSubType,
// "nickname": NickName, "remark": Remark, "account": Alias,
// "describe": describe, "headImgUrl": bigHeadImgUrl if bigHeadImgUrl else "",
// "ExtraBuf": ExtraBuf, "LabelIDList": tuple(LabelIDList)


const tableData = ref([]);


// 初始化请求session数据 START
const fetchData = async () => {
  try {
    tableData.value = await apiUserSessionList();
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
};
onMounted(fetchData);
// END 初始化请求session数据 END

// 搜索框以及按钮 START
const search_word = ref('');
const search = async () => {
  try {
    // console.log(body_data);
    if (search_word.value === '') {
      tableData.value = await apiUserSessionList();
      return;
    }
    console.log(search_word.value);
    tableData.value = []
    const ret = await apiUserList(search_word.value);
    if (ret !== null && typeof ret === 'object') {
      Object.entries(ret).forEach(([key, value]) => {
        tableData.value.push(value);
      });
    }
    // for (const key in ret) {
    //   if (ret.hasOwnProperty(key)) {
    //     tableData.value.push(ret[key]);
    //   }
    // }
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}
// END 搜索框以及按钮 END

// 处理user数据 传递给父组件 START
const emits = defineEmits(['wxid']);

const handleCurrentChange = (val: User | undefined) => {
  // 触发自定义事件，并传递数据
  if (val !== undefined) {
    // 处理user数据
    // 判断val是否有wxid
    if (val.wxid !== undefined) {
      console.log('wxid:', val.wxid);
      emits('wxid', val.wxid);
    }
  }
}
// END 处理user数据 传递给父组件 END


// 生成显示的name


</script>

<template>
  <div>
    <!-- 搜索框以及按钮   -->
    <div style="padding: 10px 10px;">
      <el-input placeholder="请输入关键字" v-model="search_word" @keyup.enter="search"
                style="width: 170px;margin-left: 15px;"></el-input>
      <el-button type="primary" @click="search" style="width: 50px;">搜索</el-button>
    </div>
    <!--  这是联系人的list    -->
    <el-table :data="tableData" stripe style="width: 100%" max-height="100%" height="100%" highlight-current-row loading="lazy"
              @current-change="handleCurrentChange">
      <el-table-column width="57">
        <template v-slot="{ row }">
          <el-avatar :size="33" :src="api_img(row.headImgUrl)" v-if="row.headImgUrl!==''"></el-avatar>
          <el-avatar :size="33" v-else>群</el-avatar>
        </template>
      </el-table-column>
      <el-table-column width="190">
        <template v-slot="{ row }">
          <el-tooltip class="item" effect="light" placement="right">
            <div slot="content" class="tips">
              <span>{{ gen_show_name(row) }}</span> <br>
              <span v-if="row.nTime" style="color: #909399; font-size: 12px;">{{ row.nTime }}</span>
            </div>
            <template #content>
              <user-info-show :userinfo="row" :show_all="false" style="max-width: 600px"></user-info-show>
            </template>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
/* 允许提示内容换行 */
.el-tooltip__popper .popper__content {
  white-space: pre-line; /* 允许换行 */
}
</style>