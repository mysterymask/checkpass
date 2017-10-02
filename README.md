CHECKPASS
======

一个python脚本，调用了mimikatz获取windows登录用户的明文密码，并分析密码是否符合规范，对不合规的密码提示用户更改密码，并在5分钟后强制重新登录。

* python2.7
* 在winxp、win7 (32与64位）下测试通过

依赖
-------------

* pypiwin32、requests
* mimikatz


使用
-------------

* 推荐使用py2exe或pyinstaller将所有脚本和资源（包括mimikatz）打包为一个独立exe运行，解决客户端windows没有python和依赖包的问题；在实际使用中我是将项目打包为checkpass.exe的。
* 由于mimikatz必须运行在管理员权限下才能获取明文密码，因此使用run.js调用runas以获得UAC授权，windows下直接调用checkpass.exe
* setup.vbs是调用vbs脚本检测用户的操作系统版本（为了兼容winxp)
* setup.py是用于py2exe打包用
* config.ini配置将检测结果上传便于统计分析
* run.js与setup.vbs的脚本参考了网上大牛的方法

```bash
	├── README.md
	├── checkpass.py
	├── config.ini
	├── install.vbs
	├── run.js
	├── setup.py
	├── Win32
	│   ├── mimidrv.sys
	│   ├── mimikatz.exe
	│   ├── mimilib.dll
	│   └── mimilove.exe
	└── x64
	    ├── mimidrv.sys
	    ├── mimikatz.exe
	    └── mimilib.dll

```	    
	 