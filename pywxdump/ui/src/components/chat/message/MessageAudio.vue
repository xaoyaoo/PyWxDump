
<script setup lang="ts">
import {defineProps, onMounted, ref} from "vue";
// import http from '@/router/axios.js';
import ElTextarea from 'element-plus';

const props = defineProps({
  is_sender: {
    type: Number,
    default: 0
  },
  headUrl: {
    type: String,
    default: ''
  },
  direction: {
    type: String,
    default: ''
  },
  src: {
    type: String,
    default: ''
  },
  msg: {
    type: String,
    default: ''
  },
})
// const audioSrc = ref("");

// onMounted(async () => {
//   // audioSrc.value = await read_audio_base64(props.src);
// });
//
// const read_audio_base64 = async (src: string) => {
//
//   // try {
//   //   const body_data = await http.post('/rs_api/audio', {
//   //     'savePath': src,
//   //   });
//   //   return body_data;
//   // } catch (error) {
//   //   console.error('Error fetching data:', error);
//   //   return "";
//   // }
//   return src;
// }
</script>

<template>
  <div class="chat-content">
    <!-- recordContent 聊天记录数组-->
    <!-- 对方 -->
    <div class="word" v-if="!is_sender">
      <img :src="headUrl">
      <div class="info">
        <p class="time">{{ direction }}</p>

        <audio controls style="background-color:#fff ">
          <source :src="src" type="audio/wav">
        </audio>
        <el-textarea
            :rows="1"
            :readonly="true"
            :value="msg"
            style="width: 100%;"/>

      </div>
    </div>
    <!-- 我的 -->
    <div class="word-my" v-else>
      <div class="info">
        <p class="time">{{ direction }}</p>

        <audio controls style="background-color:#95EC69;">
          <source :src="src" type="audio/wav">
        </audio>
        <el-textarea
            :rows="1"
            :readonly="true"
            :value="msg"
            style="width: 100%;"/>
      </div>
      <img :src="headUrl">
    </div>
  </div>
</template>

<style scoped lang="scss">

.chat-content {
  width: 100%;
  padding: 20px;

  .word {
    display: flex;
    margin-bottom: 20px;

    img {
      width: 40px;
      height: 40px;
      border-radius: 50%;
    }

    .info {
      margin-left: 10px;

      .time {
        font-size: 12px;
        color: rgba(51, 51, 51, 0.8);
        margin: 0;
        height: 20px;
        line-height: 20px;
        margin-top: -5px;
      }

      .info-content {
        max-width: 80%;
        padding: 10px;
        font-size: 14px;
        background: #fff;
        position: relative;
        margin-top: 8px;
      }

      .chat_img {
        width: 200px;
        height: 200px;
        border-radius: 5px;
      }

      //小三角形
      .info-content::before {
        position: absolute;
        left: -8px;
        top: 8px;
        content: '';
        border-right: 10px solid #FFF;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
      }
    }
  }

  .word-my {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;

    img {
      width: 40px;
      height: 40px;
      border-radius: 50%;
    }

    .info {
      width: 90%;
      margin-left: 10px;
      text-align: right;

      .time {
        font-size: 12px;
        color: rgba(51, 51, 51, 0.8);
        margin: 0;
        height: 20px;
        line-height: 20px;
        margin-top: -5px;
        margin-right: 10px;
      }

      .info-content {
        max-width: 80%;
        padding: 10px;
        font-size: 14px;
        float: right;
        margin-right: 10px;
        position: relative;
        margin-top: 8px;
        background: #95EC69;
        text-align: left;
        display: inline-block;
      }

      .chat_img {
        width: 200px;
        height: 200px;
        border-radius: 5px;
      }

      //小三角形
      .info-content::after {
        position: absolute;
        right: -8px;
        top: 8px;
        content: '';
        border-left: 10px solid #95EC69;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
      }
    }
  }
}

.demo-image__error .image-slot {
  font-size: 30px;
}

.demo-image__error .image-slot .el-icon {
  font-size: 30px;
}

.demo-image__error .el-image {
  width: 100%;
  height: 200px;
}
</style>
