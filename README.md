# Movie Robot 产品手册
[Movie Robot WIki](https://yee329.notion.site/Movie-Robot-Wiki-9abef8c648c840fca47a0bf308957f85)
* [使用Movie Robot前检查清单](https://yee329.notion.site/d8479e45ecbd4ed487726f86ddcfc3fd)
* [开发计划](https://yee329.notion.site/7015972108424f14a1f2e15bde5205b4?v=6a041b4a727c48588134db8538e2b164)
* [更新日志](https://www.notion.so/yee329/231dce04132642359e4a979e6b544ffd)
* 更多文档持续更新中......

**欢迎到WIKI中心（正在编写中），查看产品的发展动态。这套WIKI我会慢慢补充内容，后续会包含完整的开发计划、产品介绍、新手指南、进阶玩法、常见问题答疑等几个板块内容，欢迎大家收藏！**

产品大图
<img alt="产品大图" src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/Movie Robot.jpg"/>

定时自动从豆瓣电影的想看、在看、看过中获取影音信息，然后去PT站（支持多家站点）自动检索种子，找到最佳资源后按豆瓣电影分类提交到BT下载工具下载。在下载前，会自动检查你的Emby中是否已经存在。
基于此功能机制，还顺带具备了下列功能：
- 将一部刚上映，或者还没上映的电影加入想看，当PT站更新时会第一时间帮你下好，被Emby扫描到后直接观看。
- 对剧集类型的影视资源，如果你正在看一部没更新完的剧，只要pt站更新，也会帮你对比本地影音库缺少的剧集开始自动下载。
- 支持多PT站汇总搜索打分选种

针对新增下载和存量硬盘的影视库，机器人还可以帮你对乱七八糟下载种子名做标准化整理，整理后会按电影名+年份+tmdbid的方式存储，可以使用硬链接或复制模式的整理方式。

# 使用须知
* 影音是自己的终身需求，我会持续迭代更新。不过我个人认为这个领域的产品，用户越少，意味着越稳定可靠，广为流传的产品，注定因为和依赖站点或其他依赖资源产生利益冲突，影响软件功能，也影响生态平衡。所以选择封闭激活使用制度，控制用户保有量，避免成为大众产品。
* 产品设计上已经尽量将配置复杂度降到最低，但是私有化产品部署运维有一定门槛，需要掌握诸多linux和dokcer知识。但完成初期搭建，将进入养老状态，全家畅享极致观影体验。
* 如果想使用又不想付出学习成本，可以购买激活码后，悬赏红包（建议50-100），联络VIP群内爱好者，远程手把手帮你搞定，这至少占用一个人1-2小时时间，如果遇到疑难问题特殊需求，甚至更长，所以请尊重帮助你的人吧！

激活码获取方式：
* 通过捐助作者，肯定作者的开发付出，可以获得激活码，现在永久买断使用权128元，打赏码在下面，也可以直接访问：[点击查看微信打赏码](https://yee-1254270141.cos.ap-beijing.myqcloud.com/movie_robot/pay.jpg) 打赏后加作者微信 yipengfei329 来获得激活码以及交流群。当然你也可以直接截图打赏记录，发送邮件到：yipengfei329@gmail.com
* 机器人现已开放API系统，如果你可以在此基础上构建其他场景应用，凡被采纳收纳入产品手册，均可获得激活码。
* 前端代码开源，你可以通过持续的项目贡献（bug修复、代码重构、新功能、交互体验优化等有效PR）获得持续的使用时间。
* PT站点核心骨干或运营人员凭身份标识，也可以领取激活码。

发上一枚可以体验到4月30日的激活码，可以随意传播，邀请自己的朋友来玩，430结束，将会调整激活码捐赠规则和价格。
seGRdbqgVolN0JveBe5p58fnXNGcw9TbtyFoWoLKqOtkU8JrCZGaa3Bj8OWhD8AVXaqTYYja4RO6f2o32To4cDJhz7n6JV7PakwONqg5fZfTw3YkDMICj85FncwEUjuH

# Docker官方镜像
https://registry.hub.docker.com/r/yipengfei/movie-robot/

# 前端源代码
https://github.com/pofey/movie-robot-frontend

# 功能预览
## WebUI
### PC端：
<img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/sublist.jpg" width="926" height="551"/>
<img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/download_dashboard.jpg" width="926" height="551"/>
<img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/site_dashboard.jpg" width="926" height="551"/>

### 移动端：
<img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/webui-search.jpg" width="300" height="650"/><img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/webui-downloading-dark.jpg" width="300" height="650"/>
<img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/search-ww.jpg" width="300" height="650"/><img src="https://raw.githubusercontent.com/pofey/movie_robot/main/doc/images/webui-downloading.jpg" width="300" height="650"/>

## 当前支持的站点
几乎所有主流国内PT站点

# 赞赏一下
<img src="https://yee-1254270141.cos.ap-beijing.myqcloud.com/movie_robot/pay.jpg" width="310" height="310" alt="赞赏码" style="float: left;"/>

# 作者微信
微信号：yipengfei329
