# luckysheet_django
luckysheet + django实现多人在线协同操作excel

[演示地址](http://49.234.35.155:8080/luckysheetindex/) http://49.234.35.155:8080/luckysheetindex/

QQ交流群: 697107880

## 一、安装
### 1. 安装必要依赖
1. 安装python3.7。(版本不可过高，python3.10中会有bug：[AttributeError: module 'collections' has no attribute 'MutableMapping'](https://blog.csdn.net/lishuaigell/article/details/125221750))
2. 安装jdk。建议jdk8，因为我使用的就是该版本,因为当前py3的解压有bug (https://bugs.python.org/issue24301)
3. pip install django==2.2.8 (版本不可过高，django3.0废弃了本项目中使用的dwebsocket。否则会遇到报错:TypeError: WebSocketMiddleware() takes no arguments)
4. pip安装requirements.txt中的包。
5. pip install django_redis
6. 本地安装redis服务器。
7. 先安装node.js，之后进入项目目录安装。
```
    cd luckysheet_django/luckysheet_obj/Luckysheet-master
    npm install
    npm install gulp -g
    //开发
    npm run dev
    //打包
    npm run build
```

### 2. 启动
1. [改IP] 进入到luckysheet_django/luckysheet_obj目录，执行./new.ip [IP]，更改当前ip设置。注意，第一次使用new.ip后，要手动将luckysheet_django/luckysheet_obj/luckysheet_obj/settings.py中的ALLOWED_HOSTS中的第一个逗号删除；之后就不需要了。
```
cd luckysheet_django/luckysheet_obj/
./new.ip xxx.xxx.xxx.xxx
vim ./luckysheet_obj/settings.py #去除ALLOWED_HOSTS中第一个逗号。
```
2. [启动后端]
```
cd luckysheet_django/luckysheet_obj/
python manage.py runserver xxx.xxx.xxx.xxx:8080
```
3. [启动前端] 会在3000端口打开前端服务器。
```
cd luckysheet_django/luckysheet_obj/Luckysheet-master
npm run dev
```
4. [启动Redis] 
```
redis-server [指定config文件位置]
```
5. [启动Redis-cli]：可选，便于查看
```
redis-cli -h 127.0.0.1 -p 6379
```


### 3. 目录介绍
1. luckysheet_django/luckysheet_obj/：django项目位置。
2. luckysheet_django/luckysheet_obj/Luckysheet-master：前端Luckysheet的目录，浏览器读取luckysheet的js等内容位置。
3. luckysheet_django/luckysheet_obj/luckysheet_obj/：该django项目的urls、settings等django相关内容。
4. luckysheet_django/luckysheet_obj/apps/lucky_sheet/：该django项目主app实现，实际后端的内容。
5. luckysheet_django/luckysheet_obj/apps/lucky_sheet/tools/：里面为后端抽象提供redis接口的实现。
6. luckysheet_django/luckysheet_obj/apps/lucky_sheet/templates/：django后端，给前端提供的页面。



## 二、开发细节
### 1. 解决大图片无法通过wss传输的方法：
```
源码 https://github.com/mengshukeji/Luckysheet
解决方案：
        1.首先config里面添加自定义图片的发送配置
        2.把该配置添加到core.js里面
        3.添加一个自定义js文件，把发送图片函数写进去
        4.server.js里面修改原来的wss发送配置
```
详细修改如下：
######1、 config里面添加自定义图片的发送配置, [点击查看config.js](./luckysheet_obj/Luckysheet-master/src/core.js)
```angular2html
bigImageUpdateMethod:{"method":"POST", "url":"http://127.0.0.1:8000/luckysheetupdateurl"},  //自定义前端大图片大发送方式
```
![config配置](./readmeImages/config自定义图片配置.png)
######2、 把该配置添加到core.js里面, [点击查看core.js](./luckysheet_obj/Luckysheet-master/src/core.js)
```angular2html
luckysheetConfigsetting.bigImageSendMethod = extendsetting.bigImageUpdateMethod;
```
![core自定义图片配置](./readmeImages/core自定义图片配置.png)
######3、 src/controllers/里面添加一个自定义js文件，把发送图片函数写进去
代码块较多，详细请查看 [src/controllers/imageUpdateCtrl.js](luckysheet_obj/Luckysheet-master/src/controllers/imageUpdateCtrl.js)

![自定义图片发送方式](./readmeImages/自定义图片发送方式.png)

######4、 src/controllers/server.js  里面修改原来的wss发送配置
4.1 顶部导入所需变量、函数
   ```
   import luckysheetConfigsetting from './luckysheetConfigsetting';
   import {customBigImageUpdate} from './bigImageUpdate'
   ```
4.2 修改wss发送方式，代码较多，详细参考 [src/controllers/server.js](./luckysheet_obj/Luckysheet-master/src/controllers/server.js)

![自定义图片发送方式](./readmeImages/微信截图_20210302010044.png)
![自定义图片发送方式](./readmeImages/微信截图_20210302010418.png)

### 2. 初始化加载excel的效果图加载失败
1、 src\controllers\constant.js 里面将加载图片的路径改为 image://static/css/loading.gif

### 后台数据是如何保存的
```angular2html
1、 通过新页面上传，通过toJson的aip获取到数据，发送给后台，后台一边保存mysql一边放至redis
2、 如果是新进来的excel则全部放到redis里面，如果是已经有的，则更新已有的值
3、 定时从redis里面把每一个excel记录固化到mysql数据库中
4、 重新进入excel编辑的时候，通过gridekey从redis/mysql 获取最新的excel内容
键值更新方法：先获取sheet索引，然后再获取到具体的一个小格子位置，如果有则更新，没有则新增
```

### 3. 当前问题
1、新建一个sheet页的时候，如果别的客户端不点击这个新页面一下电话，那新建一方在新sheet页面的修改就不会被同步到其他客户端。因此别的客户端必须点击
一下新的sheet页，才能把新sheet页的修改同步过来。--2021/02/01

2、筛选功能，当前只能把添加筛选功能同步到其他客户端，无法把去除筛选功能同步到其他客户端。--2021/02/01

3、当前由于py3的gzip的bug冲突，所以暂时解压数据得使用java包了，[gzip的bug](https://bugs.python.org/issue24301) --2021/02/01

### 4. 已解决问题
1、多人协同的时候，无法做到同步，卡在了返回值的这一步，返回格式未能对齐，单双引号导致的  --2021/02/01-问题已解决