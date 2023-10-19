# CheckBiliRelation
B站回复互相关注和取关那些非互粉的用户

基于bilibili-API-collect 项目整理的API开发
https://github.com/Vita-314/bilibili-API-collect


Config配置：

Headers : 浏览器头

Cookies： 登录后缓存cookie

tag_name：互粉用户的分组名，需提前手动创建，或者已创建的分组

is_check: 为true则检查取关的粉丝，取消关注那些不互粉的

is_log：为true则生成一个log.txt日志文件
