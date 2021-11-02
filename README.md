# socketio_template

Socket.io Python3.7 template

> note: 
>   本次测试使用 socket.io.js 版本为 4.1.3 



==对接说明==

1. 后端
   1. 首先在`redis`中添加`SIO_UID_ROOM_HASH`的hash，key为唯一的项目ID，value为所使用的`socket.io`的room名称。建议 key 与 value 值相等以避免room名称重复
2. 前端   

   1. 前端连接上`socket.io`的服务端后需要`emit`一条数据到服务端的`login`Event中，以便把当前客户端加到对应的`room`中，之后将接收到持续性的推送
3. redis接收要求
   1. 由于使用`redis`订阅的`psubscribe`方法，可接受来自于特定条件下的多个通道，通道有统一的前缀，通道后缀建议和项目ID相同
   2. 通道中推送的数据必须为一个字典格式的`json`字符串，且必须包含项目ID`uid`和推送数据`data`两个字段