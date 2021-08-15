# GitHub520
<p align="center">
  <img src="https://vip1.loli.net/2020/05/19/fLSBE29NxoFtOcd.gif"/>
  <br><strong><a href="https://github.com/521xueweihan/HelloGitHub" target="_blank">HelloGitHub</a></strong> 分享 GitHub 上有趣、入门级的开源项目。<br>兴趣是最好的老师，这里能够帮你找到编程的兴趣！
</p>

有问题可以来[「HelloGitHub 视频号」](https://static.hellogithub.com/5y/img/v.jpeg)问我，不定期直播。

## 一、介绍
对 GitHub 说"爱"太难了：访问慢、图片加载不出来。

*注：* 本项目还处于测试阶段，仅在本机测试通过，如有问题欢迎提 [issues](https://github.com/521xueweihan/GitHub520/issues/new)

---

本项目无需安装任何程序，通过修改本地 hosts 文件，试图解决：
- GitHub 访问速度慢的问题
- GitHub 项目中的图片显示不出的问题

花 5 分钟时间，让你"爱"上 GitHub。

## 二、使用方法

### 2.1 复制下面的内容
```bash
# GitHub520 Host Start
140.82.113.26                 alive.github.com
140.82.113.26                 live.github.com
185.199.108.154               github.githubassets.com
140.82.113.22                 central.github.com
185.199.108.133               desktop.githubusercontent.com
185.199.108.153               assets-cdn.github.com
185.199.108.133               camo.githubusercontent.com
185.199.108.133               github.map.fastly.net
199.232.5.194                 github.global.ssl.fastly.net
140.82.113.4                  gist.github.com
185.199.108.153               github.io
140.82.113.3                  github.com
192.0.66.2                    github.blog
140.82.112.5                  api.github.com
185.199.108.133               raw.githubusercontent.com
185.199.108.133               user-images.githubusercontent.com
185.199.108.133               favicons.githubusercontent.com
185.199.108.133               avatars5.githubusercontent.com
185.199.108.133               avatars4.githubusercontent.com
185.199.108.133               avatars3.githubusercontent.com
185.199.108.133               avatars2.githubusercontent.com
185.199.108.133               avatars1.githubusercontent.com
185.199.108.133               avatars0.githubusercontent.com
185.199.108.133               avatars.githubusercontent.com
140.82.112.10                 codeload.github.com
52.217.174.1                  github-cloud.s3.amazonaws.com
52.217.107.84                 github-com.s3.amazonaws.com
52.217.104.4                  github-production-release-asset-2e65be.s3.amazonaws.com
52.216.88.43                  github-production-user-asset-6210df.s3.amazonaws.com
52.216.141.188                github-production-repository-file-5c1aeb.s3.amazonaws.com
185.199.108.153               githubstatus.com
64.71.144.202                 github.community
185.199.108.133               media.githubusercontent.com


# Update time: 2021-08-15T08:09:35+08:00
# Update url: https://raw.hellogithub.com/hosts
# Star me: https://github.com/521xueweihan/GitHub520
# GitHub520 Host End

```

上面内容会自动定时更新，保证最新有效。数据更新时间：2021-08-15T08:09:35+08:00（内容无变动不会更新）

- 文件：`https://raw.hellogithub.com/hosts`
- JSON：`https://raw.hellogithub.com/hosts.json`

### 2.1 手动方式

#### 2.1.1 修改 hosts 文件
hosts 文件在每个系统的位置不一，详情如下：
- Windows 系统：`C:\Windows\System32\drivers\etc\hosts`
- Linux 系统：`/etc/hosts`
- Mac（苹果电脑）系统：`/etc/hosts`
- Android（安卓）系统：`/system/etc/hosts`
- iPhone（iOS）系统：`/etc/hosts`

修改方法，把第一步的内容复制到文本末尾：

1. Windows 使用记事本。
2. Linux、Mac 使用 Root 权限：`sudo vi /etc/hosts`。
3. iPhone、iPad 须越狱、Android 必须要 root。

#### 2.1.2 激活生效
大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

1. Windows：在 CMD 窗口输入：`ipconfig /flushdns`

2. Linux 命令：`sudo nscd restart`，如报错则须安装：`sudo apt install nscd`

3. Mac 命令：`sudo killall -HUP mDNSResponder`

**Tips：** 上述方法无效可以尝试重启机器。

### 2.2 自动方式

**Tip**：推荐 [SwitchHosts](https://github.com/oldj/SwitchHosts) 工具管理 hosts

以 SwitchHosts 为例，看一下怎么使用的，配置参考下面：

- Title: 随意

- Type: `Remote`

- URL: `https://raw.hellogithub.com/hosts`

- Auto Refresh: 最好选 `1 hour`

如图：

![](./img/switch-hosts.png)

这样每次 hosts 有更新都能及时进行更新，免去手动更新。

### 2.3 AdGuard Home 用户（自动方式）

在 **过滤器>DNS 封锁清单>添加阻止列表>添加一个自定义列表**，配置如下：

- 名称: 随意

- URL: `https://raw.hellogithub.com/hosts`（和上面 SwitchHosts 使用的一样）

如图：

![](./img/AdGuard-rules.png)

更新间隔在 **设置>常规设置>过滤器更新间隔（设置一小时一次即可）**，记得勾选上 **使用过滤器和 Hosts 文件以拦截指定域名**

![](./img/AdGuard-rules2.png)

**Tip**：不要添加在 **DNS 允许清单** 内，只能添加在 **DNS 封锁清单** 才管用。另外，AdGuard for Mac、AdGuard for Windows、AdGuard for Android、AdGuard for IOS 等等 **AdGuard 家族软件** 添加方法均类似。

### 2.4 Chrome 插件方式

[FasterHosts](https://github.com/gauseen/faster-hosts) 是个 Chrome 插件，主要原理是拦截浏览器的某些请求，将 `domain` 替换成访问速度较快的那个。hosts 资源来自 [GitHub520](https://github.com/521xueweihan/GitHub520)，每 1 小时更新一次。

> 1. 下载 [FasterHosts](https://github.com/gauseen/faster-hosts/archive/master.zip) 然后解压，找到 `extension` 子目录
> 2. 打开 Chrome，输入: `chrome://extensions/`
> 3. 打开「开发者模式」
> 4. 选择「加载已解压的扩展程序」，然后定位到刚才解压的文件夹里面的 `extension` 目录，确定
> 5. 这就安装好了，关闭「开发者模式」

## 三、效果对比
之前的样子：

![](./img/old.png)

修改完 hosts 的样子：

![](./img/new.png)


## TODO
- [x] 定时自动更新 hosts 内容
- [x] hosts 内容无变动不会更新
- [ ] 寻到最优 IP 解析结果


## 声明
<a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh"><img alt="知识共享许可协议" style="border-width: 0" src="https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png"></a><br>本作品采用 <a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh">署名-非商业性使用-禁止演绎 4.0 国际</a> 进行许可。
