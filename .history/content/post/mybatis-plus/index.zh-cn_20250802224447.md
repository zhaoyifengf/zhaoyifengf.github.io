---
title: "Mybatisplus"
description: 
date: 2025-06-23T23:26:52+08:00
image: cover.png
math: 
license: 
hidden: false
comments: true
draft: true
categories:
    - Mybatisplus
tags:
    - Mybatisplus
---

## mybatisplus SQL执行流程

### 创建SqlSessionFactory

`mybatis-plus-boot-starter`包提供了`MybatisPlusAutoConfiguration`自动配置类，该自动配置类创建了SqlSessionFactory对象并交由Spring管理。

```
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({SqlSessionFactory.class, SqlSessionFactoryBean.class})
@ConditionalOnSingleCandidate(DataSource.class)
@EnableConfigurationProperties(MybatisPlusProperties.class)
@AutoConfigureAfter({DataSourceAutoConfiguration.class, MybatisPlusLanguageDriverAutoConfiguration.class})
public class MybatisPlusAutoConfiguration implements InitializingBean {

    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")
    @Bean
    @ConditionalOnMissingBean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        // TODO 使用 MybatisSqlSessionFactoryBean 而不是 SqlSessionFactoryBean
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        ........
    }
}
