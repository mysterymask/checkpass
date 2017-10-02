#-*- coding:utf-8 -*-
import win32api
import win32con
import requests
import subprocess
import platform
import time
import re
import os

'''
写自启动项
'''
def add_reg_autorun():
	name = 'checkpass'
	#winxp下，直接启动checkpass.exe，在win7下通过UAC方式，当用户不是administrator，可以弹出UAC窗口授权
	if platform.version()[0] == '5':
		path = r'c:\checkpass\checkpass.exe'
	else:
		path = r'c:\checkpass\run.js'
	KeyName =r'Software\Microsoft\Windows\CurrentVersion\Run'
	try:
		key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE,  KeyName, 0,  win32con.KEY_ALL_ACCESS)
		win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, path)
		win32api.RegCloseKey(key)
		print u'添加自启动项成功'
		return True
	except:
		print u'失败添加自启动'
		return False
'''
判断是否是64位操作系统
'''
def is_64bit_win():
	return 'PROGRAMFILES(X86)' in os.environ
'''
调用mimikatz获取用户登录口令信息
'''
def run_mimikatz():
	if is_64bit_win():
		filepath = r'x64\mimikatz.exe'
	else:
		filepath = r'Win32\mimikatz.exe'
	filepath += ' privilege::debug  sekurlsa::logonpasswords exit '
	p = subprocess.Popen(filepath, stdin=subprocess.PIPE,
						 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
	'''
	p.stdin.write(u'privilege::debug\r\n')
	p.stdin.flush()
	time.sleep(0.3)
	p.stdin.write(u'sekurlsa::logonpasswords\r\n')
	p.stdin.flush()
	time.sleep(0.3)
	p.stdin.write(u'exit\r\n')
	p.stdin.flush()
	'''
	time.sleep(0.3)
	results = []
	while True:
		line = p.stdout.readline()
		if line == '':
			break
		results.append(line)
	#print ''.join(results)
	return results

'''
从mimikatz获取的信息中查找交互式登录的用户明文口令
'''
def search_password(results):
	passwords = []
	for i in range(len(results)):
		line = results[i]
		# 查找第一个交式互用户的会话
		if 'Session' and 'Interactive' in line:
			for j in range(i+1, len(results)):
				line_2 = results[j]
				# 如果找到第二个会话，则结束
				if 'Session' in line_2:
					return passwords
				else:
					# 找到Password：
					if '* Password :' in line_2:
						title, password = line_2.split(':')
						passwords.append(password.strip())
	return passwords

'''
对口令和复杂度进行检查
'''
def check_password(password):
	# 检测长度：
	if len(password) < 8:
		return False,u'口令长度不够！'
	# 检查复杂度：
	pattern = re.compile('[a-zA-Z]+')
	match = pattern.findall(password)
	if not match:
		return False,u'口令必须包含字母！'
	pattern = re.compile('[0-9]+')
	match = pattern.findall(password)
	if not match:
		return False,u'口令必须包数字！'

	return True,u'口令符合复杂度要求！'

'''
口令检查
'''
def check_pass():
	results = run_mimikatz()
	passwords = search_password(results)
	if len(passwords) == 0:
		valid = None
		msg = u'未正确获取到windows的密码，请检查mimikatz运行是否正常！'
		password = ''
	elif len(passwords) >= 1:
		password =  passwords[0]
		if password == u'(null)':
			valid = False
			msg = u'空口令!'
			password = ''
		else:
			print u'口令为：{}'.format(password)
			valid,msg = check_password(password)
	print msg
	return password,valid,msg

'''
等待5分钟后注册，以使mimikatz能获取修改后的登录密码
'''
def wait_for_restart():
	#等待5分钟：
	time_last = time.time()
	while True:
		if time.time() - time_last > 60 * 1:
			break
		time.sleep(5)
	#注销重登录：
	subprocess.Popen('shutdown /l /f')

'''
以HTTP方式返回检查结果到服务器
'''
def http_send_check_result(server,valid,password):
	#stats:1-满足要求的口令，2-弱口令，4-空口令，8-未获取到口令
	if valid is None:
		check_result = 8
	elif valid is True:
		check_result = 1
	else:
		check_result = 4 if len(password)==0 else 2
	length = len(password)
	data = {'check_result':check_result,'length':length}
	try:
		req = requests.get(server,params=data,timeout=5)
		if req.status_code == requests.codes.ok:
			print u'上传检查结果成功！'
		else:
			raise
	except:
		print u'上传检查结果失败！'

'''
从config.ini中读取配置的上传服务地址，比如：http://1.2.3.4/msg_receiver.php
'''
def get_server_from_config(filename):
	try:
		with open(filename) as f:
			return f.readline().strip()
	except:
		return ''

def main():
	add_reg_autorun()
	password,valid,msg = check_pass()
	#向server返回检查结果：
	server = get_server_from_config('config.ini')
	if server != '' :
		http_send_check_result(server,valid,password)
	if valid is not None:
		if not valid:
			#提示信息：
			msg += u'你必须在5分钟内修改口令为包含字母、数字且长度大于8位的强口令，5分钟后将自动注销重新登录！'
			win32api.MessageBox(0, msg, u'请注意',win32con.MB_OK | win32con.MB_ICONWARNING) 
			wait_for_restart()
		else:
			win32api.MessageBox(0, u'用户口令符合复杂度要求', u'口令',win32con.MB_OK) 
			#pass

if __name__ == '__main__':
	main()
