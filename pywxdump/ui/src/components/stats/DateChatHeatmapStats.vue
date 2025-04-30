<script setup lang="ts">
import * as echarts from "echarts";
import {onMounted, ref, shallowRef} from "vue";
import {apiDateCount, apiTalkerCount} from "@/api/stat";
import {apiUserList} from "@/api/chat";
import {gen_show_name, type User} from "@/utils/common_utils";
import DateTimeSelect from "@/components/utils/DateTimeSelect.vue";
import ColorSelect from "@/components/utils/ColorSelect.vue";
import NumberInput from "@/components/utils/NumberInput.vue";
import ChartInit from "@/components/stats/components/ChartInit.vue";

// https://echarts.apache.org/examples/en/editor.html

interface CountData {
  sender_count: number
  receiver_count: number
  total_count: number
}

interface calendar_face {
  top: number
  left: number
  orient: string
  range: string
  dayLabel: any
  monthLabel: any
  yearLabel: any
}

interface series_face {
  type: string
  coordinateSystem: string
  calendarIndex: number
  data: any[]
}


const datetime = ref([0, 0]);
const word = ref("");
const loading = ref(false);
const user_options = ref<User[]>([]);

const date_count_data = ref<any>({});
const top_user = ref<{ [key: string]: User }>({});
const top_user_count = ref<{ [key: string]: CountData }>({});

const is_update = ref(false);
const chart_option = ref({
  backgroundColor: "#ffffff",
  title: {
    left: 'center',
    text: '聊天记录（不包括群聊）'
  },
  toolbox: {
    feature: {saveAsImage: {}}
  },
  tooltip: {
    position: 'top',
    formatter: function (p: any) {
      return p.data[0] + '<br>聊天数量：' + p.data[1];
    }
  },
  visualMap: {
    min: 0,
    max: 500,
    calculable: true,
    orient: 'vertical',
    right: '0',
    top: 'center'
  },
  calendar: <calendar_face[]>[],
  series: <series_face[]>[],

});


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
  // 渲染图表
  let min_date = Object.keys(date_count_data.value)[0];
  let max_date = Object.keys(date_count_data.value)[Object.keys(date_count_data.value).length - 1];

  let min_year = parseInt(min_date.split("-")[0]);
  let max_year = parseInt(max_date.split("-")[0]);

  chart_option.value.calendar = [];
  chart_option.value.series = [];
  for (let i = min_year; i < max_year + 1; i++) {
    chart_option.value.calendar.push({
      top: 100,
      left: 50 + 200 * (i - min_year),
      orient: 'vertical',
      range: i.toString(),
      dayLabel: {
        margin: 5, firstDay: 1, nameMap: ['日', '一', '二', '三', '四', '五', '六'],
      },
      monthLabel: {
        margin: 5,
        nameMap: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
      },
      yearLabel: {"color": "#000"}
    });
    chart_option.value.series.push({
      type: 'heatmap', coordinateSystem: 'calendar', calendarIndex: i - min_year, data: []
    });
  }

  // refreshData();
  Object.keys(date_count_data.value).map(date => {
    let year = parseInt(date.split("-")[0]);
    let index = year - min_year;
    chart_option.value.series[index].data.push([date, date_count_data.value[date].total_count]);
  });
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

const set_top_user = async (wxid: string) => {
  try {
    word.value = wxid;
    await refreshChart();
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
        <el-button type="primary" @click="refreshChart">查看</el-button>
        &nbsp
        <strong>颜色设置：</strong>
        bg:
        <color-select
            @updateColors="(val:any)=>{val?chart_option.backgroundColor=val:'';refreshChart(false)}"></color-select>
        min:
        <number-input :n="chart_option.visualMap.min" :step="100"
                      @updateNumber="(val:any)=>{val?chart_option.visualMap.min=val:'';refreshChart(false)}"></number-input>
        max:
        <number-input :n="chart_option.visualMap.max" :step="100"
                      @updateNumber="(val:any)=>{val?chart_option.visualMap.max=val:'';refreshChart(false)}"></number-input>
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
        <chart-init :option="chart_option" :update="is_update"/>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>

</style>