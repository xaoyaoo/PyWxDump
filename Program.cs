using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

namespace WeChatGetKey
{
	internal class Program
	{
		private static void Main(string[] args)
		{
			try
			{
				Program.ReadTest();
			}
			catch (Exception ex)
			{
				Console.WriteLine("Error：" + ex.Message);
			}
			finally
			{
				//Console.ReadKey();
			}
			Console.WriteLine("[+] Done");
		}
		private static void ReadTest()
		{
			List<int> SupportList = null;
			Process WeChatProcess = null;
			foreach (Process ProcessesName in Process.GetProcessesByName("WeChat"))
			{
				WeChatProcess = ProcessesName;
				Console.WriteLine("[+] WeChatProcessPID: " + WeChatProcess.Id.ToString());
				foreach (object obj in WeChatProcess.Modules)
				{
					ProcessModule processModule = (ProcessModule)obj;
					if (processModule.ModuleName == "WeChatWin.dll")
					{
						Program.WeChatWinBaseAddress = processModule.BaseAddress;
						string FileVersion = processModule.FileVersionInfo.FileVersion;
						Console.WriteLine("[+] WeChatVersion: " + FileVersion);
						if (!Program.VersionList.TryGetValue(FileVersion, out SupportList))
						{
							Console.WriteLine("[-] WeChat Current Version Is: " + FileVersion + " Not Support");
							return;
						}
						break;
					}
				}
				if (SupportList == null)
				{
					Console.WriteLine("[-] WeChat Base Address Get Faild");
				}
				else
				{
					int WeChatKey = (int)Program.WeChatWinBaseAddress + SupportList[4];
					string HexKey = Program.GetHex(WeChatProcess.Handle, (IntPtr)WeChatKey);
					if (string.IsNullOrWhiteSpace(HexKey))
					{
						Console.WriteLine("[-] WeChat Is Run, But Maybe No Login");
						return;
					}
					else
					{
						int WeChatName = (int)Program.WeChatWinBaseAddress + SupportList[0];
						Console.WriteLine("[+] WeChatName: " + Program.GetName(WeChatProcess.Handle, (IntPtr)WeChatName, 100));
						int WeChatAccount = (int)Program.WeChatWinBaseAddress + SupportList[1];
						string Account = Program.GetMobile(WeChatProcess.Handle, (IntPtr)WeChatAccount);
						if (string.IsNullOrWhiteSpace(Account))
						{
							Console.WriteLine("[-] WeChatAccount: Maybe User Is No Set Account");
						}
						else
						{
							Console.WriteLine("[+] WeChatAccount: " + Program.GetAccount(WeChatProcess.Handle, (IntPtr)WeChatAccount, 100));
						}
						int WeChatMobile = (int)Program.WeChatWinBaseAddress + SupportList[2];
						string Mobile = Program.GetMobile(WeChatProcess.Handle, (IntPtr)WeChatMobile);
						if (string.IsNullOrWhiteSpace(Mobile))
						{
							Console.WriteLine("[-] WeChatMobile: Maybe User Is No Binding Mobile");
						}
						else
						{
							Console.WriteLine("[+] WeChatMobile: " + Program.GetMobile(WeChatProcess.Handle, (IntPtr)WeChatMobile, 100));
						}
						int WeChatMail = (int)Program.WeChatWinBaseAddress + SupportList[3];
						string Mail = Program.GetMail(WeChatProcess.Handle, (IntPtr)WeChatMail);
						if (string.IsNullOrWhiteSpace(Mail) != false) { }
						else
						{
							Console.WriteLine("[+] WeChatMail: " + Program.GetMail(WeChatProcess.Handle, (IntPtr)WeChatMail, 100));
						}
						Console.WriteLine("[+] WeChatKey: " + HexKey);
					}
				}
			}
			if (WeChatProcess == null)
			{
				Console.WriteLine("[-] WeChat No Run");
				return;
			}
		}
		private static string GetName(IntPtr hProcess, IntPtr lpBaseAddress, int nSize = 100)
		{
			byte[] array = new byte[nSize];
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress, array, nSize, 0) == 0)
			{
				return "";
			}
			string text = "";
			foreach (char c in Encoding.UTF8.GetString(array))
			{
				if (c == '\0')
				{
					break;
				}
				text += c.ToString();
			}
			return text;
		}
		private static string GetAccount(IntPtr hProcess, IntPtr lpBaseAddress, int nSize = 100)
		{
			byte[] array = new byte[nSize];
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress, array, nSize, 0) == 0)
			{
				return "";
			}
			string text = "";
			foreach (char c in Encoding.UTF8.GetString(array))
			{
				if (c == '\0')
				{
					break;
				}
				text += c.ToString();
			}
			return text;
		}
		private static string GetMobile(IntPtr hProcess, IntPtr lpBaseAddress, int nSize = 100)
		{
			byte[] array = new byte[nSize];
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress, array, nSize, 0) == 0)
			{
				return "";
			}
			string text = "";
			foreach (char c in Encoding.UTF8.GetString(array))
			{
				if (c == '\0')
				{
					break;
				}
				text += c.ToString();
			}
			return text;
		}
		private static string GetMail(IntPtr hProcess, IntPtr lpBaseAddress, int nSize = 100)
		{
			byte[] array = new byte[nSize];
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress, array, nSize, 0) == 0)
			{
				return "";
			}
			string text = "";
			foreach (char c in Encoding.UTF8.GetString(array))
			{
				if (c == '\0')
				{
					break;
				}
				text += c.ToString();
			}
			return text;
		}
		private static string GetHex(IntPtr hProcess, IntPtr lpBaseAddress)
		{
			byte[] array = new byte[4];
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress, array, 4, 0) == 0)
			{
				return "";
			}
			int num = 32;
			byte[] array2 = new byte[num];
			IntPtr lpBaseAddress2 = (IntPtr)(((int)array[3] << 24) + ((int)array[2] << 16) + ((int)array[1] << 8) + (int)array[0]);
			if (Program.ReadProcessMemory(hProcess, lpBaseAddress2, array2, num, 0) == 0)
			{
				return "";
			}
			return Program.bytes2hex(array2);
		}
		private static string bytes2hex(byte[] bytes)
		{
			return BitConverter.ToString(bytes, 0).Replace("-", string.Empty).ToLower().ToUpper();
		}
		[DllImport("kernel32.dll")]
		public static extern int OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);
		[DllImport("kernel32.dll")]
		public static extern int GetModuleHandleA(string moduleName);
		[DllImport("kernel32.dll")]
		public static extern int ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int nSize, int lpNumberOfBytesRead);
		public static Dictionary<string, List<int>> VersionList = new Dictionary<string, List<int>>
		{
			{
				"3.2.1.154",
				new List<int>
				{
					328121948,
					328122328,
					328123056,
					328121976,
					328123020
				}
			},
			{
				"3.3.0.115",
				new List<int>
				{
					31323364,
					31323744,
					31324472,
					31323392,
					31324436
				}
			},
			{
				"3.3.0.84",
				new List<int>
				{
					31315212,
					31315592,
					31316320,
					31315240,
					31316284
				}
			},
			{
				"3.3.0.93",
				new List<int>
				{
					31323364,
					31323744,
					31324472,
					31323392,
					31324436
				}
			},
			{
				"3.3.5.34",
				new List<int>
				{
					30603028,
					30603408,
					30604120,
					30603056,
					30604100
				}
			},
			{
				"3.3.5.42",
				new List<int>
				{
					30603012,
					30603392,
					30604120,
					30603040,
					30604084
				}
			},
			{
				"3.3.5.46",
				new List<int>
				{
					30578372,
					30578752,
					30579480,
					30578400,
					30579444
				}
			},
			{
				"3.4.0.37",
				new List<int>
				{
					31608116,
					31608496,
					31609224,
					31608144,
					31609188
				}
			},
			{
				"3.4.0.38",
				new List<int>
				{
					31604044,
					31604424,
					31605152,
					31604072,
					31605116
				}
			},
			{
				"3.4.0.50",
				new List<int>
				{
					31688500,
					31688880,
					31689608,
					31688528,
					31689572
				}
			},
			{
				"3.4.0.54",
				new List<int>
				{
					31700852,
					31701248,
					31700920,
					31700880,
					31701924
				}
			},
			{
				"3.4.5.27",
				new List<int>
				{
					32133788,
					32134168,
					32134896,
					32133816,
					32134860
				}
			},
			{
				"3.4.5.45",
				new List<int>
				{
					32147012,
					32147392,
					32147064,
					32147040,
					32148084
				}
			},
			{
				"3.5.0.20",
				new List<int>
				{
					35494484,
					35494864,
					35494536,
					35494512,
					35495556
				}
			},
			{
				"3.5.0.29",
				new List<int>
				{
					35507980,
					35508360,
					35508032,
					35508008,
					35509052
				}
			},
			{
				"3.5.0.33",
				new List<int>
				{
					35512140,
					35512520,
					35512192,
					35512168,
					35513212
				}
			},
			{
				"3.5.0.39",
				new List<int>
				{
					35516236,
					35516616,
					35516288,
					35516264,
					35517308
				}
			},
			{
				"3.5.0.42",
				new List<int>
				{
					35512140,
					35512520,
					35512192,
					35512168,
					35513212
				}
			},
			{
				"3.5.0.44",
				new List<int>
				{
					35510836,
					35511216,
					35510896,
					35510864,
					35511908
				}
			},
			{
				"3.5.0.46",
				new List<int>
				{
					35506740,
					35507120,
					35506800,
					35506768,
					35507812
				}
			},
			{
				"3.6.0.18",
				new List<int>
				{
					35842996,
					35843376,
					35843048,
					35843024,
					35844068
				}
			},
			{
				"3.6.5.7",
				new List<int>
				{
					35864356,
					35864736,
					35864408,
					35864384,
					35865428
				}
			},
			{
				"3.6.5.16",
				new List<int>
				{
					35909428,
					35909808,
					35909480,
					35909456,
					35910500
				}
			},
			{
				"3.7.0.26",
				new List<int>
				{
					37105908,
					37106288,
					37105960,
					37105936,
					37106980
				}
			},
			{
				"3.7.0.29",
				new List<int>
				{
					37105908,
					37106288,
					37105960,
					37105936,
					37106980
				}
			},
			{
				"3.7.0.30",
				new List<int>
				{
					37118196,
					37118576,
					37118248,
					37118224,
					37119268
				}
			},
			{
				"3.7.5.11",
				new List<int>
				{
					37883280,
					37884088,
					37883136,
					37883008,
					37884052
				}
			},
			{
				"3.7.5.23",
				new List<int>
				{
					37895736,
					37896544,
					37895592,
					37883008,
					37896508
				}
			},
			{
				"3.7.5.27",
				new List<int>
				{
					37895736,
					37896544,
					37895592,
					37895464,
					37896508
				}
			},
			{
				"3.7.5.31",
				new List<int>
				{
					37903928,
					37904736,
					37903784,
					37903656,
					37904700
				}
			},
			{
				"3.7.6.24",
				new List<int>
				{
					38978840,
					38979648,
					38978696,
					38978604,
					38979612
				}
			},
			{
				"3.7.6.29",
				new List<int>
				{
					38986376,
					38987184,
					38986232,
					38986104,
					38987148
				}
			},
			{
				"3.7.6.44",
				new List<int>
				{
					39016520,
					39017328,
					39016376,
					38986104,
					39017292
				}
			},
			{
				"3.8.0.31",
				new List<int>
				{
					46064088,
					46064912,
					46063944,
					38986104,
					46064876
				}
			},
			{
				"3.8.0.33",
				new List<int>
				{
					46059992,
					46060816,
					46059848,
					38986104,
					46060780
				}
			},
			{
				"3.8.0.41",
				new List<int>
				{
					46064024,
					46064848,
					46063880,
					38986104,
					46064812
				}
			},
			{
				"3.8.1.26",
				new List<int>
				{
					46409448,
					46410272,
					46409304,
					38986104,
					46410236
				}
			},
			{
				"3.9.0.28",
				new List<int>
				{
					48418376,
					48419280,
					48418232,
					38986104,
					48419244
				}
			},
			{
				"3.9.2.23",
				new List<int>
				{
					50320784,
					50321712,
					50320640,
					38986104,
					50321676
				}
			},
			{
				"3.9.2.26",
				new List<int>
				{
					50329040,
					50329968,
					50328896,
					38986104,
					50329932
				}
			}
		};
		private static IntPtr WeChatWinBaseAddress = IntPtr.Zero;
	}
}
