import ctypes
import ctypes.wintypes as wintypes
import logging
import re
import sys

# 定义常量
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_GUARD = 0x100
PAGE_NOCACHE = 0x200
PAGE_WRITECOMBINE = 0x400

MEM_COMMIT = 0x1000
MEM_FREE = 0x10000
MEM_RESERVE = 0x2000
MEM_DECOMMIT = 0x4000
MEM_RELEASE = 0x8000


# 定义结构体
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


# 加载Windows API函数
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

ReadProcessMemory = kernel32.ReadProcessMemory

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.restype = ctypes.c_size_t
VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [wintypes.HANDLE]


def search_memory(hProcess, pattern=br'\\Msg\\FTSContact', max_num=100,start_address=0x0,end_address=0x7FFFFFFFFFFFFFFF):
    """
    在进程内存中搜索字符串
    :param p: 进程ID或者进程句柄
    :param pattern: 要搜索的字符串
    :param max_num: 最多找到的数量
    """
    result = []
    # 打开进程
    if not hProcess:
        raise ctypes.WinError(ctypes.get_last_error())

    mbi = MEMORY_BASIC_INFORMATION()

    address = start_address
    max_address = end_address if sys.maxsize > 2 ** 32 else 0x7fff0000
    pattern = re.compile(pattern)

    while address < max_address:
        if VirtualQueryEx(hProcess, address, ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        # 读取内存数据
        allowed_protections = [PAGE_EXECUTE, PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE, PAGE_READWRITE, PAGE_READONLY, ]
        if mbi.State != MEM_COMMIT or mbi.Protect not in allowed_protections:
            address += mbi.RegionSize
            continue

        # 使用正确的类型来避免OverflowError
        base_address_c = ctypes.c_ulonglong(mbi.BaseAddress)
        region_size_c = ctypes.c_size_t(mbi.RegionSize)

        page_bytes = ctypes.create_string_buffer(mbi.RegionSize)
        bytes_read = ctypes.c_size_t()

        if ReadProcessMemory(hProcess, base_address_c, page_bytes, region_size_c, ctypes.byref(bytes_read)) == 0:
            address += mbi.RegionSize
            continue
        # 搜索字符串 re  print(page_bytes.raw)
        find = [address + match.start() for match in pattern.finditer(page_bytes, re.DOTALL)]
        if find:
            result.extend(find)
        if len(result) >= max_num:
            break
        address += mbi.RegionSize
    return result


if __name__ == '__main__':
    # 示例用法
    pid = 29320  # 将此替换为你要查询的进程ID
    try:
        maps = search_memory(pid)
        print(len(maps))
        for m in maps:
            print(hex(m))
    except Exception as e:
        logging.error(e, exc_info=True)
