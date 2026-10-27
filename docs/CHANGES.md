# 整理记录

## 2026 年 10 月 27 日

- 展示名调整为 LocalLife Lab，定位为本地生活服务后端与并发优化实践；仓库地址、包名及 artifact 保留。
- 复现来源限流脚本的同毫秒请求记录覆盖问题，改由 Java 生成独立 UUID 作为 ZSet member。
- 增加脚本参数检查，并使用毫秒 TTL；活动窗口保持 `(now-window, now]` 的边界约定。
- 增加真实 Redis 回归脚本和 Java 调用参数测试。7 项 Redis 检查和 1 项 Java 测试通过。
- 保存原脚本、原始结果和实验说明，明确这不是 HTTP 性能压测。
- 新增工程路线与来源介绍口径；消息下单闭环、完整缓存实验及应用级验证仍待后续迭代。

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
