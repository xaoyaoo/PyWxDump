<script setup lang="ts">
import DbInitView from "@/views/DbInitView.vue";
import {ref} from "vue";
import DbInitComponent from "@/components/utils/DbInitComponent.vue";

const setting_selected = ref("")

const MeneSelect = (val: any) => {
  setting_selected.value = val
}

</script>

<template>
  <div class="common-layout" style="height: 100vh;width: 100%;background-color: #F7F7F7;">
    <el-container>
      <el-header style="height: 35px; max-height: 35px; width: 100%;">
        <h2 style="text-align: center">欢迎使用<a
            href="https://github.com/xaoyaoo/PyWxDump.git">PyWxDump</a>聊天记录查看工具!
          <span style="font-size: 14px">(如需提前体验更多功能请开通超级vip)</span>
        </h2>
      </el-header>
      <el-container style="height: calc(100vh - 35px);width: 100%;">

        <el-aside width="200px" style="height: 100%;">
          <el-menu style="height: 100%;background-color: #F7F7F7;color:#262626;"
                   default-active="2"
                   class="el-menu-vertical-demo"
                   @select="MeneSelect"
          >
            <el-menu-item index="-1" disabled>
              <span style="color: #043bea">设置</span>
            </el-menu-item>
            <el-menu-item index="db_init">
              <span>初始化设置</span>
            </el-menu-item>
            <el-menu-item index="3">
              <span></span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main style="height: 100%;max-height: 100%;width: 100%;margin: 0;padding: 0;">
          <db-init-component v-if="setting_selected=='db_init'"></db-init-component>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>

</style>