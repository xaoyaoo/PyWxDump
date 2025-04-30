<script setup lang="ts">
import {defineEmits, defineProps, nextTick, onMounted, ref, watch} from 'vue';
import http from "@/utils/axios.js";
import {ElTable, ElNotification, ElMessage, ElMessageBox} from "element-plus";
import {apiMsgCount, apiMsgCountSolo, apiRealTime, apiUserList} from "@/api/chat";
import {gen_show_name, type User} from "@/utils/common_utils";
import UserInfoShow from "@/components/chat/components/UserInfoShow.vue";

const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});

const msg_count = ref<number>(0);
const userinfo = ref<User>({
  wxid: '',
  nOrder: 0,
  nUnReadCount: 0,
  strNickName: '',
  nStatus: 0,
  nIsSend: 0,
  strContent: '',
  nMsgLocalID: 0,
  nMsgStatus: 0,
  nTime: '',
  nMsgType: 0,
  nMsgSubType: 0,
  nickname: '',
  remark: '',
  account: '',
  describe: '',
  headImgUrl: '',
  ExtraBuf: {
    "个性签名": "",
    "企微属性": "",
    "公司名称": "",
    "国": "",
    "备注图片": "",
    "备注图片2": "",
    "市": "",
    "性别[1男2女]": 0,
    "手机号": "",
    "朋友圈背景": "",
    "省": ""
  },
  LabelIDList: [],
  extra: null
});

// 请求数据，赋值 START
const req_user_info = async () => {
  // 请求数据 用户信息
  try {
    const body_data = await apiUserList("", [props.wxid]);
    userinfo.value.wxid = props.wxid;
    userinfo.value.remark = body_data[props.wxid]?.remark;
    userinfo.value.account = body_data[props.wxid]?.account;
    userinfo.value.describe = body_data[props.wxid]?.describe;
    userinfo.value.headImgUrl = body_data[props.wxid]?.headImgUrl;
    userinfo.value.nickname = body_data[props.wxid]?.nickname;
    userinfo.value.LabelIDList = body_data[props.wxid]?.LabelIDList;
    userinfo.value.ExtraBuf = body_data[props.wxid]?.ExtraBuf;
    userinfo.value.extra = body_data[props.wxid]?.extra;
    return body_data;
  } catch (error) {
    console.error('Error fetching data wxid2user :', error);
    return [];
  }
}

const req_msg_count = async () => {
  try {
    msg_count.value = 0;
    const body_data = await apiMsgCountSolo(props.wxid);
    msg_count.value = body_data || 0;
    return body_data;
  } catch (error) {
    console.error('Error fetching data msg_count:', error);
    return [];
  }
}
// 请求数据，赋值 END

// 初始调用函数 START
const init = () => {
  is_export.value = false;
  req_user_info();
  req_msg_count();
}
onMounted(() => {
  console.log('ChatRecprdsHeader onMounted', props.wxid)
  init();
});
watch(() => props.wxid, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    init();
  }
});
// 初始调用函数 END

// 弹窗展示更多信息 START
const is_show_more = ref(false);
// 获取实时消息 START

const is_getting_real_time_msg = ref(false);
const get_real_time_msg = async () => {
  if (is_getting_real_time_msg.value) {
    console.log("正在获取实时消息，请稍后再试!")
    return;
  }
  is_getting_real_time_msg.value = true;
  try {
    const body_data = await apiRealTime();
    is_getting_real_time_msg.value = false;
    return body_data;
  } catch (error) {
    is_getting_real_time_msg.value = false;
    return [];
  }
}
// 获取实时消息 END

// 导出消息按钮，并传递是否导出给父组件 START
const is_export = ref(false);
const emits = defineEmits(['exporting']);
const export_button = (val: boolean) => {
// 提交参数 is_export 给父组件
  emits('exporting', val);
  is_export.value = val;
}
// 导出消息按钮，并传递是否导出给父组件 END


</script>

<template>

  <el-row :gutter="5" style="width: 100%;">
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>wxid:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userinfo?.wxid">{{ userinfo?.wxid }}</el-text>
    </el-col>
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>名称:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated title="show_name">{{ gen_show_name(userinfo) }}</el-text>
    </el-col>
    <el-col :span="5" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>数量:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="msg_count">{{ msg_count }}</el-text>
    </el-col>
    <el-col :span="2" style="white-space: nowrap;">
      <el-text class="button_color mx-1 underline" truncated @click="is_show_more=!is_show_more"> 详细信息</el-text>
    </el-col>
    <el-col :span="2" style="white-space: nowrap;">
      <el-text v-if="!is_export" class="button_color mx-1 underline" truncated @click="export_button(true);">导出备份
      </el-text>
      <el-text v-if="is_export" class="button_color mx-1 underline" truncated @click="export_button(false);">聊天查看
      </el-text>
    </el-col>
    <el-col :span="3" style="white-space: nowrap;">
      <el-text class="button_color mx-1 underline" truncated @click="get_real_time_msg();">实时消息
        <template v-if="is_getting_real_time_msg" style="color: #00bd7e">...</template>
      </el-text>
    </el-col>
  </el-row>

  <el-dialog v-model="is_show_more" title="详细信息" width="600" center>
    <user-info-show :userinfo="userinfo" :show_all="true"></user-info-show>
  </el-dialog>
</template>

<style scoped>
.label_color {
  color: #333; /* 调整字体颜色 */
  font-size: 15px;
  padding-left: 15px;
  padding-right: 0;
}

.data_color {
  color: #08488c;
  background-color: #f4f4f4; /* 调整背景颜色 */
  font-size: 15px;
  padding-left: 6px;
  padding-right: 6px;
  font-weight: bold; /* 使用 bold 表示加粗 */
  white-space: nowrap;
  max-width: 80%;
}

.button_color {
  color: #0048ff; /* 调整字体颜色 */
  font-size: 15px;
  padding-left: 15px;
  padding-right: 0;
  text-decoration: underline;
}

</style>