import http from "@/utils/axios.js";

const is_local_data = localStorage.getItem('isUseLocalData') === 't';
// user list 部分
export const apiDateCount = (wxid: string = '', start_time: number = 0, end_time: number = 0) => {
    return http.post('/api/rs/date_count', {
        'wxid': wxid,
        'start_time': start_time,
        'end_time': end_time,
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}
export const apiTalkerCount = (top: number = 10, start_time: number = 0, end_time: number = 0) => {
    return http.post('/api/rs/top_talker_count', {
        'top': top,
        'start_time': start_time,
        'end_time': end_time,
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

export const apiWordcloud = (target: string = "") => {
    return http.post('/api/rs/wordcloud', {
        target: target,
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

