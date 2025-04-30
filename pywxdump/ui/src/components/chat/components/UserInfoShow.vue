<script setup lang="ts">

import {api_img} from "@/api/base";

const props = defineProps({
  userinfo: {
    type: Object,
    default: () => {
      return {}
    }
  },
  show_all: {
    type: Boolean,
    default: true,
    required: false
  }
})
const tableRowClassName = ({
                             row,
                             rowIndex,
                           }: {
  row: any
  rowIndex: number
}) => {
  console.log(row.wxid, props.userinfo.extra.owner.wxid, row.wxid == props.userinfo.extra.owner.wxid)
  if (row.wxid == props.userinfo.extra.owner.wxid) {
    console.log("table-success-row")
    return 'table-success-row'
  }
  return ''
}

</script>

<template>
  <div v-if="show_all" style="max-width: 560px">
    <!--  用于详细信息里面的更多信息显示  -->
    <div>
      <el-divider content-position="center">基本信息</el-divider>
      <span>wxid：{{ userinfo.wxid }}<br></span>
      <span>账号：{{ userinfo.account }}<br></span>
      <span>昵称：{{ userinfo.nickname }}<br></span>
      <span>备注：{{ userinfo.remark }}<br></span>
    </div>
    <div>
      <el-divider content-position="center">账号信息</el-divider>
      <span>性别：{{
          userinfo.ExtraBuf['性别[1男2女]'] == 1 ? '男' : userinfo.ExtraBuf['性别[1男2女]'] == 2 ? '女' : ''
        }}<br></span>
      <span>手机：{{ userinfo.ExtraBuf['手机号'] }}<br></span>
      <span>标签：{{ userinfo.LabelIDList.join('/') }}<br></span>
      <span>描述：{{ userinfo.describe }}<br></span>
      <span>个签：{{ userinfo.ExtraBuf['个性签名'] }}<br></span>
      <span>国家：{{ userinfo.ExtraBuf['国'] }}<br></span>
      <span>省份：{{ userinfo.ExtraBuf['省'] }}<br></span>
      <span>市名：{{ userinfo.ExtraBuf['市'] }}<br></span>
    </div>
    <div>
      <el-divider content-position="center">其他信息</el-divider>
      <span>公司：{{ userinfo.ExtraBuf['公司名称'] }}<br></span>
      <span>企微：{{ userinfo.ExtraBuf['企微属性'] }}<br></span>
      <span>朋友圈背景：<br></span>
      <el-image v-if="userinfo.ExtraBuf['朋友圈背景']" :src="api_img(userinfo.ExtraBuf['朋友圈背景'])" alt="朋友圈背景"
                style="max-width: 200px;max-height: 200px"
                :preview-src-list="[api_img(userinfo.ExtraBuf['朋友圈背景'])]" :hide-on-click-modal="true"/>
    </div>
    <div v-if="userinfo.extra">
      <el-divider content-position="center">群聊信息</el-divider>
      <span>群主: {{ userinfo.extra.owner.wxid }}<br></span>
      <span>群成员：<br></span>
      <el-table :data="Object.values(userinfo.extra.wxid2userinfo)" style="width: 100%"
                :row-class-name="tableRowClassName">
        <el-table-column prop="wxid" label="wxid"/>
        <el-table-column prop="account" label="账号"/>
        <el-table-column prop="nickname" label="昵称"/>
        <el-table-column prop="remark" label="备注"/>
        <el-table-column prop="roomNickname" label="群昵称"/>
      </el-table>
    </div>
  </div>
  <div v-else style="max-width: 560px">
    <span>wxid：{{ userinfo.wxid }}<br></span>
    <span>账号：{{ userinfo.account }}<br></span>
    <span>昵称：{{ userinfo.nickname }}<br></span>
    <span v-if="userinfo.remark">备注：{{ userinfo.remark }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['性别[1男2女]']">性别：{{
        userinfo.ExtraBuf['性别[1男2女]'] == 1 ? '男' : userinfo.ExtraBuf['性别[1男2女]'] == 2 ? '女' : ''
      }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['手机号']">手机：{{ userinfo.ExtraBuf['手机号'] }}<br></span>
    <span v-if="userinfo.LabelIDList&&userinfo.LabelIDList.length>0">标签：{{
        userinfo.LabelIDList.join('/')
      }}<br></span>
    <span v-if="userinfo.describe">描述：{{ userinfo.describe }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['个性签名']">个签：{{ userinfo.ExtraBuf['个性签名'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['国']">国家：{{ userinfo.ExtraBuf['国'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['省']">省份：{{ userinfo.ExtraBuf['省'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['市']">市名：{{ userinfo.ExtraBuf['市'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['公司名称']">公司：{{ userinfo.ExtraBuf['公司名称'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['企微属性']">企微：{{ userinfo.ExtraBuf['企微属性'] }}<br></span>
    <span v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['朋友圈背景']">朋友圈背景：<br></span>
    <el-image v-if="userinfo.ExtraBuf && userinfo.ExtraBuf['朋友圈背景']"
              :src="api_img(userinfo.ExtraBuf['朋友圈背景'])"
              style="max-width: 200px;max-height: 200px" alt="朋友圈背景"/>
  </div>
</template>

<style scoped>
.table-success-row {
  --el-table-tr-bg-color: var(--el-color-success-light-9);
}
</style>