# 整理记录

## 2026 年 10 月 18 日

| 内容 | 修改 |
| --- | --- |
| 项目名称 | 统一为邻里点评，Maven artifact 为 `neighborhood-review` |
| Java 包名 | 从 `com.hmdp` 调整为 `com.zwh.neighborhood`，同步启动类、扫描配置、XML 与日志配置 |
| 依赖 | 保留实际工程的依赖，包括 MySQL Connector 8.0.30 和 Lombok 1.18.30 |
| 连接配置 | 数据库、Redis、Kafka 地址和密码通过环境变量提供 |
| 文件目录 | 图片目录支持 JVM 参数 `review.image-dir` |
| 数据库脚本 | 只保留 10 张表的结构，去除账号和业务样例记录 |
| 仓库 | 创建新的仓库目录，排除旧 Git 历史、IDE 配置和构建产物 |
| 文档 | 新增运行说明、来源说明及当前实现状态 |

本次整理保持来源工程的缓存、限流、Lua 与 Kafka 业务代码状态；未启用被注释的消费者，也未补写消息补偿或压测成果。

## 验证范围

已使用 JDK 21、Maven 3.9.16 执行 `mvn -B -DskipTests package`，78 个 Java 文件编译并打包通过。没有执行依赖 MySQL、Redis 或 Kafka 的集成测试，尚未验证业务链路和压测结果。
