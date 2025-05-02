import http from "@/utils/axios.js";
import {ElNotification} from "element-plus";

const is_local_data = localStorage.getItem('isUseLocalData') === 't';
// 编辑器禁用检查

const l_msg_count = local_msg_count
const l_user_list = local_user_list
const l_msg_list = local_msg_list
const l_mywxid = local_mywxid

// user list 部分
export const apiUserList = (word: string = '', wxids: string[] = [], labels: string[] = []) => {
    if (is_local_data) {
        return l_user_list;
    }
    return http.post('/api/rs/user_list', {
        'word': word,
        'wxids': wxids,
        'labels': labels
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

export const apiUserSessionList = () => {
    return http.post('/api/rs/user_session_list', {})
        .then((res: any) => {
            return res;
        })
        .catch((err: any) => {
            console.log(err);
            return [];
        })
}
export const apiMyWxid = () => {
    if (is_local_data) {
        return l_mywxid;
    }
    return http.get('/api/rs/mywxid').then((res: any) => {
        return res.my_wxid;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

// 消息部分

export const apiRealTime = () => {
    return http.post('/api/ls/realtimemsg', {}).then((res: any) => {
        console.log(res);
        // 滚动消息提醒
        ElNotification({
            title: 'Success',
            message: '获取实时消息成功!',
            type: 'success',
        })
        return true;
    }).catch((err: any) => {
        console.log(err);
        ElNotification({
            title: 'Error',
            message: '获取实时消息失败!',
            type: 'error',
        })
        return false;
    })
}

export const apiMsgCount = (wxids: string[]) => {
    return http.post('/api/rs/msg_count', {
        "wxids": wxids
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}
export const apiMsgCountSolo = (wxid: string) => {
    if (is_local_data) {
        return l_msg_count;
    }
    return apiMsgCount([wxid]).then((res: any) => {
        return res[wxid] || 0;
    }).catch((err: any) => {
        console.log(err);
        return 0;
    })
}


export const apiMsgs = (wxid: string, start: number, limit: number) => {
    if (is_local_data) {
        return {
            'msg_list': l_msg_list || [],
            'user_list': l_user_list || [],
        }
    }
    return http.post('/api/rs/msg_list', {
        'start': start,
        'limit': limit,
        'wxid': wxid,
    }).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

/**
 * 获取ai可视化文件列表
 */
export const apiAiList = () =>{
    return http.get('/api/rs/ai_ui_json_list' ).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}


/**
 * 获取ai可视化文件内容
 */

export interface AiUiJson {
    
    wxid: string,
    start_time:string,
    end_time:string,
    
}



export const apiAiUiJson = (file_name: AiUiJson) =>{
    return http.post('/api/rs/get_ui_json', {file_name}).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}


export const apiAiUiCreateJson = (file_name: AiUiJson) =>{
    return http.post('/api/rs/db_to_ai_json', {file_name}).then((res: any) => {
        return res;
    }).catch((err: any) => {
        console.log(err);
        return '';
    })
}

