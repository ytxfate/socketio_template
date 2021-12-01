# socketio_template

Socket.io Python3.7 template

> note: 
>   本次测试使用 socket.io.js 版本为 4.1.3 



==对接说明==

1. 后端
   1. 首先在`redis`中添加`PROID_REDCHAN_MAPPING`的hash，key为唯一的项目ID，value为需要订阅的redis的`channel`名称。`socket.io` 的 `room`为 `RN_{项目id}`
2. 前端   

   1. 前端连接上`socket.io`的服务端后需要`emit`一条数据到服务端的`login`Event中，以便把当前客户端加到对应的`room`中，之后将接收到持续性的推送
3. redis接收要求
   1. 由于使用`redis`订阅的`subscribe`方法，可接受来自于特定条件下的一个或多个通道，通道最好有统一的前缀
   2. 通道中推送的数据必须为一个字典格式的`json`字符串，若不为`json`字符串的话需修改`back_task`后台任务格式化`redis channel`数据部分