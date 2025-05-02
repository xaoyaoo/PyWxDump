<script setup lang="ts">
import chatIcon from "@/assets/icon/ChatIcon.vue";
import StatisticsIcon from "@/assets/icon/StatisticsIcon.vue";
import CleanupIcon from "@/assets/icon/CleanupIcon.vue";
import ToolsIcon from "@/assets/icon/ToolsIcon.vue";
import AboutIcon from "@/assets/icon/AboutIcon.vue";
import HelpIcon from "@/assets/icon/HelpIcon.vue";
import SettingIcon from "@/assets/icon/SettingIcon.vue";
// import CollapseIcon from "@/assets/icon/CollapseIcon.vue";
import HomeIcon from "@/assets/icon/HomeIcon.vue";
import ContactsIcon from "@/assets/icon/ContactsIcon.vue";
import MomentsIcon from "@/assets/icon/MomentsIcon.vue";
import FavoriteIcon from "@/assets/icon/FavoriteIcon.vue";
import CollapseOpenIcon from "@/assets/icon/CollapseOpenIcon.vue";
import CollapseCloseIcon from "@/assets/icon/CollapseCloseIcon.vue";

import {RouterLink, RouterView} from 'vue-router'
import {ref, onMounted, withCtx, watch} from 'vue'
import router from "@/router";
import {is_db_init, is_use_local_data} from "@/utils/common_utils";
import ChatRecordsMain from "@/components/chat/ChatRecordsMain.vue";

const isCollapse = ref(true);

const is_local_data = ref(true);

onMounted(() => {
  // localStorage.setItem('isDbInit', "t");
  is_local_data.value = localStorage.getItem('isUseLocalData') === 't';
  console.log("is_local_data", is_local_data.value);
  if(!is_local_data.value) {
    is_db_init();
  }
})
// watch(isDbInit, (val) => {
//   localStorage.setItem('isDbInit', val);
// })

const handleOpen = (key: string, keyPath: string[]) => {
  // console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  // console.log(key, keyPath)
}
</script>

<template>
  <div class="export-main" v-if="is_local_data">
    <chat-records-main wxid="wxid_test"/>
  </div>
  <div id="appbg" v-else>
    <el-container class="layout-container-demo" style="height: 100%;background:none;">
      <el-aside :width="isCollapse ? '64px' : '160px'">
        <el-container class="sidebar-container">
          <el-menu default-active="1" class="el-menu-vertical-demo" :collapse="isCollapse" :router='true'
                   :collapse-transition="false" :show-timeout="0" :hide-timeout="0">

            <el-radio-group v-model="isCollapse"
                            style="margin-bottom: 20px;margin-top: 10px;margin-left: 10px;max-height: 30px">
              <el-radio-button :label="false" v-if="isCollapse">
                <collapse-open-icon></collapse-open-icon>
              </el-radio-button>
              <el-radio-button :label="true" v-else>
                <collapse-close-icon></collapse-close-icon>
              </el-radio-button>
            </el-radio-group>

            <el-menu-item index='/home'>
              <home-icon></home-icon>
              <template #title>首页</template>
            </el-menu-item>
            <el-menu-item index='/chat'>
              <chat-icon></chat-icon>
              <template #title>聊天查看</template>
            </el-menu-item>

            <!--            <el-menu-item index='/contacts'>-->
            <!--              <contacts-icon></contacts-icon>-->
            <!--              <template #title>好友管理</template>-->
            <!--            </el-menu-item>-->
            <!--            <el-menu-item index='/moments'>-->
            <!--              <moments-icon></moments-icon>-->
            <!--              <template #title>朋友圈</template>-->
            <!--            </el-menu-item>-->
            <!--            <el-menu-item index='/favorite'>-->
            <!--              <favorite-icon></favorite-icon>-->
            <!--              <template #title>收藏管理</template>-->
            <!--            </el-menu-item>-->

            <el-menu-item index='/statistics'>
              <statistics-icon></statistics-icon>
              <template #title>统计分析</template>
            </el-menu-item>
            <el-menu-item index='/cleanup'>
              <cleanup-icon></cleanup-icon>
              <template #title>文件清理</template>
            </el-menu-item>
            <el-sub-menu index='/tools'>
              <template #title>
                <tools-icon></tools-icon>
                <span>实用工具</span>
              </template>
              <el-menu-item index='/wxinfo'>账号信息</el-menu-item>
              <el-menu-item index='/bias'>基址偏移</el-menu-item>
              <el-menu-item index='/decrypt'>解密数据</el-menu-item>
              <el-menu-item index='/merge'>数据库合并</el-menu-item>
            </el-sub-menu>

            <el-menu-item index='/chat2ui_select'>
              <statistics-icon></statistics-icon>
              <template #title>AI可视化</template>
            </el-menu-item>

          </el-menu>

         
          <el-menu default-active="1" class="el-menu-vertical-demo" :collapse="isCollapse" @open="handleOpen"
                   @close="handleClose" :router='true'>
            <el-menu-item index='/about'>
              <about-icon></about-icon>
              <template #title>关于我们</template>
            </el-menu-item>
            <el-menu-item index='/help'>
              <help-icon></help-icon>
              <template #title>帮助中心</template>
            </el-menu-item>
            <el-menu-item index='/setting'>
              <setting-icon></setting-icon>
              <template #title>更多设置</template>
            </el-menu-item>
          </el-menu>
        </el-container>
      </el-aside>

      <el-main>
        <RouterView/>
      </el-main>

    </el-container>
  </div>
</template>

<style scoped>

.export-main {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

#appbg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 160px;
}

.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  padding: 0;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 0px;
}

.sidebar-container {
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}
</style>
