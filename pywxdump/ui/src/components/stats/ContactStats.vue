<script setup lang="ts">
import * as echarts from "echarts";
import {onMounted, ref, shallowRef} from "vue";
import {apiDateCount, apiTalkerCount, apiWordcloud} from "@/api/stat";
import {apiUserList} from "@/api/chat";
import {gen_show_name, type User} from "@/utils/common_utils";
import DateTimeSelect from "@/components/utils/DateTimeSelect.vue";
import ColorSelect from "@/components/utils/ColorSelect.vue";
import ChartInit from "@/components/stats/components/ChartInit.vue";


// https://echarts.apache.org/examples/en/editor.html

interface gender_face {
  男: number
  女: number
  未知: number
}

const user = ref<{ [key: string]: User }>({});
const gender_data = ref<gender_face>({});
const signature_count_dict = ref<{ [key: string]: number }>({});

const is_update = ref(false);
const chart_option = ref({
  backgroundColor: "",
  tooltip: {
    trigger: 'item'
  },
  title: {
    left: 'center',
    text: '联系人画像'
  },
  toolbox: {
    feature: {
      saveAsImage: {}
    }
  },
  series: [
    {
      name: '性别',
      type: 'pie',
      radius: ["10%", "20%"],
      center: ['50%', '200px'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 40,
          fontWeight: 'bold'
        }
      },
      data: <any>[]
    }, {
      name: '个性签名词云',
      type: 'wordCloud',
      sizeRange: [15, 80],
      rotationRange: [0, 0],
      rotationStep: 45,
      gridSize: 8,
      shape: 'cardioid',
      keepAspect: false,
      width: '100%',
      height: '100%',
      drawOutOfBound: false,
      textStyle: {
        normal: {
          color: function () {
            return 'rgb(' + [
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160)
            ].join(',') + ')';
          },
          fontFamily: 'sans-serif',
          fontWeight: 'normal'
        },
        emphasis: {
          shadowBlur: 10,
          shadowColor: '#333'
        }
      },
      data: <any>[]
    }
  ]
});


const get_data = async () => {
  user.value = await apiUserList();
  signature_count_dict.value = await apiWordcloud("signature");

  let gender_data1 = {'男': 0, '女': 0, '未知': 0};
  let province_data: { [key: string]: number } = {};
  let city_data: { [key: string]: number } = {};
  let signature_data: { [key: string]: number } = {};
  for (let key in user.value) {
    let u = user.value[key];
    let ExtraBuf = u.ExtraBuf;
    if (ExtraBuf) {
      if (ExtraBuf["性别[1男2女]"] == 1) {
        gender_data1['男'] += 1;
      } else if (ExtraBuf["性别[1男2女]"] == 2) {
        gender_data1['女'] += 1
      } else {
        gender_data1['未知'] += 1
      }
    } else {
      gender_data1['未知'] += 1
    }
  }
  gender_data.value = gender_data1;
}

// 刷新图表 START
const refreshChart = async (is_get_data: boolean = true) => {
  if (is_get_data) {
    await get_data();
  }
  // 渲染图表
  chart_option.value.series[0].data = [
    {'value': gender_data.value["男"], 'name': '男', itemStyle: {color: '#4F6FE8'}},
    {'value': gender_data.value["女"], 'name': '女', itemStyle: {color: '#FF6347'}}
  ]

  chart_option.value.series[1].data = Object.keys(signature_count_dict.value).map((key) => {
    return {name: key, value: signature_count_dict.value[key]}
  });
  is_update.value = !is_update.value;
}
// 刷新图表 END

onMounted(() => {
  refreshChart();
});


// 搜索联系人相关 END

</script>

<template>
  <div class="common-layout" style="background-color: #d2d2fa;height: 100%;width: 100%;">
    <el-container style="height: 100%;width: 100%;">
      <el-header :height="'80px'" style="width: 100%;">
        <strong>颜色设置：</strong>
        bg:
        <color-select
            @updateColors="(val:any)=>{val?chart_option.backgroundColor=val:'';refreshChart(false)}"></color-select>
      </el-header>

      <el-main style="height: calc(100% - 100px);width: 100%;">
        <chart-init :option="chart_option" :update="is_update" class="charts_main"/>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.charts_main {
  width: 100%;
  height: 100%;
}
</style>