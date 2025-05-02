<template>
  <div
    style="
      background-color: #d2d2fa;
      height: 100vh;
      display: grid;
      place-items: center;
    "
  >
    <div
      style="
        background-color: #fff;
        width: 90%;
        height: 80%;
        border-radius: 10px;
        padding: 20px;
        overflow: auto;
      "
    >
      <div
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
        "
      >
        <div style="font-size: 20px; font-weight: bold">微信数据可视化</div>
      </div>
      <div style="margin-top: 20px">
        <el-table
          :data="tableData"
          style="width: 100%"
          :default-sort="{ prop: 'startTime', order: 'descending' }"
        >
          <el-table-column
            prop="wxid"
            label="微信ID"
            sortable
            
            :filter-method="filterWxid"
          ></el-table-column>
          <el-table-column
            prop="start_time"
            label="开始时间"
            sortable
            
            :filter-method="filterStartTime"
          ></el-table-column>
          <el-table-column
            prop="end_time"
            label="结束时间"
            sortable
            :filter-method="filterEndTime"
          ></el-table-column>
          <el-table-column
            prop="flag"
            label="状态"
            :filters="[
              { text: '已生成', value: true },
              { text: '未生成', value: false },
            ]"
            :filter-method="filterFlag"
          >
            <template #default="scope">
              <el-tag :type="scope.row.flag ? 'success' : 'warning'">
                {{ scope.row.flag ? "已生成" : "未生成" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button
                v-if="scope.row.flag"
                type="primary"
                @click="handleJump(scope.row)"
                >跳转</el-button
              >
              <el-button
                v-else
                type="success"
                @click="handleGenerate(scope.row)"
                >生成</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup tang="ts">
import { onMounted, ref } from "vue";
import { apiAiList } from "@/api/chat";
import { useRoute, useRouter } from "vue-router";
import {ElLoading,ElMessage} from "element-plus";
import { apiAiUiCreateJson } from "@/api/chat";
const route = useRoute();
const router = useRouter();

const tableData = ref([

]);

/**
 * 获取数据
 */
const getTableData = async () => {
  try {
    const res = await apiAiList();
    // console.log("数据：" + res.items[0]);
    tableData.value = res.items;
  } catch (error) {
    console.error("获取数据失败:", error);
  }
};

const filterWxid = (value, row) => {
  return row.wxid === value;
};

const filterStartTime = (value, row) => {
  return row.startTime.includes(value);
};

const filterEndTime = (value, row) => {
  return row.endTime.includes(value);
};

const filterFlag = (value, row) => {
  return row.flag === value;
};

const handleJump = (row) => {
  // 跳转逻辑
  /***
   * 构建查询参数
   * 格式：
   */
  console.log("跳转到可视化页面:", row);
  router.push({
    path: "/chat2ui",
    query: {
      wxid: row.wxid,
      start_time: row.start_time,
      end_time: row.end_time,
    },
  });
};

const handleGenerate = async (row) => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在生成可视化数据，可能需要3分钟左右...',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  
  try {
    // 设置3分钟超时
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('请求超时')), 180000)
    );
    
    const response = await Promise.race([
      apiAiUiCreateJson({
        
            wxid: row.wxid,
        start_time: row.start_time,
        end_time: row.end_time
        
        
      }),
      timeoutPromise
    ]);
    
    if (response) {
      ElMessage.success('可视化数据生成成功');
      await getTableData(); // 刷新表格数据
    }
  } catch (error) {
    console.error('生成失败:', error);
    ElMessage.error(error.message || '生成可视化数据失败');
  } finally {
    loading.close();
  }
};

onMounted(async () => {
  console.log("页面加载完成");
  await getTableData();
});
</script>

<style scoped></style>
