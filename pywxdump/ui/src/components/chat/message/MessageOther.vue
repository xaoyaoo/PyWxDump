<template>
  <div class="chat-content">
    <!-- recordContent 聊天记录数组-->
    <!-- 对方 -->
    <div class="word" v-if="!is_sender">
      <img :src="headUrl">
      <div class="info">
        <p class="time">{{ direction }}</p>
        <div class="info-content" v-html="sanitizeHTML(content)"></div>
      </div>
    </div>
    <!-- 我的 -->
    <div class="word-my" v-else>
      <div class="info">
        <p class="time">{{ direction }}</p>
        <div class="info-content" v-html="sanitizeHTML(content)"></div>
      </div>
      <img :src="headUrl">
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineProps} from "vue";

const props = defineProps({
  is_sender: {
    type: Number,
    default: 0
  },
  content: {
    type: String,
    default: ''
  },
  headUrl: {
    type: String,
    default: ''
  },
  direction: {
    type: String,
    default: ''
  }
})
const sanitizeHTML = (html: any) => {
  // Use DOMParser to parse the HTML and then serialize it to a trusted HTML string
  html = html.replace(/\n/g, '<br>');
  const doc = new DOMParser().parseFromString(html, 'text/html');
  return doc.body.innerHTML;
};
</script>

<style scoped lang="scss">

.chat-content {
  width: 100%;
  max-width: 100%;
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
        display: inline-block;


        word-break: break-word;
        white-space: pre-wrap;
        overflow: hidden;
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


        word-break: break-word;
        white-space: pre-wrap;
        overflow: hidden;
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
</style>
