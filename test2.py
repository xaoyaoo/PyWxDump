import os


# s = "48805389894@chatroom_aiyes_2025-04-30_00-00-00_to_2025-05-01_23-59-59.json"
# wxid = s.split('.')[0].split('_')[0] # wxid
# time_start = " ".join(s.split('.')[0].split('_')[2:4]) # time start
# time_end = " ".join(s.split('.')[0].split('_')[5:7]) # time end
# # flag = s.split('.')[0].split('_')[-1] #flag
# print(wxid, time_start, time_end)



def get_file_path(work_path: str, file_name: str) -> str | None:
    """
    获取ai_json文件路径
    """
    path_list = os.listdir(work_path)
    for path in path_list:
        full_path = os.path.join(work_path, path)
        if os.path.isfile(full_path) and path == file_name:
            return full_path
        elif os.path.isdir(full_path):
            result = get_file_path(full_path, file_name)
            if result is not None:
                return result
    return None


if __name__ == '__main__':
    work_path = r'E:\project\wx_db_ui\PyWxDump-master\pywxdump\wxdump_work\export\wxid_7l787uu0sm8e22'
    file_name = 'aa.txt'
    print(get_file_path(work_path, file_name))

