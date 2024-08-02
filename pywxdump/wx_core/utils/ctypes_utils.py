import ctypes
import ctypes.wintypes
from collections import namedtuple

# 定义必要的常量
TH32CS_SNAPPROCESS = 0x00000002
MAX_PATH = 260
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


# MEMORY_BASIC_INFORMATION 结构体定义
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.wintypes.LPVOID),
        ('AllocationBase', ctypes.wintypes.LPVOID),
        ('AllocationProtect', ctypes.wintypes.DWORD),
        ('RegionSize', ctypes.c_size_t),
        ('State', ctypes.wintypes.DWORD),
        ('Protect', ctypes.wintypes.DWORD),
        ('Type', ctypes.wintypes.DWORD)
    ]


class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),  # remote pointer
        ("SizeOfImage", ctypes.c_ulong),
        ("EntryPoint", ctypes.c_void_p),  # remote pointer
    ]


# 定义PROCESSENTRY32结构
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.wintypes.DWORD),
                ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ProcessID", ctypes.wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.wintypes.ULONG)),
                ("th32ModuleID", ctypes.wintypes.DWORD),
                ("cntThreads", ctypes.wintypes.DWORD),
                ("th32ParentProcessID", ctypes.wintypes.DWORD),
                ("pcPriClassBase", ctypes.wintypes.LONG),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("szExeFile", ctypes.c_char * MAX_PATH)]


class VS_FIXEDFILEINFO(ctypes.Structure):
    _fields_ = [
        ('dwSignature', ctypes.wintypes.DWORD),
        ('dwStrucVersion', ctypes.wintypes.DWORD),
        ('dwFileVersionMS', ctypes.wintypes.DWORD),
        ('dwFileVersionLS', ctypes.wintypes.DWORD),
        ('dwProductVersionMS', ctypes.wintypes.DWORD),
        ('dwProductVersionLS', ctypes.wintypes.DWORD),
        ('dwFileFlagsMask', ctypes.wintypes.DWORD),
        ('dwFileFlags', ctypes.wintypes.DWORD),
        ('dwFileOS', ctypes.wintypes.DWORD),
        ('dwFileType', ctypes.wintypes.DWORD),
        ('dwFileSubtype', ctypes.wintypes.DWORD),
        ('dwFileDateMS', ctypes.wintypes.DWORD),
        ('dwFileDateLS', ctypes.wintypes.DWORD),
    ]


# 加载dll
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)
version = ctypes.WinDLL('version', use_last_error=True)

# 创建进程快照
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
CreateToolhelp32Snapshot.restype = ctypes.wintypes.HANDLE

# 获取第一个进程
Process32First = kernel32.Process32First
Process32First.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
Process32First.restype = ctypes.wintypes.BOOL

# 获取下一个进程
Process32Next = kernel32.Process32Next
Process32Next.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
Process32Next.restype = ctypes.wintypes.BOOL

# 关闭句柄
CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
CloseHandle.restype = ctypes.wintypes.BOOL

# 打开进程
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
OpenProcess.restype = ctypes.wintypes.HANDLE

# 获取模块文件名
GetModuleFileNameEx = psapi.GetModuleFileNameExA
GetModuleFileNameEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.HANDLE, ctypes.c_char_p, ctypes.wintypes.DWORD]
GetModuleFileNameEx.restype = ctypes.wintypes.DWORD

# 获取文件版本信息大小
GetFileVersionInfoSizeW = version.GetFileVersionInfoSizeW
GetFileVersionInfoSizeW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.POINTER(ctypes.wintypes.DWORD)]
GetFileVersionInfoSizeW.restype = ctypes.wintypes.DWORD

# 获取文件版本信息
GetFileVersionInfoW = version.GetFileVersionInfoW
GetFileVersionInfoW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.c_void_p]
GetFileVersionInfoW.restype = ctypes.wintypes.BOOL

# 查询文件版本信息
VerQueryValueW = version.VerQueryValueW
VerQueryValueW.argtypes = [ctypes.c_void_p, ctypes.wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p),
                           ctypes.POINTER(ctypes.wintypes.UINT)]
VerQueryValueW.restype = ctypes.wintypes.BOOL

# 获取模块信息
GetModuleInformation = psapi.GetModuleInformation
GetModuleInformation.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.HMODULE, ctypes.POINTER(MODULEINFO),
                                 ctypes.wintypes.DWORD]
GetModuleInformation.restype = ctypes.c_bool

# 读取进程内存
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory

# 定义VirtualQueryEx函数
VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.LPCVOID, ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                           ctypes.c_size_t]
VirtualQueryEx.restype = ctypes.c_size_t

# 获取映射文件名
GetMappedFileName = psapi.GetMappedFileNameA
GetMappedFileName.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.LPVOID, ctypes.c_char_p, ctypes.wintypes.DWORD]
GetMappedFileName.restype = ctypes.wintypes.DWORD

GetMappedFileNameW = psapi.GetMappedFileNameW
GetMappedFileNameW.restype = ctypes.wintypes.DWORD
GetMappedFileNameW.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD]


def get_memory_maps(pid):
    # 打开进程
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
    hProcess = OpenProcess(access, False, pid)
    if not hProcess:
        return []

    memory_maps = []
    base_address = 0
    mbi = MEMORY_BASIC_INFORMATION()
    max_address = 0x7FFFFFFFFFFFFFFF  # 64位系统的最大地址

    while base_address < max_address:
        if VirtualQueryEx(hProcess, base_address, ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break

        mapped_file_name = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        if GetMappedFileNameW(hProcess, base_address, mapped_file_name, ctypes.wintypes.MAX_PATH) > 0:
            file_name = mapped_file_name.value
        else:
            file_name = None

        # module_info = MODULEINFO()
        # if GetModuleInformation(hProcess, mbi.BaseAddress, ctypes.byref(module_info), ctypes.sizeof(module_info)):
        #     file_name = get_file_version_info(module_info.lpBaseOfDll)

        memory_maps.append({
            'BaseAddress': mbi.BaseAddress,
            'RegionSize': mbi.RegionSize,
            'State': mbi.State,
            'Protect': mbi.Protect,
            'Type': mbi.Type,
            'FileName': file_name
        })

        base_address += mbi.RegionSize

    CloseHandle(hProcess)
    MemMap = namedtuple('MemMap', ['BaseAddress', 'RegionSize', 'State', 'Protect', 'Type', 'FileName'])
    return [MemMap(**m) for m in memory_maps]


def get_process_exe_path(process_id):
    h_process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id)
    if not h_process:
        return None
    exe_path = ctypes.create_string_buffer(MAX_PATH)
    if GetModuleFileNameEx(h_process, None, exe_path, MAX_PATH) > 0:
        CloseHandle(h_process)
        return exe_path.value.decode('utf-8', errors='ignore')
    else:
        CloseHandle(h_process)
        return None


def get_file_version_info(file_path):
    size = GetFileVersionInfoSizeW(file_path, None)
    if size == 0:
        return None
    res = ctypes.create_string_buffer(size)
    if not GetFileVersionInfoW(file_path, 0, size, res):
        return None

    uLen = ctypes.wintypes.UINT()
    lplpBuffer = ctypes.c_void_p()

    if not VerQueryValueW(res, r'\\', ctypes.byref(lplpBuffer), ctypes.byref(uLen)):
        return None

    ffi = ctypes.cast(lplpBuffer, ctypes.POINTER(VS_FIXEDFILEINFO)).contents

    if ffi.dwSignature != 0xFEEF04BD:
        return None

    version = (
        (ffi.dwFileVersionMS >> 16) & 0xffff,
        ffi.dwFileVersionMS & 0xffff,
        (ffi.dwFileVersionLS >> 16) & 0xffff,
        ffi.dwFileVersionLS & 0xffff,
    )
    # f"{version[0]}.{version[1]}.{version[2]}.{version[3]}"
    return f"{version[0]}.{version[1]}.{version[2]}.{version[3]}"


def get_process_list():
    h_process_snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h_process_snap == ctypes.wintypes.HANDLE(-1).value:
        print("Failed to create snapshot")
        return []

    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    process_list = []

    if not Process32First(h_process_snap, ctypes.byref(pe32)):
        print("Failed to get first process")
        CloseHandle(h_process_snap)
        return []

    while True:
        # process_path = get_process_exe_path(pe32.th32ProcessID)
        process_list.append((pe32.th32ProcessID, pe32.szExeFile.decode('utf-8', errors='ignore')))
        if not Process32Next(h_process_snap, ctypes.byref(pe32)):
            break

    CloseHandle(h_process_snap)
    return process_list


if __name__ == "__main__":
    processes = get_process_list()
    for pid, name in processes:
        if name == "WeChat.exe":
            # print(f"PID: {pid}, Process Name: {name}, Exe Path: {path}")
            # Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
            # wechat_base_address = 0
            memory_maps = get_memory_maps(pid)
            for module in memory_maps:
                if module.FileName and 'WeChatWin.dll' in module.FileName:
                    print(module.BaseAddress)
                    print(module.FileName)
                    break
            # print(wechat_base_address)
            # get_info_with_key(Handle, key_baseaddr, addrLen)
