# 邻里点评 Neighborhood Review

基于黑马点评课程及其扩展代码整理的本地生活服务后端学习仓库，围绕商铺查询、优惠券、用户登录和探店笔记，学习缓存、限流与秒杀并发处理。

当前仓库从本地使用的工程整理而来，保留课程来源与原作者注释。仓库名称、包名和文档已经统一，数据库和服务连接参数通过环境变量配置。当前验证范围与功能边界见 [项目现状](docs/STATUS.md)，来源见 [NOTICE](NOTICE.md)。

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
