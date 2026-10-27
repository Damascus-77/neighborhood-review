# LocalLife Lab

本地生活服务后端与并发优化实践

以黑马点评课程及其扩展代码为基础的 Java 后端工程实践项目。保留商铺查询、优惠券、用户登录和探店笔记作为业务场景，逐项验证缓存、限流与并发订单处理的设计和边界。

当前仓库从本地使用的工程整理而来，保留课程来源与原作者注释。仓库名称、包名和文档已经统一，数据库和服务连接参数通过环境变量配置。当前验证范围与功能边界见 [项目现状](docs/STATUS.md)，来源见 [NOTICE](NOTICE.md)。

展示名为 **LocalLife Lab**，现有仓库地址、Java 包名和 Maven artifact 保留，方便已有链接和本地启动配置继续使用。

## 实验记录

- [滑动窗口限流的同毫秒计数缺陷](docs/experiments/rate-limiter.md)：使用真实 Redis 复现旧脚本问题，验证请求标识修复、并发计数、窗口边界和过期行为。
- 功能状态与实验结论分别记录；脚本正确性结果不作为整站吞吐量或生产容量指标。

## 技术栈

Java · Spring Boot · MyBatis-Plus · MySQL · Redis · Lua · Redisson · Caffeine · Spring Kafka

## 核心模块

| 模块 | 源码内容 | 阅读入口 |
| --- | --- | --- |
| 登录与会话 | Redis 验证码、登录信息与拦截器续期 | `UserServiceImpl`、`RefreshTokenInterceptor` |
| 商铺缓存 | 缓存空值，互斥重建和逻辑过期的替代实现 | `ShopServiceImpl`、`CacheClient` |
| 优惠券多级缓存 | MySQL、Redis、Caffeine 三种配置模式 | `VoucherListCacheService`、`VoucherCacheProperties` |
| 滑动窗口限流 | 自定义注解、AOP 切面与 Redis ZSet Lua 脚本 | `RateLimiter`、`RateLimiterAspect`、`limiter.lua` |
| 秒杀资格校验 | Lua 检查库存与重复请求，并预扣 Redis 库存 | `VoucherOrderServiceImpl`、`seckill.lua` |
| 异步订单示例 | Kafka 发送调用及消费者示例，消费监听当前停用 | `SeckillVoucherConsumer`、`KafkaConfig` |

多级缓存默认保留原工程的 `mysql` 模式，可通过 `VOUCHER_CACHE_MODE` 切换为 `redis` 或 `caffeine`。商铺详情默认使用缓存空值路径，逻辑过期需要切换调用和预热后验证。

秒杀链路保留源工程状态：生产端有 Kafka 发送调用，但消费者监听注解和自定义容器配置被注释。该部分需要联调后才能作为完整异步下单能力使用。当前没有本仓库的性能提升数字。

## 本地准备

- Java 源码目标为 JDK 8；兼容性以实际构建结果为准。
- MySQL 8，建立独立的 `hmdp` 学习数据库。
- Redis 6.2+，附近商铺代码使用 `GEOSEARCH`。
- 验证消息链路时另备 Kafka；本仓库暂时保留停用的消费监听。
- 本仓库为后端工程，课程前端和 Nginx 资源需另外配置。

数据库脚本 `src/main/resources/db/hmdp.sql` 仅含表结构。导入独立学习库后，按需要添加自己的演示数据。

启动前配置环境变量：

```powershell
$env:DB_USER = "your_database_user"
$env:DB_PASSWORD = "your_local_password"
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
# Redis 启用认证时设置 REDIS_PASSWORD。
# 如需切换缓存模式，设置 VOUCHER_CACHE_MODE 为 mysql、redis 或 caffeine。
# 验证消息链路时设置 KAFKA_BOOTSTRAP_SERVERS。
```

```powershell
mvn -DskipTests package
java -jar target/neighborhood-review-0.0.1-SNAPSHOT.jar
```

服务默认端口为 `8081`。图片目录可通过 JVM 参数 `-Dreview.image-dir=...` 配置。详细配置见 `application.yaml`。

## 阅读与验证

按“请求入口 → Service → Redis 数据结构或 Lua → 数据库变化 → 异常情况”阅读代码。[项目现状](docs/STATUS.md) 记录现有实现与需要继续验证的问题，[整理记录](docs/CHANGES.md) 区分本次整理与来源工程已有内容。

本项目面向本地学习。对外部署前需要继续核对权限、输入与上传校验、消息序列化、事务和故障恢复。

## 运行回归测试

Java 调用参数的回归测试：

```text
mvn test
```

Redis 脚本的真实服务回归测试，仅使用 Python 标准库及本地 Redis 可执行文件：

```text
python scripts/test_rate_limiter.py --redis-server /path/to/redis-server
```

脚本启动一个独立、仅监听本机的临时 Redis 实例，测试完成后关闭，不连接现有 Redis。复现实验中的固定时间戳用于构造确定性的边界场景。
