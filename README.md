# CheckBiliRelation
B站回复互相关注和取关那些非互粉的用户

基于bilibili-API-collect 项目整理的API开发
https://github.com/Vita-314/bilibili-API-collect


使用说明：
1. 修改config.json里的配置，主要修改有tag_name 写上你已经创建的互粉分组名，没创建需要手动建一下，会自动把之前互粉的用户添加到分组里的；is_check就是检查那些提前取消互关的人，从关注列表中删除
2. 第一次打开会在运行目录生成一个二维码并用默认的图片程序打开，用哔哩app扫码登录后会自动删除，关闭图片程序即可
3. 可能会看到诸如 操作超时的提示，那代表操作用户太多，隔几秒再运行下程序就行


Config配置说明：

Headers : 浏览器头

Cookies： 登录后缓存cookie

tag_name：互粉用户的分组名，需提前手动创建，或者已创建的分组

is_check: 为true则检查取关的粉丝，取消关注那些不互粉的

is_log：为true则生成一个log.txt日志文件
