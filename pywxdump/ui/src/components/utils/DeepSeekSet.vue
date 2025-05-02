<template>
  <div class="deepseek-set">
    <el-form :model="form" label-width="120px">
      <el-form-item label="DeepSeek API Key">
        <el-input 
          v-model="form.apiKey" 
          placeholder="请输入DeepSeek API Key"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="submitting"
        >
          提交
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiDeepSeekSet, apiDeepSeekGet } from '@/api/base'

const form = ref({
  apiKey: ''
})

const submitting = ref(false)

const fetchSettings = async () => {
  try {
    const res = await apiDeepSeekGet()
    if (res?.API_KEY) {
      form.value.apiKey = res.API_KEY
    }
  } catch (error) {
    ElMessage.error('获取设置失败')
  }
}

onMounted(() => {
  fetchSettings()
})

const handleSubmit = async () => {
  if (!form.value.apiKey) {
    ElMessage.warning('请输入API Key')
    return
  }
  
  submitting.value = true
  try {
    await apiDeepSeekSet(form.value.apiKey)
    ElMessage.success('设置成功')
  } catch (error) {
    ElMessage.error('设置失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.deepseek-set {
  padding: 20px;
}
</style>