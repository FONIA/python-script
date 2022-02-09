# -*- coding: utf-8 -*-
import sys,os
import urllib
import requests,re
if sys.version_info[0] == 3: raw_input = input

raw_tip = "==============================================="

def curl_get(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
    except requests.RequestException:
        return None

def color_print(str, type = "success"):
    if type == "warn":
        raw = ["\33[5;31;40m ",str," \33[0m"]
    if type == "success":
        raw = ["\33[1;32;40m ",str," \33[0m"]
    if type == "fail":
        raw = ["\33[1;31;40m ",str," \33[0m"]
    print(''.join(raw))

def git_install():
    chk = os.system("git --version > /dev/null 2>&1")
    if chk:
        os.system("yum install curl-devel expat-devel gettext-devel openssl-devel zlib-devel")
        os.system("yum -y install git-core")
        code = os.system("git --version > /dev/null 2>&1")
        if code:
            color_print("安装失败，手动执行：\nyum install curl-devel expat-devel gettext-devel openssl-devel zlib-devel\nyum -y install git-core", "fail")
        else:
            color_print("已安装git")
    else:
        color_print("已安装git")

def redis_install():
    color_print("安装前请检测以下信息是否存在：redis、redis-cli、redis-server，存在勿安装！", "warn") 
    print(raw_tip)
    os.system("find / -name redis")
    os.system("find / -name redis-cli")
    os.system("find / -name redis-server")
    print(raw_tip)
    ok = raw_input("确认安装? N/Y\n")
    if not ok in ["Y","N","y","n"] or ok in ["N","n"]:
        color_print("已取消")
        os._exit(0)
    chk = os.system("redis-cli -v > /dev/null 2>&1")
    if chk:
        chk2 = os.system("gcc -v > /dev/null 2>&1")
        if chk2:
            os.system("yum install gcc")
        release = raw_input("请输入需要安装的redis版本号(x.x.x)：")
        str = ["http://download.redis.io/releases/","redis-",release,".tar.gz"]
        _, msg = urllib.urlretrieve(''.join(str), "redis.%s.tar.gz" % release)
        ##取content-length，验证下载是否成功
        cnt = 0
        for each in msg.items():
            if each[0] == "content-length":
                cnt = int(each[1])
                break
        ##<100k
        if cnt < 100000 :
            color_print("下载失败：%s" % msg)   
        else:
            os.system("tar -zxvf redis.%s.tar.gz -C /usr/local" % release)
            os.system("rm -rf redis.%s.tar.gz" % release)
            if os.path.exists("/usr/local/redis"): os.system("rm -rf /usr/local/redis")
            os.system("mv /usr/local/redis-%s /usr/local/redis" % release)
            os.system("cd /usr/local/redis && make && make install PREFIX=/usr/local/redis")
            os.system("ln -s /usr/local/redis/bin/redis-cli /usr/bin/redis-cli")
            os.system("mv /usr/local/redis/redis.conf /usr/local/redis/bin/")
            os.system("sed -i 's/daemonize no/daemonize yes/g' /usr/local/redis/bin/redis.conf")
            playload="""
[Unit]
Description=redis-server
After=network.target
[Service]
Type=forking
ExecStart=/usr/local/redis/bin/redis-server /usr/local/redis/bin/redis.conf
PrivateTmp=true
[Install]
WantedBy=multi-user.target
"""
            os.system("cat>/etc/systemd/system/redis.service<<EOF%sEOF" % playload)
            os.system("systemctl daemon-reload")
            os.system("systemctl start redis")
            os.system("systemctl enable redis")
            chk = os.system("redis-cli -v > /dev/null 2>&1")
            if not chk:
                color_print("已安装redis")
            else:
                color_print("安装失败","warn")
    else:
        color_print("已安装redis")

def fun_exec(num):
    nums = [1,2]
    if not num in nums:
        print(raw_tip)
        print("已取消！")
        exit()
    print(raw_tip)
    print("正在执行(%s)..." % num)
    print(raw_tip)

    nums = {
        1 : git_install,
        2 : redis_install
    }
    fun = nums.get(num, None)
    if fun: fun()

def tools_init():
    print("===================FONIA=======================")
    print("(1) 安装git           (2) 安装redis")
    print("(0) 取消")
    print(raw_tip)
    try:
        u_input = input("请输入命令编号：")
        if sys.version_info[0] == 3: u_input = int(u_input)
    except: u_input = 0
    fun_exec(u_input)

if __name__ == "__main__":
    ##python tools.py 1
    tools_init()