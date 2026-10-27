package com.zwh.neighborhood.limiter;

import com.zwh.neighborhood.limiter.aop.RateLimiterAspect;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.test.util.ReflectionTestUtils;
import java.util.Collections;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class RateLimiterAspectTest {
    @Test
    void suppliesDistinctMembersToTheLuaScript() {
        StringRedisTemplate redis = mock(StringRedisTemplate.class);
        RateLimiterAspect aspect = new RateLimiterAspect();
        ReflectionTestUtils.setField(aspect, "stringRedisTemplate", redis);
        aspect.executeSlidingWindowScript("limiter:test", 1L, 10L);
        aspect.executeSlidingWindowScript("limiter:test", 1L, 10L);
        ArgumentCaptor<String> member = ArgumentCaptor.forClass(String.class);
        verify(redis, times(2)).execute(
                org.mockito.ArgumentMatchers.<RedisScript<Long>>any(),
                eq(Collections.singletonList("limiter:test")),
                eq("1"), eq("10"), anyString(), member.capture());
        String first = member.getAllValues().get(0);
        String second = member.getAllValues().get(1);
        assertNotNull(UUID.fromString(first));
        assertNotNull(UUID.fromString(second));
        assertNotEquals(first, second);
    }
}
