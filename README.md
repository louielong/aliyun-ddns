# aliyun-ddns

为阿里云注册的域名实现DDNS动态解析功能（类似花生壳），使用Python实现并支持docker。

# 使用

> 方法一 直接运行

在使用之前，请确定你安装了python 2.7版本，以及pip。

1、将项目中，`conf.d` 文件夹下内的配置文件 `config-template.json` 修改为 `config.conf`，并按照说明，完成配置。

2、在项目根目录下，执行：
```shell
pip install requests
python main.py
```

每次执行，均会更新一次配置的域名的IP。

> 方法二 Docker运行

在使用之前，确保安装了docker。

1、将项目中，`conf.d` 文件夹下内的配置文件 `config-template.json` 修改为 `config.conf`，并按照说明，完成配置。

2、在项目根目录下，执行：
```
docker build . -t aliyun-ddns
docker run --restart=always aliyun-ddns

```

容器会每分钟自动查询并更新域名解析。

# 配置文件说明

| Name | Description | example |
| --- | --- | --- |
| Key | 你的阿里云账号的Access Key ID |  |
| Secret | 你的阿里云账号的Access Key Secret |  |
| Domain | 注册的域名，注意不要输入二级域名 | example.com |
| RR | 二级域名前缀 | www（www.example.com,只需要填写www即可） |
| RecordID | 保持原信息即可，用于脚本判断当前DNS信息是否为最新使用 |  |
| Region | 保持不变，阿里云API Endpoint |  |


# Q&A

* 我使用方法一运行脚本，如何让系统定时运行？

如果你用的是linux系统，可以通过cron实现定时任务：
```shell
1 * * * * python /usr/src/app/main.py
```

其中 `/usr/src/app/main.py` 更改为项目文件实际位置，这将会实现每分钟自动更新，具体命令参数含义，请参考cron介绍。

