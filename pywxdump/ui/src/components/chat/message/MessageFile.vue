<template>
    <div class="chat-content">
        <!-- recordContent 聊天记录数组-->
        <!-- 对方 -->
        <div class="word" v-if="!is_sender">
            <img :src="headUrl">
            <div class="info">
                <p class="time">{{ direction }}</p>
                <div style="float: left">
                    <el-card shadow="hover" style="width:fit-content;">文件 ： <a :href="videoSrc" download>{{
                        file_info.file_name }}</a>
                        <div>
                            文件大小：<span>{{ file_info.file_size }}{{ file_info.file_size_unit }}</span>
                        </div>
                    </el-card>
                </div>
            </div>
        </div>
        <!-- 我的 -->
        <div class="word-my" v-else>
            <div class="info">
                <p class="time">{{ direction }}</p>

                <div style="float: right">
                    <el-card shadow="hover" style="width:fit-content;">文件 ： <a :href="videoSrc" download>{{
                        file_info.file_name }}</a>
                        <div>
                            文件大小：<span>{{ file_info.file_size }}{{ file_info.file_size_unit }}</span>
                        </div>
                    </el-card>
                </div>
            </div>
            <img :src="headUrl">
        </div>
    </div>
</template>
  
<script setup lang="ts">
import { defineProps, onMounted, reactive, ref } from "vue";
import http from '@/utils/axios.js';
import {api_file, api_file_info} from "@/api/base";

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
    },
    src: {
        type: String,
        default: ''
    }
})
const videoSrc = ref("");
const file_info = reactive({
    file_name: String,
    file_size: Number,
    file_size_unit: String,
});
onMounted(async () => {
    console.log('文件加载中')
    const file_info_resp = await api_file_info(props.src);
    // console.log(file_info_resp)
    file_info.file_name = file_info_resp.file_name;
    file_info.file_size = Number(file_info_resp.file_size) / 1024;
    if (file_info.file_size < 1024) {
        file_info.file_size_unit = "kb";
    } else {
        file_info.file_size = file_info.file_size / 1024;
        file_info.file_size_unit = "mb";
    }
    file_info.file_size = Number(file_info_resp.file_size) / 1024;
    // 字符串转float
    // var file_size = file_info_resp.file_size/1024;
    videoSrc.value = api_file(props.src);

});

</script>
  
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

.demo-video__preview {
    padding-left: 5px;
    padding-right: 5px;
}
</style>
  