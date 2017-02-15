HUSTOJ Adapter for SDUSTOJ
==

用于SDUSTOJ的适配器，当暂无其他评测机可用时可用此将HUSTOJ接入SDUSTOJ，作为评测机使用。

## 使用方法

### 依赖的Python包

* psycopg2 (2.6.2)
* PyMySQL (0.7.9)
* redis (2.10.5)
* SQLAlchemy (1.1.5)

建议通过pip安装。

中文Windows系统使用pip安装可能遇到UnicodeDecodeError，可从上至下依次尝试如下方案：

* 在命令行执行```chcp 65001```切换代码页后尝试安装。

* 打开python安装目录，在“lib\site-packages\pip\compat\__init__.py”约75行处，有如下代码：

    ```return s.decode('utf_8')```
    
    修改为：
    
    ```return s.decode('cp936')```
    
   尝试安装。
   
   （来自[我在SegmentFault的提问hongweipeng的回答](https://segmentfault.com/q/1010000008071661/a-1020000008186512)，感谢大神）


### Manager

安装好依赖的包后，随便放到什么地方。按照注释说明修改conf.py，设置好相应参数。

对于Linux平台，执行app.sh。

对于Windows平台，仅建议测试使用，运行app.bat即可。
    
### Client

Client部分需要放在HUSTOJ的评测机上的任意位置。 不同于Manager，Client部分仅需要redis包即可运行。
    
安装好依赖的包后，运行app.py即可。


## 模块组成

### Manager

行使评测机功能的主体，用于接收来自SDUSTOJ消息的接受以及评测状态的回填。

* problem_updater

    接收题目题元更新消息，将SDUSTOJ中的题目按测试数据分拆为一至多个HUSTOJ中的题目写入HUSTOJ的数据库，将测试数据或特殊评测代码发送至Client写入评测机文件系统。
    
    SDUSTOJ中的题目将依照测试数据生成HUSTOJ题目，一组数据一个题目。
    
    接收消息与向Client发送消息均通过Redis的队列实现。

* submission_updater

    订阅SDUSTOJ的提交频道，接收来自SDUSTOJ的提交消息并与SDUSTOJ的其他评测机竞争提交。根据获得的提交ID从SDUSTOJ数据库获得提交，将其转换为一至多个HUSTOJ中的提交，写入HUSTOJ的数据库。并标记当前未完成的提交。
    
    SDUSTOJ的提交消息将根据不同的编程环境（语言）被发送到不同的频道上，例如C语言的提交，其消息将发送到C语言提交对应的频道上，订阅该频道的评测机将收到通知，并通过一个仅含该提交的队列参与该提交的竞争，队列中仅为一个标记，不含提交信息。竞争到的评测机将自行获取提交信息进行评测。
    
    当Manager竞争到提交后，将从SDUSTOJ的数据库中获取提交，并根据提交对应的题目在HUSTOJ数据库中查找对应的题目。如果存在未对应的题目，则将自动同步题目，重新执行查询。在找到对应的一至多个题目后，Manager将为每个HUSTOJ题目生成一个对应提交写入HUSTOJ数据库。生成的提交将自动被HUSTOJ进行评测。
    
    当提交生成完毕后，Manager会将SDUSTOJ提交ID加入未完成提交队列，并通过Redis的哈希记录此提交的测试数据与HUSTOJ提交的映射关系（一组数据一个提交），供submission_reporter追踪。

* submission_reporter

    维护标记提交，根据标记的未完成提交轮询HUSTOJ数据库，将HUSTOJ提交状态转换为SDUSTOJ提交状态回填SDUSTOJ数据库。
    
    Manager将从未完成提交队列中轮流获取提交ID，根据此ID查询到对应的HUSTOJ提交，并根据提交状态生成SDUSTOJ提交的每组测试数据的状态及当前总状态。根据各状态信息决定当前评测是否完成，若未完成，则提交将被重新加入未完成提交队列继续下一轮处理。

### Client

接收来自Manager的消息，写入测试数据文件或写入并编译特殊评测文件。