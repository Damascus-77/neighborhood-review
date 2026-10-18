package com.zwh.neighborhood;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.retry.annotation.EnableRetry;

@MapperScan("com.zwh.neighborhood.mapper")
@EnableRetry
@EnableKafka
@SpringBootApplication
public class NeighborhoodReviewApplication {

    public static void main(String[] args) {
        SpringApplication.run(NeighborhoodReviewApplication.class, args);
    }

}
