<script setup lang="ts">
import {defineEmits, ref, watch} from 'vue';

const defaultTime: [Date, Date] = [
  new Date(2000, 1, 1, 0, 0, 0),
  new Date(2000, 2, 1, 23, 59, 59),
] // '12:00:00', '08:00:00'

const shortcuts = [
  {
    text: '全部',
    value: () => {
      const end = new Date();
      const start = new Date(2010, 0, 1, 0, 0, 0);
      return [start, end]
    },
  },
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
  {
    text: '最近半年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 180)
      return [start, end]
    },
  },
  {
    text: '最近一年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
      return [start, end]
    },
  },
  {
    text: '去年一整年',
    value: () => {
      const start = new Date()
      start.setFullYear(start.getFullYear() - 1)
      start.setMonth(0)
      start.setDate(1)
      start.setHours(0, 0, 0)
      const end = new Date()
      end.setFullYear(end.getFullYear() - 1)
      end.setMonth(11)
      end.setDate(31)
      end.setHours(23, 59, 59)
      return [start, end]
    },
  },
]

const datetime = ref([Date, Date])
const emits = defineEmits(['datetime']);

// 向父组件传递数据
// 检测datetime的变化
watch(() => datetime.value, (newVal: any, oldVal: any) => {
  let start;
  let end;
  if (newVal) {
    start = newVal[0].getTime();
    end = newVal[1].getTime();
  } else {
    start = 0;
    end = 0;
  }
  // 向父组件传递数据
  emits('datetime', [start, end]);
})

</script>

<template>
  <!--  <div class="block">-->
  <el-date-picker
      v-model="datetime"
      type="datetimerange"
      :shortcuts="shortcuts"
      range-separator="至"
      start-placeholder="开始时间"
      end-placeholder="结束时间"
      :default-time="defaultTime"
      format="YYYY-MM-DD HH:mm"
  />
  <!--  </div>-->
</template>

<style scoped>
.block {
  padding: 30px 0;
  text-align: center;
  border-right: solid 1px var(--el-border-color);
  flex: 1;
}

.block:last-child {
  border-right: none;
}

.block .demonstration {
  display: block;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}
</style>