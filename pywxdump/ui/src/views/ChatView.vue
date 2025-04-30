<script setup lang="ts">
import ContactsList from '@/components/chat/ContactsList.vue';
import ChatRecords from '@/components/chat/ChatRecords.vue';
import {onMounted, ref} from "vue";
import IndexView from "@/views/IndexView.vue";
import {apiVersion} from "@/api/base";
import {is_db_init} from "@/utils/common_utils";

const wxid = ref('');

onMounted(() => {
  apiVersion().then((data: string) => {
    console.log("API version: " + data);
  }).catch((error: string) => {
    console.error('Error fetching API version:', error);
  });
  is_db_init();
})

</script>
<template>
  <div id="chat_view" class="common-layout">
    <div>
      <el-container>
        <!--  这是左边的list    -->
        <el-aside width="auto" style="overflow-y: auto; height: calc(100vh);">
          <ContactsList @wxid="(val: any) => {  wxid = val;}"/>
        </el-aside>
        <!-- END 这是左边的list -->

        <!--这是右边的具体聊天记录-->
        <div v-if="wxid != ''" style="height: calc(100vh);width: 100%;">
          <ChatRecords :wxid="wxid"/>
        </div>

        <div v-else style="width: 100%;height: 100%">
          <IndexView/>
        </div>
        <!-- END 这是右边的具体聊天记录 -->
      </el-container>
    </div>
  </div>
</template>

<style scoped>

</style>