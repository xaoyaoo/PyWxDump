<script setup lang="ts">
import {defineEmits, defineProps, ref} from 'vue';

// 进度条
const percentage = ref(0);

const timeout = ref(500);
const colors = [
  {color: '#f56c6c', percentage: 20},
  {color: '#e6a23c', percentage: 40},
  {color: '#5cb87a', percentage: 60},
  {color: '#1989fa', percentage: 80},
  {color: '#6f7ad3', percentage: 100},
]
const last_time = ref(new Date().getTime());

// END 进度条
const props = defineProps({
  startORstop: {
    type: Number,
    required: true,
  }
});

const updateProgress = () => {
  if (props.startORstop === 1) {
    percentage.value = 100;
    return;
  }

  last_time.value = new Date().getTime();
  if (percentage.value >= 99) {
    return;
  }
  if (percentage.value >= 60) {
    timeout.value = timeout.value + 50;
  }
  percentage.value = percentage.value + 1;
  // 调用自身并计算下一个延迟时长
  setTimeout(updateProgress, timeout.value);
};

// 监听开始和停止
updateProgress();

</script>

<template>
  <div class="progress-bar">
    <el-progress type="dashboard" :percentage="percentage" :color="colors"/>
  </div>
</template>

<style scoped>

</style>