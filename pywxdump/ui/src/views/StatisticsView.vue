<script setup lang="ts">
import DateChatStats from "@/components/stats/DateChatStats.vue";
import {ref} from "vue";
import ContactStats from "@/components/stats/ContactStats.vue";
import DateChatHeatmapStats from "@/components/stats/DateChatHeatmapStats.vue";

const mene_selected = ref("date_chat_heatmap");
</script>

<template>
  <!--    <h2 style="text-align: center">欢迎使用<a href="https://github.com/xaoyaoo/PyWxDump.git">PyWxDump</a>聊天记录查看工具!-->
  <!--    </h2>-->
  <!--    <h3 style="text-align: center">-->
  <!--      用于统计微信聊天记录，包括聊天记录数量、聊天记录总字数、聊天记录总图片数量<br>聊天记录总视频数量、聊天记录总文件数量、聊天记录总语音数量等等。-->
  <!--      行成统计报表，方便用户查看自己的聊天记录情况-->
  <!--    </h3>-->
  <div class="common-layout" style="height: 100vh;width: 100%;background-color: #d2d2fa;">
    <el-container style="height: calc(100vh);width: 100%;">
      <el-aside width="120px" style="height: 100%;">
        <el-menu style="height: 100%;background-color: #F7F7F7;color:#262626;"
                 :default-active="mene_selected"
                 class="el-menu-vertical-demo"
                 @select="(val: string)=>{mene_selected = val}"
        >
          <el-menu-item index="date_chat_heatmap">
            <span>聊天热力图</span>
          </el-menu-item>
          <el-menu-item index="date_chat_count">
            <span>日聊天数据</span>
          </el-menu-item>
          <el-menu-item index="contact_stats">
            <span>联系人画像</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main style="height: 100%;width: 100%;margin: 0;padding: 0;">
        <date-chat-stats v-if="mene_selected=='date_chat_count'"/>
        <date-chat-heatmap-stats v-if="mene_selected=='date_chat_heatmap'"/>
        <contact-stats v-if="mene_selected=='contact_stats'"/>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>

</style>