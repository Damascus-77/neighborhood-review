package com.zwh.neighborhood.config;

import org.redisson.Redisson;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Redisson 配置
 *
 * 注意：Redisson 有自己的 Config，它【不会】读取 Spring Boot 的 spring.redis.* 自动配置，
 * 所以 Redis 的地址、密码必须在这里再写一遍（这里改成从 application.yaml 读取，避免硬编码）。
 */
@Configuration
public class RedissonConfig {

    @Value("${spring.redis.host:127.0.0.1}")
    private String host;

    @Value("${spring.redis.port:6379}")
    private int port;

    @Value("${spring.redis.password:}")
    private String password;

    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer()
                .setAddress("redis://" + host + ":" + port);
        // 本机 Redis 设了密码，必须带上；没设密码时留空即可
        if (password != null && !password.isEmpty()) {
            config.useSingleServer().setPassword(password);
        }
        // 创建RedissonClient对象
        return Redisson.create(config);
    }
}
