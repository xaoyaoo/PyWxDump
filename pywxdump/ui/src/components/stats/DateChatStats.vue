<script setup lang="ts">
import * as echarts from "echarts";
import {onMounted, ref, shallowRef} from "vue";
import {apiDateCount, apiTalkerCount} from "@/api/stat";
import {apiUserList} from "@/api/chat";
import {gen_show_name, type User} from "@/utils/common_utils";
import DateTimeSelect from "@/components/utils/DateTimeSelect.vue";
import ColorSelect from "@/components/utils/ColorSelect.vue";
import ChartInit from "@/components/stats/components/ChartInit.vue";

// https://echarts.apache.org/examples/en/editor.html

interface CountData {
  sender_count: number
  receiver_count: number
  total_count: number
}

const date_count_data = ref<{ [key: string]: CountData }>({});

const datetime = ref([0, 0]);
const word = ref("");
const loading = ref(false);
const user_options = ref<User[]>([]);

const top_user = ref<{ [key: string]: User }>({});
const top_user_count = ref<{ [key: string]: CountData }>({});

const is_update = ref(false);

const colors = [
  {
    "color": '#ffeab6',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(255,234,182,0)"},
          {offset: 1, color: "rgba(255,234,182,0)"}])
  }, {
    "color": '#c0ffc2',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(192,255,194,0)"},
          {offset: 1, color: "rgba(192,255,194,0)"}])
  }, {
    "color": '#a1d9ff',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(161,217,255,0)"},
          {offset: 1, color: "rgba(161,217,255,0)"}])
  }, {
    "color": '#D37373',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(192,255,194,0)"},
          {offset: 1, color: "rgba(192,255,194,0)"}])
  }, {
    "color": '#e4ecf6',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(161,217,255,0)"},
          {offset: 1, color: "rgba(161,217,255,0)"}])
  }, {
    "color": 'rgba(185,4,245,0.44)',
    "areaStyle": new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{offset: 0, color: "rgba(161,217,255,0)"},
          {offset: 1, color: "rgba(161,217,255,0)"}])
  }
];
const bg_color = ref("");

const chart_option = ref({
  backgroundColor: bg_color.value,
  tooltip: {
    trigger: 'axis',
    position: function (pt: any) {
      return [pt[0], '90%'];
    },
    formatter: function (params: any) {
      let date = params[0].name;
      // let total_count = params[0].value;
      // let sender_count = params[1].value;
      // let receiver_count = params[2].value;
      let total_count = date_count_data.value[date].total_count;
      let sender_count = date_count_data.value[date].sender_count;
      let receiver_count = date_count_data.value[date].receiver_count;
      return `${date}<br>
          聊天记录数量：${total_count}<br>
          发送数量：${sender_count}(${(sender_count / total_count * 100).toFixed(2)}%)<br>
          接收数量：${receiver_count}(${(receiver_count / total_count * 100).toFixed(2)}%) `
    }
  },
  title: {
    left: 'center',
    text: '日聊天记录（不包括群聊）'
  },
  toolbox: {
    feature: {
      dataZoom: {
        yAxisIndex: 'none'
      },
      saveAsImage: {}
    }
  },
  dataZoom: [
    {type: 'inside', start: 0, end: 100},
    {start: 0, end: 100}
  ],
  legend: {
    right: '1%', // 设置图例位于右侧，距离右边边缘 5%
    top: '5%', // 设置图例位于上方
    orient: 'vertical' // 设置图例为垂直排列
  },
  xAxis: {
    type: 'category', // x 轴类型为分类
    boundaryGap: false, // x 轴两端不留空白间隙
    data: <any>[], // x 轴的数据，这里使用了 TypeScript 的泛型表示尚未填充数据
  },
  yAxis: [
    {type: 'value', boundaryGap: ['100%', '10%'], name: '数量', axisLabel: {formatter: '{value}'}},
    {
      type: 'value', boundaryGap: [0, '100%'], name: '百分比', position: 'right', max: 200,
      axisLabel: {formatter: '{value} %'}
    }
  ],
  series: [
    {
      name: '聊天记录数量',
      type: 'line',
      symbol: 'none',
      sampling: 'lttb',
      yAxisIndex: 0,
      itemStyle: {color: colors[0].color},
      areaStyle: {color: colors[0].areaStyle},
      data: <any>[]
    }, {
      name: '发送数量',
      type: 'line',
      showSymbol: false,
      show: false,
      symbol: 'none',
      sampling: 'lttb',
      yAxisIndex: 0,
      itemStyle: {color: colors[1].color},
      areaStyle: {color: colors[1].areaStyle},
      data: <any>[]
    }, {
      name: '接收数量',
      type: 'line',
      symbol: 'none',
      show: false,
      showSymbol: false,
      sampling: 'lttb',
      yAxisIndex: 0,
      itemStyle: {color: colors[2].color},
      areaStyle: {color: colors[2].areaStyle},
      data: <any>[]
    }, {
      name: '发送数量bar',
      type: 'bar',
      stack: 'total',
      barWidth: '50%',
      yAxisIndex: 1,
      itemStyle: {color: colors[3].color},
      areaStyle: {color: colors[3].areaStyle},
      data: <any>[]
    }, {
      name: '接收数量bar',
      type: 'bar',
      stack: 'total',
      barWidth: '50%',
      yAxisIndex: 1,
      itemStyle: {color: colors[4].color},
      areaStyle: {color: colors[4].areaStyle},
      data: <any>[]
    }, {
      name: '分界线',
      type: 'line',
      symbol: 'none',
      sampling: 'lttb',
      yAxisIndex: 1,
      itemStyle: {color: colors[5].color},
      areaStyle: {color: colors[5].areaStyle},
      data: <any>[]
    }
  ]
});

const update_chart_option = () => {
  for (let i = 0; i < chart_option.value.series.length; i++) {
    chart_option.value.series[i].itemStyle.color = colors[i].color;
    chart_option.value.series[i].areaStyle.color = colors[i].areaStyle;
  }
  chart_option.value.backgroundColor = bg_color.value;
}

const get_date_count_data = async () => {
  // {"2024-12-20":{ "sender_count": sender_count,  "receiver_count": receiver_count, "total_count": total_count  },....}
  date_count_data.value = await apiDateCount(word.value, datetime.value[0] / 1000, datetime.value[1] / 1000);
  // 根据key排序
  date_count_data.value = Object.fromEntries(Object.entries(date_count_data.value).sort());
}

const get_top_user_count = async () => {
  // {"wxid":{ "sender_count": sender_count,  "receiver_count": receiver_count, "total_count": total_count  },....}
  const body_data = await apiTalkerCount();
  top_user.value = await apiUserList("", Object.keys(body_data));
  top_user_count.value = body_data;
  // 根据total_count排序
  top_user_count.value = Object.fromEntries(Object.entries(top_user_count.value).sort((a, b) => b[1].total_count - a[1].total_count));
}

// 刷新图表 START
const refreshChart = async (is_get_data: boolean = true) => {
  if (is_get_data) {
    await get_date_count_data();
  }
  // refreshData();
  chart_option.value.xAxis.data = Object.keys(date_count_data.value);
  chart_option.value.series[0].data = Object.values(date_count_data.value).map((item: any) => item.total_count);
  // chart_option.value.series[1].data = Object.values(date_count_data.value).map((item: any) => item.sender_count);
  // chart_option.value.series[2].data = Object.values(date_count_data.value).map((item: any) => item.receiver_count);
  chart_option.value.series[3].data = Object.values(date_count_data.value).map((item: any) => item.sender_count / item.total_count * 100);
  chart_option.value.series[4].data = Object.values(date_count_data.value).map((item: any) => item.receiver_count / item.total_count * 100);
  chart_option.value.series[5].data = Object.values(date_count_data.value).map((item: any) => 50);
  // 渲染图表
  is_update.value = !is_update.value;
}
// 刷新图表 END

onMounted(() => {
  get_top_user_count();
  refreshChart();
});


// 搜索联系人相关 START
const search_user = async (query: string) => {
  try {
    loading.value = true;
    if (query === '') {
      user_options.value = [];
      return;
    }
    const body_data = await apiUserList(query);
    loading.value = false;
    user_options.value = Object.values(body_data);
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}

const search_change = async () => {
  try {
    console.log('search_change:', word.value);
    // await get_data();
    await refreshChart();
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}

const set_top_user = async (wxid: string) => {
  try {
    word.value = wxid;
    await search_change();
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}
// 搜索联系人相关 END

</script>

<template>
  <div class="common-layout" style="background-color: #d2d2fa;height: 100%;width: 100%;">
    <el-container style="height: 100%;width: 100%;">
      <el-header :height="'80px'" style="width: 100%;">
        <strong>时间(默认全部)：</strong>
        <DateTimeSelect @datetime="(val: any) => {datetime = val;}"/> &nbsp;
        <el-select
            v-model="word"
            filterable
            remote
            reserve-keyword
            placeholder="输入想查看的联系人"
            remote-show-suffix
            clearable
            :remote-method="search_user"
            :loading="loading"
            style="width: 240px"
        >
          <el-option v-for="item in user_options" :key="item.wxid" :label="gen_show_name(item)" :value="item.wxid"/>
        </el-select>&nbsp;
        <el-button type="primary" @click="search_change">查看</el-button>
        &nbsp;
        <strong>颜色设置：</strong>
        bg:
        <color-select
            @updateColors="(val:any)=>{val?chart_option.backgroundColor=val:'';refreshChart(false)}"></color-select>

        <template v-for="(color, index) in chart_option.series" :key="index">
          c{{ index + 1 }}
          <color-select
              @updateColors="(val:any)=>{val?chart_option.series[index].itemStyle.color=val:'';refreshChart(false)}"
          ></color-select>
        </template>
        <el-button @click="update_chart_option();refreshChart(false);" size="small">重置</el-button>
        <br>
        <strong>top10[总:(收/发)]：</strong>
        <template v-for="wxid in Object.keys(top_user_count)" :key="wxid">
          <el-button type="primary" plain @click="set_top_user(wxid)" size="small">
            {{ gen_show_name(top_user[wxid]) }} [{{ top_user_count[wxid]?.total_count }}({{
              top_user_count[wxid]?.receiver_count
            }}/{{ top_user_count[wxid]?.sender_count }})]
          </el-button>
        </template>
      </el-header>

      <el-main style="height: calc(100% - 100px);width: 100%;">
        <chart-init :option="chart_option" :update="is_update" id="charts_main"/>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>

</style>