pub mod procmem;

use std::{
    fs::{self, File},
    io::Read,
    ops::{Add, Sub},
    path::PathBuf,
};

use rayon::prelude::*;
use aes::cipher::{KeyIvInit, BlockDecryptMut, block_padding::NoPadding};
use anyhow::{Ok, Result};
use hmac::{Hmac, Mac};
use pbkdf2::pbkdf2_hmac_array;
use regex::Regex;
use sha1::Sha1;
use windows::Win32::{
    Foundation::CloseHandle,
    System::{
        Diagnostics::Debug::ReadProcessMemory,
        Memory::{PAGE_EXECUTE_READWRITE, PAGE_EXECUTE_WRITECOPY, PAGE_READWRITE, PAGE_WRITECOPY, MEM_PRIVATE},
        Threading::{OpenProcess, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ},
    },
};
use yara::Compiler;

use crate::procmem::ProcessMemoryInfo;

const RULES: &str = r#"
    rule GetPhoneTypeStringOffset
    {
        strings:
            $a = "iphone\x00" ascii fullword
            $b = "android\x00" ascii fullword

        condition:
            any of them
    }

    rule GetDataDir
    {
        strings:
            $a = /[a-zA-Z]:\\.{0,100}?\\WeChat Files\\[0-9a-zA-Z_-]{6,20}?\\/

        condition:
            $a
    }
"#;

#[derive(Debug, Clone)]
struct WechatInfo {
    pub pid: u32,
    pub version: String,
    pub account_name: String,
    pub phone_type: String,
    pub data_dir: String,
    pub key: String,
}

impl std::fmt::Display for WechatInfo {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            r#"=======================================
ProcessId: {}
WechatVersion: {}
AccountName: {}
PhoneType: {}
DataDir: {}
key: {}
=======================================
"#,
            self.pid,
            self.version,
            self.account_name,
            self.phone_type,
            self.data_dir,
            self.key
        )
    }
}

fn get_pid_by_name(pname: &str) -> Vec<u32> {
    let mut result = vec![];
    unsafe {
        for pp in tasklist::Tasklist::new() {
            if pp.get_pname() == pname {
                result.push(pp.get_pid());
            }
        }
    }

    result
}

fn read_number<T: Sub + Add + Ord + Default>(pid: u32, addr: usize) -> Result<T> {
    unsafe {
        let hprocess = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, false, pid)?;

        let mut result: T = T::default();

        ReadProcessMemory(
            hprocess,
            addr as _,
            std::mem::transmute(&mut result),
            std::mem::size_of::<T>(),
            None,
        )?;

        CloseHandle(hprocess)?;
        Ok(result)
    }
}

fn read_string(pid: u32, addr: usize, size: usize) -> Result<String> {
    unsafe {
        let hprocess = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, false, pid)?;

        let mut buffer = vec![0; size];
        let _ = ReadProcessMemory(hprocess, addr as _, buffer.as_mut_ptr() as _, size, None);

        CloseHandle(hprocess)?;

        match buffer.iter().position(|&x| x == 0) {
            Some(pos) => Ok(String::from_utf8(buffer[..pos].to_vec())?),
            None => Ok(String::from_utf8(buffer)?),
        }
    }
}

fn read_bytes(pid: u32, addr: usize, size: usize) -> Result<Vec<u8>> {
    unsafe {
        let hprocess = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, false, pid)?;

        let mut buffer = vec![0; size];
        let _ = ReadProcessMemory(hprocess, addr as _, buffer.as_mut_ptr() as _, size, None)?;

        CloseHandle(hprocess)?;

        Ok(buffer)
    }
}

fn get_proc_file_version(pid: u32) -> String {
    unsafe {
        tasklist::get_proc_file_info(pid)
            .get("FileVersion")
            .expect("read file version failed")
            .to_string()
    }
}

fn dump_wechat_info(pid: u32, special_data_dir: Option::<&PathBuf>) -> WechatInfo {
    let version = get_proc_file_version(pid);
    println!("[+] wechat version is {}", version);

    let pmis = procmem::get_mem_list(pid);

    let wechatwin_all_mem_infos: Vec<&ProcessMemoryInfo> = pmis
        .iter()
        .filter(|x| x.filename.is_some() && x.filename.clone().unwrap().contains("WeChatWin.dll"))
        .collect();

    let wechatwin_writable_mem_infos: Vec<&ProcessMemoryInfo> = wechatwin_all_mem_infos
        .iter()
        .filter(|x| {
            (x.protect
                & (PAGE_READWRITE
                    | PAGE_WRITECOPY
                    | PAGE_EXECUTE_READWRITE
                    | PAGE_EXECUTE_WRITECOPY))
                .0
                > 0
        })
        .map(|x| *x)
        .collect();

    let wechat_writeable_private_mem_infos: Vec<&ProcessMemoryInfo> = pmis
        .iter()
        .filter(|x| {
            (x.protect & (PAGE_READWRITE | PAGE_WRITECOPY)).0 > 0 && x.mtype == MEM_PRIVATE
        })
        .collect();

    // 使用 yara 匹配到登录设备的地址和数据目录
    let compiler = Compiler::new().unwrap();
    let compiler = compiler
        .add_rules_str(RULES)
        .expect("Should have parsed rule");
    let rules = compiler
        .compile_rules()
        .expect("Should have compiled rules");
    let results = rules
        .scan_process(pid, 0)
        // .scan_file(r"C:\Users\thin0\Desktop\WeChatWin.dll", 0)
        .expect("Should have scanned");

    let phone_type_str_match = results
        .iter()
        .filter(|x| x.identifier == "GetPhoneTypeStringOffset")
        .next()
        .expect("unbale to find phone type string")
        .strings
        .iter()
        .filter(|x| {
            x.matches.iter().any(|y| {
                wechatwin_writable_mem_infos
                    .iter()
                    .any(|z| y.base == z.base)
            })
        })
        .next()
        .expect("unbale to find phone type string")
        .matches
        .iter()
        .filter(|x| {
            wechatwin_writable_mem_infos
                .iter()
                .any(|y| x.base == y.base)
        })
        .next()
        .expect("unable to find phone type string");
    let phone_type_string_addr = phone_type_str_match.base + phone_type_str_match.offset;
    let phone_type_string =
        read_string(pid, phone_type_string_addr, 20).expect("read phone type string failed");
    let data_dir = if special_data_dir.is_some() {
        special_data_dir.unwrap().clone().into_os_string().into_string().unwrap()
    } else {
        let data_dir_match = results
            .iter()
            .filter(|x| x.identifier == "GetDataDir")
            .next()
            .expect("unable to find data dir")
            .strings
            .first()
            .expect("unable to find data dir")
            .matches
            .iter()
            .filter(|x| wechat_writeable_private_mem_infos.iter().any(|pmi| pmi.base == x.base))
            .next()
            .expect("unable to find data dir");
        String::from_utf8(data_dir_match.data.clone()).expect("data dir is invalid string")
    };

    println!("[+] login phone type is {}", phone_type_string);
    println!("[+] wechat data dir is {}", data_dir);

    let align = std::mem::size_of::<usize>();   // x64 -> 16, x86 -> 8

    // account_name 在 phone_type 前面，并且是 16 位补齐的，所以向前找，离得比较近不用找太远的
    let mut start = phone_type_string_addr - align;
    let mut account_name_addr = start;
    let mut account_name: Option<String> = None;
    let mut count = 0;
    while start >= phone_type_string_addr - align * 20 {
        // 名字长度>=16，就会变成指针，不直接存放字符串
        let account_name_point_address = read_number::<usize>(pid, start)
        .expect("read account name point address failed");
        let result = if pmis.iter().any(|x| {
            account_name_point_address >= x.base && account_name_point_address <= x.base + x.region_size
        }) {
            read_string(pid, account_name_point_address, 100)
        } else {
            read_string(pid, start, align)
        };

        if result.is_ok() {
            let ac = result.unwrap();

            // 微信号是字母、数字、下划线组合，6-20位
            let re = Regex::new(r"^[a-zA-Z0-9_]+$").unwrap();
            if re.is_match(&ac) && ac.len() >= 6 && ac.len() <= 20{
                // 首次命中可能是原始的 wxid_，第二次是修改后的微信号，找不到第二次说明注册后没改过微信号
                account_name = Some(ac);
                account_name_addr = start;
                count += 1;
                if count == 2 {
                    break;
                }
            }
        }

        start -= align;
    }

    if account_name.is_none() {
        panic!("not found account name address");
    }
    let account_name = account_name.unwrap();
    println!("[+] account name is {}", account_name);

    // 读取一个文件准备暴力搜索key
    const IV_SIZE: usize = 16;
    const HMAC_SHA1_SIZE: usize = 20;
    const KEY_SIZE: usize = 32;
    const AES_BLOCK_SIZE: usize = 16;
    const SALT_SIZE: usize = 16;
    const PAGE_SIZE: usize = 4096;
    let db_file_path = data_dir.clone() + "Msg\\Misc.db";
    let mut db_file = std::fs::File::open(&db_file_path).expect(format!("{} is not exsit", &db_file_path).as_str());
    let mut buf = [0u8; PAGE_SIZE];
    db_file.read(&mut buf[..]).expect("read Misc.db is failed");

    // key 在微信号前面找
    let mut key: Option<String> = None;
    let mem_base = phone_type_str_match.base;
    let mut key_point_addr = account_name_addr - align;
    while key_point_addr >= mem_base {
        let key_addr = read_number::<usize>(pid, key_point_addr).expect("find key addr failed in memory");

        if wechat_writeable_private_mem_infos.iter().any(|x| key_addr >= x.base && key_addr <= x.base + x.region_size) {
            let key_bytes = read_bytes(pid, key_addr, KEY_SIZE).expect("find key bytes failed in memory");
            if key_bytes.iter().filter(|&&x| x == 0x00).count() < 5 {
                // 验证 key 是否有效
                let start = SALT_SIZE;
                let end = PAGE_SIZE;

                // 获取到文件开头的 salt
                let salt = buf[..SALT_SIZE].to_owned();
                // salt 异或 0x3a 得到 mac_salt， 用于计算HMAC
                let mac_salt: Vec<u8> = salt.to_owned().iter().map(|x| x ^ 0x3a).collect();

                // 通过 key_bytes 和 salt 迭代64000次解出一个新的 key，用于解密
                let new_key = pbkdf2_hmac_array::<Sha1, KEY_SIZE>(&key_bytes, &salt, 64000);

                // 通过 key 和 mac_salt 迭代2次解出 mac_key
                let mac_key = pbkdf2_hmac_array::<Sha1, KEY_SIZE>(&new_key, &mac_salt, 2);

                // hash检验码对齐后长度 48，后面校验哈希用
                let mut reserve = IV_SIZE + HMAC_SHA1_SIZE;
                reserve = if (reserve % AES_BLOCK_SIZE) == 0 {
                    reserve
                } else {
                    ((reserve / AES_BLOCK_SIZE) + 1) * AES_BLOCK_SIZE
                };

                // 校验哈希
                type HamcSha1 = Hmac<Sha1>;

                unsafe {
                    let mut mac = HamcSha1::new_from_slice(&mac_key).expect("hmac_sha1 error, key length is invalid");
                    mac.update(&buf[start..end-reserve+IV_SIZE]);
                    mac.update(std::mem::transmute::<_, &[u8; 4]>(&(1u32)).as_ref());
                    let hash_mac = mac.finalize().into_bytes().to_vec();

                    let hash_mac_start_offset = end - reserve + IV_SIZE;
                    let hash_mac_end_offset = hash_mac_start_offset + hash_mac.len();
                    if hash_mac == &buf[hash_mac_start_offset..hash_mac_end_offset] {
                        key = Some(hex::encode(key_bytes));
                        break;
                    }
                }
            }
        }

        key_point_addr -= align;
    }

    if key.is_none() {
        panic!("not found key");
    }

    WechatInfo {
        pid,
        version,
        account_name,
        phone_type: phone_type_string,
        data_dir,
        key: key.unwrap()
    }
}

fn scan_db_files(dir: String) -> Result<Vec<PathBuf>> {
    let mut result = vec![];

    for entry in fs::read_dir(dir)?.filter_map(Result::ok) {
        let path = entry.path();
        if path.is_dir() {
            result.extend(scan_db_files(path.to_str().unwrap().to_string())?);
        } else if let Some(ext) = path.extension() {
            if ext == "db" {
                result.push(path);
            }
        }
    }

    Ok(result)
}

fn read_file_content(path: &PathBuf) -> Result<Vec<u8>> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

fn decrypt_db_file(path: &PathBuf, pkey: &String) -> Result<Vec<u8>> {
    const IV_SIZE: usize = 16;
    const HMAC_SHA1_SIZE: usize = 20;
    const KEY_SIZE: usize = 32;
    const AES_BLOCK_SIZE: usize = 16;
    const SQLITE_HEADER: &str = "SQLite format 3";

    let mut buf = read_file_content(path)?;

    // 如果开头是 SQLITE_HEADER，说明不需要解密
    if buf.starts_with(SQLITE_HEADER.as_bytes()) {
        return Ok(buf);
    }

    let mut decrypted_buf: Vec<u8> = vec![];

    // 获取到文件开头的 salt，用于解密 key
    let salt = buf[..16].to_owned();
    // salt 异或 0x3a 得到 mac_salt， 用于计算HMAC
    let mac_salt: Vec<u8> = salt.to_owned().iter().map(|x| x ^ 0x3a).collect();

    unsafe {
        // 通过 pkey 和 salt 迭代64000次解出一个新的 key，用于解密
        let pass = hex::decode(pkey)?;
        let key = pbkdf2_hmac_array::<Sha1, KEY_SIZE>(&pass, &salt, 64000);

        // 通过 key 和 mac_salt 迭代2次解出 mac_key
        let mac_key = pbkdf2_hmac_array::<Sha1, KEY_SIZE>(&key, &mac_salt, 2);

        // 开头是 sqlite 头
        decrypted_buf.extend(SQLITE_HEADER.as_bytes());
        decrypted_buf.push(0x00);

        // hash检验码对齐后长度 48，后面校验哈希用
        let mut reserve = IV_SIZE + HMAC_SHA1_SIZE;
        reserve = if (reserve % AES_BLOCK_SIZE) == 0 {
            reserve
        } else {
            ((reserve / AES_BLOCK_SIZE) + 1) * AES_BLOCK_SIZE
        };

        // 每页大小4096，分别解密
        const PAGE_SIZE: usize = 4096;
        let total_page = (buf.len() as f64 / PAGE_SIZE as f64).ceil() as usize;
        for cur_page in 0..total_page {
            let offset = if cur_page == 0 {
                16
            } else {
                0
            };
            let start: usize = cur_page * PAGE_SIZE;
            let end: usize = if (cur_page + 1) == total_page {
                start + buf.len() % PAGE_SIZE
            } else {
                start + PAGE_SIZE
            };

            // 搞不懂，这一堆0是干啥的，文件大小直接翻倍了
            if buf[start..end].iter().all(|&x| x == 0) {
                decrypted_buf.extend(&buf[start..]);
                break;
            }

            // 校验哈希
            type HamcSha1 = Hmac<Sha1>;

            let mut mac = HamcSha1::new_from_slice(&mac_key)?;
            mac.update(&buf[start+offset..end-reserve+IV_SIZE]);
            mac.update(std::mem::transmute::<_, &[u8; 4]>(&(cur_page as u32 + 1)).as_ref());
            let hash_mac = mac.finalize().into_bytes().to_vec();

            let hash_mac_start_offset = end - reserve + IV_SIZE;
            let hash_mac_end_offset = hash_mac_start_offset + hash_mac.len();
            if hash_mac != &buf[hash_mac_start_offset..hash_mac_end_offset] {
                return Err(anyhow::anyhow!("Hash verification failed"));
            }

            // aes-256-cbc 解密内容
            type Aes256CbcDec = cbc::Decryptor<aes::Aes256>;

            let iv = &buf[end-reserve..end-reserve+IV_SIZE];
            decrypted_buf.extend(Aes256CbcDec::new(&key.into(), iv.into())
                .decrypt_padded_mut::<NoPadding>(&mut buf[start+offset..end-reserve])
                .map_err(anyhow::Error::msg)?);
            decrypted_buf.extend(&buf[end-reserve..end]);
        }
    }

    Ok(decrypted_buf)
}

fn dump_all_by_pid(wechat_info: &WechatInfo, output: &PathBuf) {
    let msg_dir = wechat_info.data_dir.clone() + "Msg";
    let dbfiles = scan_db_files(msg_dir.clone()).unwrap();
    println!("scanned {} files in {}", dbfiles.len(), &msg_dir);
    println!("decryption in progress, please wait...");

    // 创建输出目录
    if output.is_file() {
        panic!("the output path must be a directory");
    }
    let output_dir = PathBuf::from(format!("{}\\wechat_{}", output.to_str().unwrap(), wechat_info.pid));
    if !output_dir.exists() {
        std::fs::create_dir_all(&output_dir).unwrap();
    }

    dbfiles.par_iter().for_each(|dbfile| {
        let mut db_file_dir = PathBuf::new();
        let mut dest = PathBuf::new();
        db_file_dir.push(&output_dir);
        db_file_dir.push(dbfile.parent().unwrap().strip_prefix(PathBuf::from(msg_dir.clone())).unwrap());
        dest.push(db_file_dir.clone());
        dest.push(dbfile.file_name().unwrap());

        if !db_file_dir.exists() {
            std::fs::create_dir_all(db_file_dir).unwrap();
        }

        std::fs::write(dest, decrypt_db_file(&dbfile, &wechat_info.key).unwrap()).unwrap();
    });
    println!("decryption complete!!");
    println!("output to {}", output_dir.to_str().unwrap());
    println!();
}

fn cli() -> clap::Command {
    use clap::{arg, value_parser, Command};

    Command::new("wechat-dump-rs")
        .version("1.0.5")
        .about("A wechat db dump tool")
        .author("REinject")
        .help_template("{name} ({version}) - {author}\n{about}\n{all-args}")
        .disable_version_flag(true)
        .arg(arg!(-p --pid <PID> "pid of wechat").value_parser(value_parser!(u32)))
        .arg(
            arg!(-k --key <KEY> "key for offline decryption of db file")
                .value_parser(value_parser!(String)),
        )
        .arg(arg!(-f --file <PATH> "special a db file path").value_parser(value_parser!(PathBuf)))
        .arg(arg!(-d --"data-dir" <PATH> "special wechat data dir path (pid is required)").value_parser(value_parser!(PathBuf)))
        .arg(arg!(-o --output <PATH> "decrypted database output path").value_parser(value_parser!(PathBuf)))
        .arg(arg!(-a --all "dump key and decrypt db files"))
}

fn main() {
    // 解析参数
    let matches = cli().get_matches();

    let all = matches.get_flag("all");
    let output = match matches.get_one::<PathBuf>("output") {
        Some(o) => PathBuf::from(o),
        None => PathBuf::from(format!("{}{}", std::env::temp_dir().to_str().unwrap(), "wechat_dump"))
    };

    let key_option = matches.get_one::<String>("key");
    let file_option = matches.get_one::<PathBuf>("file");
    let data_dir_option = matches.get_one::<PathBuf>("data-dir");
    let pid_option = matches.get_one::<u32>("pid");

    match (pid_option, key_option, file_option) {
        (None, None, None) => {
            for pid in get_pid_by_name("WeChat.exe") {
                let wechat_info = dump_wechat_info(pid, None);
                println!("{}", wechat_info);
                println!();

                // 需要对所有db文件进行解密
                if all {
                    dump_all_by_pid(&wechat_info, &output);
                }
            }
        },
        (Some(&pid), None, None) => {
            let wechat_info = dump_wechat_info(pid, data_dir_option);
            println!("{}", wechat_info);
            println!();

            // 需要对所有db文件进行解密
            if all {
                dump_all_by_pid(&wechat_info, &output);
            }
        },
        (None, Some(key), Some(file)) => {
            if !file.exists() {
                panic!("the target file does not exist");
            }

            match file.is_dir() {
                true => {
                    let dbfiles = scan_db_files(file.to_str().unwrap().to_string()).unwrap();
                    println!("scanned {} files in {}", dbfiles.len(), &file.to_str().unwrap());
                    println!("decryption in progress, please wait...");

                    // 创建输出目录
                    if output.is_file() {
                        panic!("the output path must be a directory");
                    }
                    if !output.exists() {
                        std::fs::create_dir_all(&output).unwrap();
                    }

                    for dbfile in dbfiles {
                        let mut db_file_dir = PathBuf::new();
                        let mut dest = PathBuf::new();
                        db_file_dir.push(&output);
                        db_file_dir.push(dbfile.parent().unwrap().strip_prefix(PathBuf::from(&file)).unwrap());
                        dest.push(db_file_dir.clone());
                        dest.push(dbfile.file_name().unwrap());

                        if !db_file_dir.exists() {
                            std::fs::create_dir_all(db_file_dir).unwrap();
                        }

                        std::fs::write(dest, decrypt_db_file(&dbfile, &key).unwrap()).unwrap();
                    }
                    println!("decryption complete!!");
                    println!("output to {}", output.to_str().unwrap());
                    println!();
                },
                false => {
                    std::fs::write(&output, decrypt_db_file(&file, &key).unwrap()).unwrap();
                    println!("output to {}", output.to_str().unwrap());
                }
            }
        },
        _ => panic!("param error")
    }
}