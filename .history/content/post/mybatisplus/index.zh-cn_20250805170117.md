---
title: "Mybatisplus与DataSource"
description: 
date: 2025-06-23T23:26:52+08:00
image: 
math: 
license: 
hidden: false
comments: true
draft: true
categories:
    - Mybatisplus DataSource
tags:
    - Mybatisplus DataSource
---

## mybatisplus SQL执行流程

### 服务启动时通过自动配置类创建MybatisSqlSessionFactoryBean
  

`mybatis-plus-boot-starter`包提供了`MybatisPlusAutoConfiguration`自动配置类，该自动配置类创建了MybatisSqlSessionFactoryBean对象并交由Spring管理，在创建MybatisSqlSessionFactoryBean时，sqlSessionFactory方法设置了DataScoure对象。自动配置类需要满足以下几个条件才会创建MybatisSqlSessionFactoryBean：

- MybatisPlusAutoConfiguration上的@ConditionalOnSingleCandidate指定了：被Spring管理的只有一个DataSource对象或者多个DataSource对指定了优先级（如通过@Primary注解指定）
- sqlSessionFactory方法上@ConditionalOnMissingBean指定了：只有在不存在SqlSessionFactory时才会创建MybatisSqlSessionFactoryBean对象

```
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({SqlSessionFactory.class, SqlSessionFactoryBean.class})
@ConditionalOnSingleCandidate(DataSource.class)
@EnableConfigurationProperties(MybatisPlusProperties.class)
@AutoConfigureAfter({DataSourceAutoConfiguration.class, MybatisPlusLanguageDriverAutoConfiguration.class})
public class MybatisPlusAutoConfiguration implements InitializingBean {

	@Bean
    @ConditionalOnMissingBean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        // TODO 使用 MybatisSqlSessionFactoryBean 而不是 SqlSessionFactoryBean
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
		.....
	}
}
```

###  Spring对事务进行代理
执行Mybatisplus DML语句前，Spring对要执行的方法（加了@Transactiontional注解）进行代理，代理执行的逻辑在TransactionAspectSupport中的invokeWithinTransaction方法中。整体调用流程如下

TransactionInterceptor#invoke -> TransactionAspectSupport#invokeWithinTransaction执行开启事务、执行业务逻辑、提交事务三个步骤。
- 开启事务
   - TransactionAspectSupport#invokeWithinTransaction -> determineTransactionManager
   - TransactionAspectSupport#determineTransactionManager -> createTransactionIfNecessary
   - TransactionAspectSupport#createTransactionIfNecessary -> AbstractPlatformTransactionManager#getTransaction，getTransaction方法先尝试获取事务再开启事务：
     - 获取事务
       - AbstractPlatformTransactionManager#getTransaction -> DataSourceTransactionManager#doGetTransaction（doGetTransaction是个抽象方法，具体逻辑由实现类提供，我们在这里只讨论DataSourceTransactionManager的实现逻辑）
       - DataSourceTransactionManager#doGetTransaction，该方法做下如下操作：
         - 创建DataSourceTransactionObject对象
         - TransactionSynchronizationManager.getResource方法获取DataSourceTransactionManager中dataScoure对象绑定的ConnectionHolder对象（用来存储connection对象）。TransactionSynchronizationManager中维护了一个ThreadLocal属性resources，这是一个以dataScoure对象为key、ConnectionHolder对象为值的Map。TransactionSynchronizationManager用来管理每个线程中和dataScoure对象绑定的connection对象。
         - 将上一步获取的ConnectionHolder设置到DataSourceTransactionObject中
     - 开启事务
       - AbstractPlatformTransactionManager#getTransactio -> DataSourceTransactionManager#startTransaction
		- DataSourceTransactionManager#startTransactionn -> doBegin方法，实现如下操作（DataSourceTransactionManager#doGetTransaction对象返回的DataSourceTransactionObject中的ConnectionHolder为空时执行该步骤）：
         - 通过DataSourceTransactionManager中dataScoure对象获取connection
         - 将connection包装为ConnectionHolder对象
         - 通过TransactionSynchronizationManager.bindResource将ConnectionHolder对象和connection对象绑定并设置上面提到的TransactionSynchronizationManager中的ThreadLocal属性resources中
 - 执行业务逻辑 
   - TransactionAspectSupport#invokeWithinTransaction执行被代理方法，mybatisplus中的方法也会在在此被执行，具体流程我们方法下一个部分讨论。
 - 提交事务

```
@SuppressWarnings("serial")
public class TransactionInterceptor extends TransactionAspectSupport implements MethodInterceptor, Serializable {

	@Override
	@Nullable
	public Object invoke(MethodInvocation invocation) throws Throwable {
		// Work out the target class: may be {@code null}.
		// The TransactionAttributeSource should be passed the target class
		// as well as the method, which may be from an interface.
		Class<?> targetClass = (invocation.getThis() != null ? AopUtils.getTargetClass(invocation.getThis()) : null);

		// Adapt to TransactionAspectSupport's invokeWithinTransaction...
		return invokeWithinTransaction(invocation.getMethod(), targetClass, invocation::proceed);
	}
}

public abstract class TransactionAspectSupport implements BeanFactoryAware, InitializingBean {
	@Nullable
	protected Object invokeWithinTransaction(Method method, @Nullable Class<?> targetClass,
			final InvocationCallback invocation) throws Throwable {

		// If the transaction attribute is null, the method is non-transactional.
		TransactionAttributeSource tas = getTransactionAttributeSource();
		final TransactionAttribute txAttr = (tas != null ? tas.getTransactionAttribute(method, targetClass) : null);
		final TransactionManager tm = determineTransactionManager(txAttr);

		........ // 响应式事务处理逻辑

		PlatformTransactionManager ptm = asPlatformTransactionManager(tm);
		final String joinpointIdentification = methodIdentification(method, targetClass, txAttr);

		if (txAttr == null || !(ptm instanceof CallbackPreferringPlatformTransactionManager)) {
			// Standard transaction demarcation with getTransaction and commit/rollback calls.
			TransactionInfo txInfo = createTransactionIfNecessary(ptm, txAttr, joinpointIdentification);

			Object retVal;
			try {
				// This is an around advice: Invoke the next interceptor in the chain.
				// This will normally result in a target object being invoked.
				retVal = invocation.proceedWithInvocation();
			}
			catch (Throwable ex) {
				// target invocation exception
				completeTransactionAfterThrowing(txInfo, ex);
				throw ex;
			}
			finally {
				cleanupTransactionInfo(txInfo);
			}

			if (retVal != null && vavrPresent && VavrDelegate.isVavrTry(retVal)) {
				// Set rollback-only in case of Vavr failure matching our rollback rules...
				TransactionStatus status = txInfo.getTransactionStatus();
				if (status != null && txAttr != null) {
					retVal = VavrDelegate.evaluateTryFailure(retVal, txAttr, status);
				}
			}

			commitTransactionAfterReturning(txInfo);
			return retVal;
		}else {
			...... // 非回调事务处理逻辑
	}

	protected TransactionInfo createTransactionIfNecessary(@Nullable PlatformTransactionManager tm,
			@Nullable TransactionAttribute txAttr, final String joinpointIdentification) {
		...........
		TransactionStatus status = null;
		if (txAttr != null) {
			if (tm != null) {
				status = tm.getTransaction(txAttr);
			}
			.......
		}
		...........
	}
}

public abstract class AbstractPlatformTransactionManager implements PlatformTransactionManager, Serializable {
	@Override
	public final TransactionStatus getTransaction(@Nullable TransactionDefinition definition)
			throws TransactionException {
		...........................
		
		Object transaction = doGetTransaction();
		boolean debugEnabled = logger.isDebugEnabled();

		
		// No existing transaction found -> check propagation behavior to find out how to proceed.
		if (def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_MANDATORY) {
			.............
		}
		else if (def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRED ||
				def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW ||
				def.getPropagationBehavior() == TransactionDefinition.PROPAGATION_NESTED) {
			SuspendedResourcesHolder suspendedResources = suspend(null);
			...............
			try {
				return startTransaction(def, transaction, debugEnabled, suspendedResources);
			}
			catch (RuntimeException | Error ex) {
				
			}
		}
		else {
			.........
		}
	}

	/**
	 * Start a new transaction.
	 */
	private TransactionStatus startTransaction(TransactionDefinition definition, Object transaction,
			boolean debugEnabled, @Nullable SuspendedResourcesHolder suspendedResources) {

		boolean newSynchronization = (getTransactionSynchronization() != SYNCHRONIZATION_NEVER);
		DefaultTransactionStatus status = newTransactionStatus(
				definition, transaction, true, newSynchronization, debugEnabled, suspendedResources);
		doBegin(transaction, definition);
		prepareSynchronization(status, definition);
		return status;
	}
}

public class DataSourceTransactionManager extends AbstractPlatformTransactionManager
		implements ResourceTransactionManager, InitializingBean {
	protected Object doGetTransaction() {
		DataSourceTransactionObject txObject = new DataSourceTransactionObject();
		txObject.setSavepointAllowed(isNestedTransactionAllowed());
		ConnectionHolder conHolder =
				(ConnectionHolder) TransactionSynchronizationManager.getResource(obtainDataSource());
		txObject.setConnectionHolder(conHolder, false);
		return txObject;
	}

	protected void doBegin(Object transaction, TransactionDefinition definition) {
		DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
		Connection con = null;

		try {
			if (!txObject.hasConnectionHolder() ||
					txObject.getConnectionHolder().isSynchronizedWithTransaction()) {
				Connection newCon = obtainDataSource().getConnection();
				if (logger.isDebugEnabled()) {
					logger.debug("Acquired Connection [" + newCon + "] for JDBC transaction");
				}
				txObject.setConnectionHolder(new ConnectionHolder(newCon), true);
			}

			txObject.getConnectionHolder().setSynchronizedWithTransaction(true);
			con = txObject.getConnectionHolder().getConnection();

			Integer previousIsolationLevel = DataSourceUtils.prepareConnectionForTransaction(con, definition);
			txObject.setPreviousIsolationLevel(previousIsolationLevel);
			txObject.setReadOnly(definition.isReadOnly());

			// Switch to manual commit if necessary. This is very expensive in some JDBC drivers,
			// so we don't want to do it unnecessarily (for example if we've explicitly
			// configured the connection pool to set it already).
			if (con.getAutoCommit()) {
				txObject.setMustRestoreAutoCommit(true);
				if (logger.isDebugEnabled()) {
					logger.debug("Switching JDBC Connection [" + con + "] to manual commit");
				}
				con.setAutoCommit(false);
			}

			prepareTransactionalConnection(con, definition);
			txObject.getConnectionHolder().setTransactionActive(true);

			int timeout = determineTimeout(definition);
			if (timeout != TransactionDefinition.TIMEOUT_DEFAULT) {
				txObject.getConnectionHolder().setTimeoutInSeconds(timeout);
			}

			// Bind the connection holder to the thread.
			if (txObject.isNewConnectionHolder()) {
				TransactionSynchronizationManager.bindResource(obtainDataSource(), txObject.getConnectionHolder());
			}
		}

		catch (Throwable ex) {
			if (txObject.isNewConnectionHolder()) {
				DataSourceUtils.releaseConnection(con, obtainDataSource());
				txObject.setConnectionHolder(null, false);
			}
			throw new CannotCreateTransactionException("Could not open JDBC Connection for transaction", ex);
		}
	}
}
```

## 执行mybatisplus DML与Select语句

以调用IService的saveBatch方法为例，其最初调用链路如下ServiceImpl#saveBatch -> ServiceImpl#executeBatch -> SqlHelper#executeBatch，
执行步骤如下：

- 获取SqlSessionFactory

	SqlHelper#executeBatch调用sqlSessionFactory方法，sqlSessionFactory对象中持有DataSource对象的引用。

- 调用上面一步获取的SqlSessionFactory的openSession方法（这里以DefaultSqlSessionFactory加以说明），需要注意的事这里的Transaction对象并不参与事务的执行，只是用来管理数据源，该方法执行了如下步骤：

	- 创建TransactionFactory对象
	- 通过TransactionFactory对象创建Transaction对象，并传入从configure（SqlSessionFactory持有）对象中获取的dataScoure对象
	- 创建Executor对象并传入Transaction对象
	- 创建DefaultSqlSession对象并传入Executor对象
  ```
  private SqlSession openSessionFromDataSource(ExecutorType execType, TransactionIsolationLevel level, boolean autoCommit) {
		Transaction tx = null;
		try {
		final Environment environment = configuration.getEnvironment();
		final TransactionFactory transactionFactory = getTransactionFactoryFromEnvironment(environment);
		tx = transactionFactory.newTransaction(environment.getDataSource(), level, autoCommit);
		final Executor executor = configuration.newExecutor(tx, execType);
		return new DefaultSqlSession(configuration, executor, autoCommit);
		} catch (Exception e) {
		closeTransaction(tx); // may have fetched a connection so lets call close()
		throw ExceptionFactory.wrapException("Error opening session.  Cause: " + e, e);
		} finally {
		ErrorContext.instance().reset();
		}
  }
  ```
	

- 调用SqlSession的insert方法
  - 调用链路SqlSession#insert -> SqlSession#update -> BaseExecutor#update -> BatchExecutor#doUpdate，BatchExecutor#doUpdate执行了如下步骤：
    - 获取Connection，调用BaseExecutor#getConnection -> Transaction.getConnection -> SpringManagedTransaction.getConnection -> SpringManagedTransaction.openConnection -> DataSourceUtils.getConnection -> DataSourceUtils.doGetConnection，从下面的代码可知道如果当前数据源绑定了Connection则获取绑定的Connection，如果没有绑定则调用DataScoure对象的getConnection方法获取新的connection方法
	```
	public static Connection doGetConnection(DataSource dataSource) throws SQLException {
		.......
		ConnectionHolder conHolder = (ConnectionHolder) TransactionSynchronizationManager.getResource(dataSource);
		if (conHolder != null && (conHolder.hasConnection() || conHolder.isSynchronizedWithTransaction())) {
			conHolder.requested();
			if (!conHolder.hasConnection()) {
				logger.debug("Fetching resumed JDBC Connection from DataSource");
				conHolder.setConnection(fetchConnection(dataSource));
			}
			return conHolder.getConnection();
		}
		// Else we either got no holder or an empty thread-bound holder here.

		logger.debug("Fetching JDBC Connection from DataSource");
		Connection con = fetchConnection(dataSource);
		........
		return con;
	}

	private static Connection fetchConnection(DataSource dataSource) throws SQLException {
		Connection con = dataSource.getConnection();
		if (con == null) {
			throw new IllegalStateException("DataSource returned null from getConnection(): " + dataSource);
		}
		return con;
	}
	```
    - 准备Statement，设置Connection为上一步获取的Connection
    - 执行SQL语句
  
## DataScoure：数据库链接的管理者

不论是在Spring事务还是mybatisplus执行SQL语句前获取connection，都会调用DataScoure#getConnection方法。如下，DataScoure只提供了两个获取connection方法，由此可知DataScoure最主要的功能就是进行Connection的管理。对DataSource的getConnection方法提供不同的实现可以提供不同的功能，最典型的莫过于连接池和动态数据源。

```
public interface DataSource  extends CommonDataSource, Wrapper {

  Connection getConnection() throws SQLException;

  Connection getConnection(String username, String password) throws SQLException;
}
```

### 连接池

我们以HikariCP为例，先介绍其在SpringBoot项目中如何使用，再介绍如何通过其获取Connection

- SpringBoot集成HikariCP

	- yaml配置
	```
	spring:
		datasource:
		type: com.zaxxer.hikari.HikariDataSource
		url: jdbc:mysql://localhost:3306/test?useSSL=false
		username: root
		password: 123456
		driver-class-name: com.mysql.cj.jdbc.Driver
		hikari:
			pool-name: MyHikariCP
			minimum-idle: 5
			maximum-pool-size: 20
			idle-timeout: 600000
			max-lifetime: 1800000
			connection-timeout: 30000
			connection-test-query: SELECT 1
	```

	- 数据源属性类
	```
	@ConfigurationProperties(prefix = "spring.datasource")
	public class DataSourceProperties implements BeanClassLoaderAware, InitializingBean {
		private ClassLoader classLoader;
		private String name;
		private boolean generateUniqueName = true;
		private Class<? extends DataSource> type;
		private String driverClassName;
		private String url;
		private String username;
		private String password;
	}
	```
	- Springboot自动配置

		当我们在yaml文件中指定了`type: com.zaxxer.hikari.HikariDataSource`满足了自动配置类`@ConditionalOnProperty(name = "spring.datasource.type", havingValue = "com.zaxxer.hikari.HikariDataSource",matchIfMissing = true)`的条件，创建HikariDataSource对象并交由Spring管理。
	```
	stract class DataSourceConfiguration {
		@Configuration(proxyBeanMethods = false)
		@ConditionalOnClass(HikariDataSource.class)
		@ConditionalOnMissingBean(DataSource.class)
		@ConditionalOnProperty(name = "spring.datasource.type", havingValue = "com.zaxxer.hikari.HikariDataSource",
				matchIfMissing = true)
		static class Hikari {

			@Bean
			@ConfigurationProperties(prefix = "spring.datasource.hikari")
			HikariDataSource dataSource(DataSourceProperties properties) {
				HikariDataSource dataSource = createDataSource(properties, HikariDataSource.class);
				if (StringUtils.hasText(properties.getName())) {
					dataSource.setPoolName(properties.getName());
				}
				return dataSource;
			}
		}
	}
	```
- HikariDataSource实现数据库链接管理
	在没有创建其他数据源的情况下，HikariDataSource会被注入Mybatisplus的MybatisSqlSessionFactoryBean并在执行SQL语句前被获取，HikariDataSource只需要重写getConnection方法就可实现对数据库连接的管理。如下代码，HikariDataSource获取数据库连接的功能最终委托给了HikariPool。

	```
	public class HikariDataSource extends HikariConfig implements DataSource, Closeable
	{
		private static final Logger LOGGER = LoggerFactory.getLogger(HikariDataSource.class);
		private final AtomicBoolean isShutdown = new AtomicBoolean();
		private final HikariPool fastPathPool;
		private volatile HikariPool pool;

		public HikariDataSource()
		{
			super();
			fastPathPool = null;
		}

		public HikariDataSource(HikariConfig configuration)
		{
			configuration.validate();
			configuration.copyStateTo(this);

			LOGGER.info("{} - Starting...", configuration.getPoolName());
			pool = fastPathPool = new HikariPool(this);
			LOGGER.info("{} - Start completed.", configuration.getPoolName());

			this.seal();
		}

		@Override
		public Connection getConnection() throws SQLException
		{
			if (isClosed()) {
				throw new SQLException("HikariDataSource " + this + " has been closed.");
			}

			if (fastPathPool != null) {
				return fastPathPool.getConnection();
			}

			// See http://en.wikipedia.org/wiki/Double-checked_locking#Usage_in_Java
			HikariPool result = pool;
			if (result == null) {
				synchronized (this) {
					result = pool;
					if (result == null) {
					validate();
					LOGGER.info("{} - Starting...", getPoolName());
					try {
						pool = result = new HikariPool(this);
						this.seal();
					}
					catch (PoolInitializationException pie) {
						if (pie.getCause() instanceof SQLException) {
							throw (SQLException) pie.getCause();
						}
						else {
							throw pie;
						}
					}
					LOGGER.info("{} - Start completed.", getPoolName());
					}
				}
			}
			return result.getConnection();
		}
	}
	```

	HikariPool核心代码如下，
	```
public final class HikariPool extends PoolBase implements HikariPoolMXBean, IBagStateListener
{
   private final Logger logger = LoggerFactory.getLogger(HikariPool.class);

   public static final int POOL_NORMAL = 0;
   public static final int POOL_SUSPENDED = 1;
   public static final int POOL_SHUTDOWN = 2;

   public volatile int poolState;

   private final long aliveBypassWindowMs = Long.getLong("com.zaxxer.hikari.aliveBypassWindowMs", MILLISECONDS.toMillis(500));
   private final long housekeepingPeriodMs = Long.getLong("com.zaxxer.hikari.housekeeping.periodMs", SECONDS.toMillis(30));

   private static final String EVICTED_CONNECTION_MESSAGE = "(connection was evicted)";
   private static final String DEAD_CONNECTION_MESSAGE = "(connection is dead)";

   private final PoolEntryCreator poolEntryCreator = new PoolEntryCreator(null /*logging prefix*/);
   private final PoolEntryCreator postFillPoolEntryCreator = new PoolEntryCreator("After adding ");
   private final Collection<Runnable> addConnectionQueueReadOnlyView;
   private final ThreadPoolExecutor addConnectionExecutor;
   private final ThreadPoolExecutor closeConnectionExecutor;

   private final ConcurrentBag<PoolEntry> connectionBag;

   private final ProxyLeakTaskFactory leakTaskFactory;
   private final SuspendResumeLock suspendResumeLock;

   private final ScheduledExecutorService houseKeepingExecutorService;
   private ScheduledFuture<?> houseKeeperTask;

   /**
    * Construct a HikariPool with the specified configuration.
    *
    * @param config a HikariConfig instance
    */
   public HikariPool(final HikariConfig config)
   {
      super(config);

      this.connectionBag = new ConcurrentBag<>(this);
      this.suspendResumeLock = config.isAllowPoolSuspension() ? new SuspendResumeLock() : SuspendResumeLock.FAUX_LOCK;

      this.houseKeepingExecutorService = initializeHouseKeepingExecutorService();

      checkFailFast();

      if (config.getMetricsTrackerFactory() != null) {
         setMetricsTrackerFactory(config.getMetricsTrackerFactory());
      }
      else {
         setMetricRegistry(config.getMetricRegistry());
      }

      setHealthCheckRegistry(config.getHealthCheckRegistry());

      handleMBeans(this, true);

      ThreadFactory threadFactory = config.getThreadFactory();

      final int maxPoolSize = config.getMaximumPoolSize();
      LinkedBlockingQueue<Runnable> addConnectionQueue = new LinkedBlockingQueue<>(maxPoolSize);
      this.addConnectionQueueReadOnlyView = unmodifiableCollection(addConnectionQueue);
      this.addConnectionExecutor = createThreadPoolExecutor(addConnectionQueue, poolName + " connection adder", threadFactory, new ThreadPoolExecutor.DiscardOldestPolicy());
      this.closeConnectionExecutor = createThreadPoolExecutor(maxPoolSize, poolName + " connection closer", threadFactory, new ThreadPoolExecutor.CallerRunsPolicy());

      this.leakTaskFactory = new ProxyLeakTaskFactory(config.getLeakDetectionThreshold(), houseKeepingExecutorService);

      this.houseKeeperTask = houseKeepingExecutorService.scheduleWithFixedDelay(new HouseKeeper(), 100L, housekeepingPeriodMs, MILLISECONDS);

      if (Boolean.getBoolean("com.zaxxer.hikari.blockUntilFilled") && config.getInitializationFailTimeout() > 1) {
         addConnectionExecutor.setCorePoolSize(Math.min(16, Runtime.getRuntime().availableProcessors()));
         addConnectionExecutor.setMaximumPoolSize(Math.min(16, Runtime.getRuntime().availableProcessors()));

         final long startTime = currentTime();
         while (elapsedMillis(startTime) < config.getInitializationFailTimeout() && getTotalConnections() < config.getMinimumIdle()) {
            quietlySleep(MILLISECONDS.toMillis(100));
         }

         addConnectionExecutor.setCorePoolSize(1);
         addConnectionExecutor.setMaximumPoolSize(1);
      }
   }

   /**
    * Get a connection from the pool, or timeout after connectionTimeout milliseconds.
    *
    * @return a java.sql.Connection instance
    * @throws SQLException thrown if a timeout occurs trying to obtain a connection
    */
   public Connection getConnection() throws SQLException
   {
      return getConnection(connectionTimeout);
   }

   /**
    * Get a connection from the pool, or timeout after the specified number of milliseconds.
    *
    * @param hardTimeout the maximum time to wait for a connection from the pool
    * @return a java.sql.Connection instance
    * @throws SQLException thrown if a timeout occurs trying to obtain a connection
    */
   public Connection getConnection(final long hardTimeout) throws SQLException
   {
      suspendResumeLock.acquire();
      final long startTime = currentTime();

      try {
         long timeout = hardTimeout;
         do {
            PoolEntry poolEntry = connectionBag.borrow(timeout, MILLISECONDS);
            if (poolEntry == null) {
               break; // We timed out... break and throw exception
            }

            final long now = currentTime();
            if (poolEntry.isMarkedEvicted() || (elapsedMillis(poolEntry.lastAccessed, now) > aliveBypassWindowMs && !isConnectionAlive(poolEntry.connection))) {
               closeConnection(poolEntry, poolEntry.isMarkedEvicted() ? EVICTED_CONNECTION_MESSAGE : DEAD_CONNECTION_MESSAGE);
               timeout = hardTimeout - elapsedMillis(startTime);
            }
            else {
               metricsTracker.recordBorrowStats(poolEntry, startTime);
               return poolEntry.createProxyConnection(leakTaskFactory.schedule(poolEntry), now);
            }
         } while (timeout > 0L);

         metricsTracker.recordBorrowTimeoutStats(startTime);
         throw createTimeoutException(startTime);
      }
      catch (InterruptedException e) {
         Thread.currentThread().interrupt();
         throw new SQLException(poolName + " - Interrupted during connection acquisition", e);
      }
      finally {
         suspendResumeLock.release();
      }
   }

   /**
    * Shutdown the pool, closing all idle connections and aborting or closing
    * active connections.
    *
    * @throws InterruptedException thrown if the thread is interrupted during shutdown
    */
   public synchronized void shutdown() throws InterruptedException
   {
      try {
         poolState = POOL_SHUTDOWN;

         if (addConnectionExecutor == null) { // pool never started
            return;
         }

         logPoolState("Before shutdown ");

         if (houseKeeperTask != null) {
            houseKeeperTask.cancel(false);
            houseKeeperTask = null;
         }

         softEvictConnections();

         addConnectionExecutor.shutdown();
         addConnectionExecutor.awaitTermination(getLoginTimeout(), SECONDS);

         destroyHouseKeepingExecutorService();

         connectionBag.close();

         final ExecutorService assassinExecutor = createThreadPoolExecutor(config.getMaximumPoolSize(), poolName + " connection assassinator",
                                                                           config.getThreadFactory(), new ThreadPoolExecutor.CallerRunsPolicy());
         try {
            final long start = currentTime();
            do {
               abortActiveConnections(assassinExecutor);
               softEvictConnections();
            } while (getTotalConnections() > 0 && elapsedMillis(start) < SECONDS.toMillis(10));
         }
         finally {
            assassinExecutor.shutdown();
            assassinExecutor.awaitTermination(10L, SECONDS);
         }

         shutdownNetworkTimeoutExecutor();
         closeConnectionExecutor.shutdown();
         closeConnectionExecutor.awaitTermination(10L, SECONDS);
      }
      finally {
         logPoolState("After shutdown ");
         handleMBeans(this, false);
         metricsTracker.close();
      }
   }

   /**
    * Evict a Connection from the pool.
    *
    * @param connection the Connection to evict (actually a {@link ProxyConnection})
    */
   public void evictConnection(Connection connection)
   {
      ProxyConnection proxyConnection = (ProxyConnection) connection;
      proxyConnection.cancelLeakTask();

      try {
         softEvictConnection(proxyConnection.getPoolEntry(), "(connection evicted by user)", !connection.isClosed() /* owner */);
      }
      catch (SQLException e) {
         // unreachable in HikariCP, but we're still forced to catch it
      }
   }

   /**
    * Set a metrics registry to be used when registering metrics collectors.  The HikariDataSource prevents this
    * method from being called more than once.
    *
    * @param metricRegistry the metrics registry instance to use
    */
   public void setMetricRegistry(Object metricRegistry)
   {
      if (metricRegistry != null && safeIsAssignableFrom(metricRegistry, "com.codahale.metrics.MetricRegistry")) {
         setMetricsTrackerFactory(new CodahaleMetricsTrackerFactory((MetricRegistry) metricRegistry));
      }
      else if (metricRegistry != null && safeIsAssignableFrom(metricRegistry, "io.micrometer.core.instrument.MeterRegistry")) {
         setMetricsTrackerFactory(new MicrometerMetricsTrackerFactory((MeterRegistry) metricRegistry));
      }
      else {
         setMetricsTrackerFactory(null);
      }
   }

   /**
    * Set the MetricsTrackerFactory to be used to create the IMetricsTracker instance used by the pool.
    *
    * @param metricsTrackerFactory an instance of a class that subclasses MetricsTrackerFactory
    */
   public void setMetricsTrackerFactory(MetricsTrackerFactory metricsTrackerFactory)
   {
      if (metricsTrackerFactory != null) {
         this.metricsTracker = new MetricsTrackerDelegate(metricsTrackerFactory.create(config.getPoolName(), getPoolStats()));
      }
      else {
         this.metricsTracker = new NopMetricsTrackerDelegate();
      }
   }

   /**
    * Set the health check registry to be used when registering health checks.  Currently only Codahale health
    * checks are supported.
    *
    * @param healthCheckRegistry the health check registry instance to use
    */
   public void setHealthCheckRegistry(Object healthCheckRegistry)
   {
      if (healthCheckRegistry != null) {
         CodahaleHealthChecker.registerHealthChecks(this, config, (HealthCheckRegistry) healthCheckRegistry);
      }
   }

   // ***********************************************************************
   //                        IBagStateListener callback
   // ***********************************************************************

   /** {@inheritDoc} */
   @Override
   public void addBagItem(final int waiting)
   {
      final boolean shouldAdd = waiting - addConnectionQueueReadOnlyView.size() >= 0; // Yes, >= is intentional.
      if (shouldAdd) {
         addConnectionExecutor.submit(poolEntryCreator);
      }
      else {
         logger.debug("{} - Add connection elided, waiting {}, queue {}", poolName, waiting, addConnectionQueueReadOnlyView.size());
      }
   }

   // ***********************************************************************
   //                        HikariPoolMBean methods
   // ***********************************************************************

   /** {@inheritDoc} */
   @Override
   public int getActiveConnections()
   {
      return connectionBag.getCount(STATE_IN_USE);
   }

   /** {@inheritDoc} */
   @Override
   public int getIdleConnections()
   {
      return connectionBag.getCount(STATE_NOT_IN_USE);
   }

   /** {@inheritDoc} */
   @Override
   public int getTotalConnections()
   {
      return connectionBag.size();
   }

   /** {@inheritDoc} */
   @Override
   public int getThreadsAwaitingConnection()
   {
      return connectionBag.getWaitingThreadCount();
   }

   /** {@inheritDoc} */
   @Override
   public void softEvictConnections()
   {
      connectionBag.values().forEach(poolEntry -> softEvictConnection(poolEntry, "(connection evicted)", false /* not owner */));
   }

   /** {@inheritDoc} */
   @Override
   public synchronized void suspendPool()
   {
      if (suspendResumeLock == SuspendResumeLock.FAUX_LOCK) {
         throw new IllegalStateException(poolName + " - is not suspendable");
      }
      else if (poolState != POOL_SUSPENDED) {
         suspendResumeLock.suspend();
         poolState = POOL_SUSPENDED;
      }
   }

   /** {@inheritDoc} */
   @Override
   public synchronized void resumePool()
   {
      if (poolState == POOL_SUSPENDED) {
         poolState = POOL_NORMAL;
         fillPool();
         suspendResumeLock.resume();
      }
   }

   // ***********************************************************************
   //                           Package methods
   // ***********************************************************************

   /**
    * Log the current pool state at debug level.
    *
    * @param prefix an optional prefix to prepend the log message
    */
   void logPoolState(String... prefix)
   {
      if (logger.isDebugEnabled()) {
         logger.debug("{} - {}stats (total={}, active={}, idle={}, waiting={})",
                      poolName, (prefix.length > 0 ? prefix[0] : ""),
                      getTotalConnections(), getActiveConnections(), getIdleConnections(), getThreadsAwaitingConnection());
      }
   }

   /**
    * Recycle PoolEntry (add back to the pool)
    *
    * @param poolEntry the PoolEntry to recycle
    */
   @Override
   void recycle(final PoolEntry poolEntry)
   {
      metricsTracker.recordConnectionUsage(poolEntry);

      connectionBag.requite(poolEntry);
   }

   /**
    * Permanently close the real (underlying) connection (eat any exception).
    *
    * @param poolEntry poolEntry having the connection to close
    * @param closureReason reason to close
    */
   void closeConnection(final PoolEntry poolEntry, final String closureReason)
   {
      if (connectionBag.remove(poolEntry)) {
         final Connection connection = poolEntry.close();
         closeConnectionExecutor.execute(() -> {
            quietlyCloseConnection(connection, closureReason);
            if (poolState == POOL_NORMAL) {
               fillPool();
            }
         });
      }
   }

   @SuppressWarnings("unused")
   int[] getPoolStateCounts()
   {
      return connectionBag.getStateCounts();
   }


   // ***********************************************************************
   //                           Private methods
   // ***********************************************************************

   /**
    * Creating new poolEntry.  If maxLifetime is configured, create a future End-of-life task with 2.5% variance from
    * the maxLifetime time to ensure there is no massive die-off of Connections in the pool.
    */
   private PoolEntry createPoolEntry()
   {
      try {
         final PoolEntry poolEntry = newPoolEntry();

         final long maxLifetime = config.getMaxLifetime();
         if (maxLifetime > 0) {
            // variance up to 2.5% of the maxlifetime
            final long variance = maxLifetime > 10_000 ? ThreadLocalRandom.current().nextLong( maxLifetime / 40 ) : 0;
            final long lifetime = maxLifetime - variance;
            poolEntry.setFutureEol(houseKeepingExecutorService.schedule(
               () -> {
                  if (softEvictConnection(poolEntry, "(connection has passed maxLifetime)", false /* not owner */)) {
                     addBagItem(connectionBag.getWaitingThreadCount());
                  }
               },
               lifetime, MILLISECONDS));
         }

         return poolEntry;
      }
      catch (ConnectionSetupException e) {
         if (poolState == POOL_NORMAL) { // we check POOL_NORMAL to avoid a flood of messages if shutdown() is running concurrently
            logger.error("{} - Error thrown while acquiring connection from data source", poolName, e.getCause());
            lastConnectionFailure.set(e);
         }
      }
      catch (Exception e) {
         if (poolState == POOL_NORMAL) { // we check POOL_NORMAL to avoid a flood of messages if shutdown() is running concurrently
            logger.debug("{} - Cannot acquire connection from data source", poolName, e);
         }
      }

      return null;
   }

   /**
    * Fill pool up from current idle connections (as they are perceived at the point of execution) to minimumIdle connections.
    */
   private synchronized void fillPool()
   {
      final int connectionsToAdd = Math.min(config.getMaximumPoolSize() - getTotalConnections(), config.getMinimumIdle() - getIdleConnections())
                                   - addConnectionQueueReadOnlyView.size();
      if (connectionsToAdd <= 0) logger.debug("{} - Fill pool skipped, pool is at sufficient level.", poolName);

      for (int i = 0; i < connectionsToAdd; i++) {
         addConnectionExecutor.submit((i < connectionsToAdd - 1) ? poolEntryCreator : postFillPoolEntryCreator);
      }
   }

   /**
    * Attempt to abort or close active connections.
    *
    * @param assassinExecutor the ExecutorService to pass to Connection.abort()
    */
   private void abortActiveConnections(final ExecutorService assassinExecutor)
   {
      for (PoolEntry poolEntry : connectionBag.values(STATE_IN_USE)) {
         Connection connection = poolEntry.close();
         try {
            connection.abort(assassinExecutor);
         }
         catch (Throwable e) {
            quietlyCloseConnection(connection, "(connection aborted during shutdown)");
         }
         finally {
            connectionBag.remove(poolEntry);
         }
      }
   }

   /**
    * If initializationFailFast is configured, check that we have DB connectivity.
    *
    * @throws PoolInitializationException if fails to create or validate connection
    * @see HikariConfig#setInitializationFailTimeout(long)
    */
   private void checkFailFast()
   {
      final long initializationTimeout = config.getInitializationFailTimeout();
      if (initializationTimeout < 0) {
         return;
      }

      final long startTime = currentTime();
      do {
         final PoolEntry poolEntry = createPoolEntry();
         if (poolEntry != null) {
            if (config.getMinimumIdle() > 0) {
               connectionBag.add(poolEntry);
               logger.debug("{} - Added connection {}", poolName, poolEntry.connection);
            }
            else {
               quietlyCloseConnection(poolEntry.close(), "(initialization check complete and minimumIdle is zero)");
            }

            return;
         }

         if (getLastConnectionFailure() instanceof ConnectionSetupException) {
            throwPoolInitializationException(getLastConnectionFailure().getCause());
         }

         quietlySleep(SECONDS.toMillis(1));
      } while (elapsedMillis(startTime) < initializationTimeout);

      if (initializationTimeout > 0) {
         throwPoolInitializationException(getLastConnectionFailure());
      }
   }

   /**
    * Log the Throwable that caused pool initialization to fail, and then throw a PoolInitializationException with
    * that cause attached.
    *
    * @param t the Throwable that caused the pool to fail to initialize (possibly null)
    */
   private void throwPoolInitializationException(Throwable t)
   {
      logger.error("{} - Exception during pool initialization.", poolName, t);
      destroyHouseKeepingExecutorService();
      throw new PoolInitializationException(t);
   }

   /**
    * "Soft" evict a Connection (/PoolEntry) from the pool.  If this method is being called by the user directly
    * through {@link com.zaxxer.hikari.HikariDataSource#evictConnection(Connection)} then {@code owner} is {@code true}.
    *
    * If the caller is the owner, or if the Connection is idle (i.e. can be "reserved" in the {@link ConcurrentBag}),
    * then we can close the connection immediately.  Otherwise, we leave it "marked" for eviction so that it is evicted
    * the next time someone tries to acquire it from the pool.
    *
    * @param poolEntry the PoolEntry (/Connection) to "soft" evict from the pool
    * @param reason the reason that the connection is being evicted
    * @param owner true if the caller is the owner of the connection, false otherwise
    * @return true if the connection was evicted (closed), false if it was merely marked for eviction
    */
   private boolean softEvictConnection(final PoolEntry poolEntry, final String reason, final boolean owner)
   {
      poolEntry.markEvicted();
      if (owner || connectionBag.reserve(poolEntry)) {
         closeConnection(poolEntry, reason);
         return true;
      }

      return false;
   }

   /**
    * Create/initialize the Housekeeping service {@link ScheduledExecutorService}.  If the user specified an Executor
    * to be used in the {@link HikariConfig}, then we use that.  If no Executor was specified (typical), then create
    * an Executor and configure it.
    *
    * @return either the user specified {@link ScheduledExecutorService}, or the one we created
    */
   private ScheduledExecutorService initializeHouseKeepingExecutorService()
   {
      if (config.getScheduledExecutor() == null) {
         final ThreadFactory threadFactory = Optional.ofNullable(config.getThreadFactory()).orElseGet(() -> new DefaultThreadFactory(poolName + " housekeeper", true));
         final ScheduledThreadPoolExecutor executor = new ScheduledThreadPoolExecutor(1, threadFactory, new ThreadPoolExecutor.DiscardPolicy());
         executor.setExecuteExistingDelayedTasksAfterShutdownPolicy(false);
         executor.setRemoveOnCancelPolicy(true);
         return executor;
      }
      else {
         return config.getScheduledExecutor();
      }
   }

   /**
    * Destroy (/shutdown) the Housekeeping service Executor, if it was the one that we created.
    */
   private void destroyHouseKeepingExecutorService()
   {
      if (config.getScheduledExecutor() == null) {
         houseKeepingExecutorService.shutdownNow();
      }
   }

   /**
    * Create a PoolStats instance that will be used by metrics tracking, with a pollable resolution of 1 second.
    *
    * @return a PoolStats instance
    */
   private PoolStats getPoolStats()
   {
      return new PoolStats(SECONDS.toMillis(1)) {
         @Override
         protected void update() {
            this.pendingThreads = HikariPool.this.getThreadsAwaitingConnection();
            this.idleConnections = HikariPool.this.getIdleConnections();
            this.totalConnections = HikariPool.this.getTotalConnections();
            this.activeConnections = HikariPool.this.getActiveConnections();
            this.maxConnections = config.getMaximumPoolSize();
            this.minConnections = config.getMinimumIdle();
         }
      };
   }

   /**
    * Create a timeout exception (specifically, {@link SQLTransientConnectionException}) to be thrown, because a
    * timeout occurred when trying to acquire a Connection from the pool.  If there was an underlying cause for the
    * timeout, e.g. a SQLException thrown by the driver while trying to create a new Connection, then use the
    * SQL State from that exception as our own and additionally set that exception as the "next" SQLException inside
    * of our exception.
    *
    * As a side-effect, log the timeout failure at DEBUG, and record the timeout failure in the metrics tracker.
    *
    * @param startTime the start time (timestamp) of the acquisition attempt
    * @return a SQLException to be thrown from {@link #getConnection()}
    */
   private SQLException createTimeoutException(long startTime)
   {
      logPoolState("Timeout failure ");
      metricsTracker.recordConnectionTimeout();

      String sqlState = null;
      final Throwable originalException = getLastConnectionFailure();
      if (originalException instanceof SQLException) {
         sqlState = ((SQLException) originalException).getSQLState();
      }
      final SQLException connectionException = new SQLTransientConnectionException(poolName + " - Connection is not available, request timed out after " + elapsedMillis(startTime) + "ms.", sqlState, originalException);
      if (originalException instanceof SQLException) {
         connectionException.setNextException((SQLException) originalException);
      }

      return connectionException;
   }


   // ***********************************************************************
   //                      Non-anonymous Inner-classes
   // ***********************************************************************

   /**
    * Creating and adding poolEntries (connections) to the pool.
    */
   private final class PoolEntryCreator implements Callable<Boolean>
   {
      private final String loggingPrefix;

      PoolEntryCreator(String loggingPrefix)
      {
         this.loggingPrefix = loggingPrefix;
      }

      @Override
      public Boolean call()
      {
         long sleepBackoff = 250L;
         while (poolState == POOL_NORMAL && shouldCreateAnotherConnection()) {
            final PoolEntry poolEntry = createPoolEntry();
            if (poolEntry != null) {
               connectionBag.add(poolEntry);
               logger.debug("{} - Added connection {}", poolName, poolEntry.connection);
               if (loggingPrefix != null) {
                  logPoolState(loggingPrefix);
               }
               return Boolean.TRUE;
            }

            // failed to get connection from db, sleep and retry
            if (loggingPrefix != null) logger.debug("{} - Connection add failed, sleeping with backoff: {}ms", poolName, sleepBackoff);
            quietlySleep(sleepBackoff);
            sleepBackoff = Math.min(SECONDS.toMillis(10), Math.min(connectionTimeout, (long) (sleepBackoff * 1.5)));
         }

         // Pool is suspended or shutdown or at max size
         return Boolean.FALSE;
      }

      /**
       * We only create connections if we need another idle connection or have threads still waiting
       * for a new connection.  Otherwise we bail out of the request to create.
       *
       * @return true if we should create a connection, false if the need has disappeared
       */
      private synchronized boolean shouldCreateAnotherConnection() {
         return getTotalConnections() < config.getMaximumPoolSize() &&
            (connectionBag.getWaitingThreadCount() > 0 || getIdleConnections() < config.getMinimumIdle());
      }
   }

   /**
    * The house keeping task to retire and maintain minimum idle connections.
    */
   private final class HouseKeeper implements Runnable
   {
      private volatile long previous = plusMillis(currentTime(), -housekeepingPeriodMs);

      @Override
      public void run()
      {
         try {
            // refresh values in case they changed via MBean
            connectionTimeout = config.getConnectionTimeout();
            validationTimeout = config.getValidationTimeout();
            leakTaskFactory.updateLeakDetectionThreshold(config.getLeakDetectionThreshold());
            catalog = (config.getCatalog() != null && !config.getCatalog().equals(catalog)) ? config.getCatalog() : catalog;

            final long idleTimeout = config.getIdleTimeout();
            final long now = currentTime();

            // Detect retrograde time, allowing +128ms as per NTP spec.
            if (plusMillis(now, 128) < plusMillis(previous, housekeepingPeriodMs)) {
               logger.warn("{} - Retrograde clock change detected (housekeeper delta={}), soft-evicting connections from pool.",
                           poolName, elapsedDisplayString(previous, now));
               previous = now;
               softEvictConnections();
               return;
            }
            else if (now > plusMillis(previous, (3 * housekeepingPeriodMs) / 2)) {
               // No point evicting for forward clock motion, this merely accelerates connection retirement anyway
               logger.warn("{} - Thread starvation or clock leap detected (housekeeper delta={}).", poolName, elapsedDisplayString(previous, now));
            }

            previous = now;

            String afterPrefix = "Pool ";
            if (idleTimeout > 0L && config.getMinimumIdle() < config.getMaximumPoolSize()) {
               logPoolState("Before cleanup ");
               afterPrefix = "After cleanup  ";

               final List<PoolEntry> notInUse = connectionBag.values(STATE_NOT_IN_USE);
               int toRemove = notInUse.size() - config.getMinimumIdle();
               for (PoolEntry entry : notInUse) {
                  if (toRemove > 0 && elapsedMillis(entry.lastAccessed, now) > idleTimeout && connectionBag.reserve(entry)) {
                     closeConnection(entry, "(connection has passed idleTimeout)");
                     toRemove--;
                  }
               }
            }

            logPoolState(afterPrefix);

            fillPool(); // Try to maintain minimum connections
         }
         catch (Exception e) {
            logger.error("Unexpected exception in housekeeping task", e);
         }
      }
   }

   public static class PoolInitializationException extends RuntimeException
   {
      private static final long serialVersionUID = 929872118275916520L;

      /**
       * Construct an exception, possibly wrapping the provided Throwable as the cause.
       * @param t the Throwable to wrap
       */
      public PoolInitializationException(Throwable t)
      {
         super("Failed to initialize pool: " + t.getMessage(), t);
      }
   }
}

	```
	

<img src="HikariDataSource.svg" width="90%" height="90%">



### 动态数据源

#### 编译时动态

#### 运行时动态



## mybatisplus 执行 SQL时数据源问题总结

- 数据源DataScoure是一个管理数据库连接的对象，它与数据库连接是一对多的关联
- mybatisplus的数据源对象取自SqlSessionFactory对象，在满足第一节Mybatisplus自动配置MybatisSqlSessionFactoryBean的条件下，mybatisplus获取的是优先级最高的（加了@Primary）DataScoure对象
- 指定事务管理器的数据源只会影响@Transactional注解绑定Datasource对象和Connection方法的逻辑，并不会影响mybatisplus实际获取的数据源（mybatisplus从SqlSessionFactory中取数据源）
	

