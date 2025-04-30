<script setup lang="ts">
import {defineProps, ref, onMounted, watch, nextTick, defineExpose} from "vue";
import http from '@/utils/axios.js';
import MessageText from '@/components/chat/message/MessageText.vue';
import MessageImg from '@/components/chat/message/MessageImg.vue';
import MessageVideo from '@/components/chat/message/MessageVideo.vue';
import MessageAudio from '@/components/chat/message/MessageAudio.vue';
import MessageFile from '@/components/chat/message/MessageFile.vue';
import MessageEmoji from '@/components/chat/message/MessageEmoji.vue'
import MessageOther from "@/components/chat/message/MessageOther.vue";
import {apiMsgCountSolo, apiMsgs, apiMyWxid} from "@/api/chat";
import type {msg, User, UserList} from "@/utils/common_utils";
import {api_audio, api_img, api_video} from "@/api/base";
// v3 无限滚动 https://vue3-infinite-loading.netlify.app/api/props.html#distance
import InfiniteLoading from "v3-infinite-loading";
import "v3-infinite-loading/lib/style.css";

// 这里的 props 是从父组件传递过来的
const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});
// 定义变量
const messages = ref<msg[]>([]);
const userlist = ref<UserList>({});
const msg_loading = ref(false);
const my_wxid = ref('');
const start = ref(0);
const limit = ref(100);
const min_id = ref(0);
const max_id = ref(0);
const msg_count = ref(0);

// 这部分为构造消息的发送时间和头像
const _direction = (message: any) => {

  if (message.talker == '我') {
    message.talker = my_wxid.value;
  }
  const sendname = (message: msg) => {
    const user = userlist.value[message.talker];
    return user?.remark || user?.nickname || user?.account || message.talker;
  }
  return `${sendname(message)} [${message.type_name}] ${message.CreateTime}`;
}

const get_head_url = (message: any) => {
  if (message.talker == '我') {
    message.talker = my_wxid.value;
  }
  if (!userlist.value.hasOwnProperty(message.talker)) {
    return '';
  }
  return api_img(userlist.value[message.talker].headImgUrl);
}
// END 这部分为构造消息的发送时间和头像

// 获取聊天记录
const fetchData = async (scroll: String = '') => {
  if (msg_loading.value) {
    console.log("正在获取消息，请稍后再试!")
    return;
  }
  if (props.wxid == '') {
    console.log("wxid 为空, 请检查!")
    return;
  }
  try {
    msg_loading.value = true;
    if (start.value < 0) {
      start.value = 0;
    }
    console.log('fetchData', props.wxid, start.value, limit.value)
    const body_data = await apiMsgs(props.wxid, start.value, limit.value);

    // messages.value = [];
    // messages.value = body_data.msg_list.concat(messages.value);
    messages.value = body_data.msg_list
    if (messages.value.length == 0) {
      msg_loading.value = false;
      return body_data;
    }
    userlist.value = Object.assign(userlist.value, body_data.user_list);
    // 去重
    messages.value = messages.value.filter((item, index, array) => {
      return index === 0 || item.id !== array[index - 1].id;
    });
    // 排序
    messages.value.sort((a, b) => {
      return a.id - b.id
    });

    min_id.value = messages.value[0].id;
    max_id.value = messages.value[messages.value.length - 1].id;

    if (scroll == "top") {
      scrollToId(messages.value[0].id);
    } else if (scroll == "bottom") {
      scrollToId(messages.value[messages.value.length - 1].id);
    }

    msg_loading.value = false;
    return body_data;
  } catch (error) {
    msg_loading.value = false;
    console.error('Error fetching data:', error);
    return [];
  }
};
// 上述为网络请求部分

// 初始加载数据

// END 获取聊天记录

// 监听 userData 中 username 的变化
const init = async () => {
  try {
    messages.value = [];
    userlist.value = {};
    msg_loading.value = false;
    limit.value = limit.value || 100;
    min_id.value = 0;
    max_id.value = 0;

    my_wxid.value = await apiMyWxid();
    msg_count.value = await apiMsgCountSolo(props.wxid);
    if (msg_count.value <= 0) {
      return;
    }
    // 切换最后一页
    console.log('msg_count.value', msg_count.value, limit.value)
    start.value = Math.floor((msg_count.value - 1) / limit.value) * limit.value || 0
    await fetchData("bottom");
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
};
watch(() => props.wxid, (newUsername, oldUsername) => {
  console.log('username changed： ', oldUsername, newUsername);
  init();
});
watch(() => start.value, (newVal, oldVal) => {
  console.log('msg start changed： ', oldVal, newVal);
  if (newVal > oldVal) {
    // 说明是向后滚动
    fetchData("top");
  } else {
    fetchData("bottom");
  }

});

onMounted(() => {
  init();
});

//  移动到底部请求获取全部数据
const loadMoreTop = async ($state: any) => {
  try {
    if (start.value == 0) {
      $state.complete();
      return;
    }
    start.value = start.value - limit.value;
    if (start.value < 0) {
      start.value = 0;
    }
    // await fetchData("bottom");
    $state.loaded();
  } catch (error) {
    console.log("Error fetching Top data:", error)
    $state.error();
  }
};

const loadMoreBottom = async ($state: any) => {
  try {
    if (start.value + limit.value > msg_count.value) {
      $state.complete();
      return;
    }
    start.value = start.value + limit.value;
    // await fetchData("top");
    $state.loaded();
  } catch (error) {
    console.log("Error fetching data:", error)
    $state.error();
  }
};
// END 循环请求获取全部数据


// 分页管理相关的变量
const handleLimitChange = (val: number) => {
  limit.value = val;
  fetchData();
};

const handleCurrentChange = (val: number) => {
  start.value = (val - 1) * limit.value;
  // fetchData();
};
// END 分页管理相关的变量

// 滚动到指定位置 id
const scrollToId = (id: number) => {
  nextTick(() => {
    const element = document.getElementById(`message-${id}`);
    console.log(`scrollToId： message-${id}`)
    if (element) {
      element.scrollIntoView({
        behavior: 'instant',
        block: 'center'
      });
    }
  })
}
// END 滚动到指定位置 id

</script>

<template>
  <div id="chat" v-if="messages.length>0 && msg_count>0">
    <el-container class="chat-records-main-container">
      <el-main class="chat-records-main-main">
        <!--        <div class="infinite-container">-->
        <!--          <InfiniteLoading @infinite="loadMoreTop" :top="true" :firstload="false">-->
        <!--            <template #spinner>-->
        <!--              <span class="spinner-text">加载中...</span>-->
        <!--            </template>-->
        <!--            <template #complete>-->
        <!--              <span class="complete-text">没有更多啦</span>-->
        <!--            </template>-->
        <!--            <template #error="{ retry }">-->
        <!--              <button @click="retry" class="retry-button">错误</button>-->
        <!--            </template>-->
        <!--          </InfiniteLoading>-->
        <!--        </div>-->

        <div class="message" v-for="(message,index) in messages" :key="index" :id="`message-${message.id}`">
          <!-- 文字消息 -->
          <MessageText v-if="message.type_name == '文本'" :is_sender="message.is_sender"
                       :direction="_direction(message)" :headUrl="get_head_url(message)"
                       :content="message.msg"></MessageText>
          <!-- 图片消息 -->
          <MessageImg v-else-if="message.type_name == '图片'" :is_sender="message.is_sender"
                      :direction="_direction(message)" :headUrl="get_head_url(message)"
                      :src="api_img(message.src)"></MessageImg>
          <!-- 表情消息 -->
          <MessageEmoji v-else-if="message.type_name == '动画表情'" :is_sender="message.is_sender"
                        :direction="_direction(message)" :headUrl="get_head_url(message)"
                        :src="api_img(message.src)"></MessageEmoji>
          <!-- 视频消息 -->
          <MessageVideo v-else-if="message.type_name == '视频'" :is_sender="message.is_sender"
                        :direction="_direction(message)" :headUrl="get_head_url(message)"
                        :src="api_video(message.src)"></MessageVideo>
          <!-- 文件消息 -->
          <MessageFile v-else-if="message.type_name == '文件'" :is_sender="message.is_sender"
                       :direction="_direction(message)" :headUrl="get_head_url(message)"
                       :src="message.src"></MessageFile>
          <!-- 语音消息 -->
          <MessageAudio v-else-if="message.type_name == '语音'" :is_sender="message.is_sender"
                        :direction="_direction(message)" :headUrl="get_head_url(message)"
                        :src="api_audio(message.src)"
                        :msg="message.msg"></MessageAudio>
          <!-- 其他消息 -->
          <MessageOther v-else :is_sender="message.is_sender" :direction="_direction(message)"
                        :headUrl="get_head_url(message)" :content="message.msg"></MessageOther>
        </div>
        <!--                <div class="infinite-container">-->
        <!--                  <InfiniteLoading @infinite="loadMoreBottom" :top="false" :firstload="false">-->
        <!--                    <template #spinner>-->
        <!--                      <span class="spinner-text">加载中...</span>-->
        <!--                    </template>-->
        <!--                    <template #complete>-->
        <!--                      <span class="complete-text">没有更多啦</span>-->
        <!--                    </template>-->
        <!--                    <template #error="{ retry }">-->
        <!--                      <button @click="retry" class="retry-button">错误</button>-->
        <!--                    </template>-->
        <!--                  </InfiniteLoading>-->
        <!--                </div>-->
      </el-main>
      <el-footer height="20px" class="chat-records-main-footer">
        <el-pagination background small layout="sizes, prev, pager, next, jumper" :total="msg_count"
                       :page-size="limit" :page-sizes="[50,100, 200, 300, 500]" @size-change="handleLimitChange"
                       :current-page="Math.floor(start / limit + 1)" @current-change="handleCurrentChange"
        />
      </el-footer>
    </el-container>
  </div>
  <el-skeleton v-else-if="messages.length<=0 && msg_count>0" :rows="30" animated/>
  <el-empty description="无记录" v-else/>
</template>

<style scoped>

#chat {
  position: relative;
  width: 100%;
  height: calc(100% - 15px);
  display: flex;
  flex-direction: column;

  .chat-records-main-container {
    height: calc(100% - 15px);
    width: 100%;
    display: flex;
    flex-direction: column;

    .chat-records-main-main {
      padding: 0;
      margin: 0;

      .message:last-of-type {
        margin-bottom: 0px;
      }
    }

    .chat-records-main-footer {
      display: grid;
      place-items: center; /* 居中对齐 */
      padding: 0;
      margin: 0;
    }
  }
}


.infinite-container {
  display: grid;
  place-items: center; /* 居中对齐 */

  .spinner-text,
  .complete-text,
  .retry-button {
    font-size: 16px;
    color: #9d09f3;
  }
}

</style>
