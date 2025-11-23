package eu.jerrysamek.tickspace.model.ticktime;

import java.math.BigInteger;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

/**
 * Simple tick-based time model that fires updates to TimeTickConsumers.
 * Each tick increments a dimensional length in the consumer by 1 point.
 */
public class TickTimeModel implements AutoCloseable {

  private final ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();

  private final TickTimeConsumer<TickTimeUpdate> consumer;
  private BigInteger tickCount = BigInteger.ZERO;
  private final Consumer<BigInteger> afterTick;

  /**
   * Creates a TickTimeModel with the associated TickTimeConsumer.
   *
   * @param consumer the consumer to update on each tick
   */
  public TickTimeModel(final TickTimeConsumer<TickTimeUpdate> consumer, final Consumer<BigInteger> afterTick) {
    if (consumer == null) {
      throw new IllegalArgumentException("TickTimeConsumer cannot be null");
    }
    this.consumer = consumer;
    this.afterTick = afterTick;
  }

  /**
   * Starts tick updates
   * This fires an update to the consumer, incrementing all dimensions by 1.
   */
  public void start() {
    var tickTaskExecutor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors() * 2);

    executor.scheduleWithFixedDelay(() -> {
      tickCount = tickCount.add(BigInteger.ONE);

      var start = System.nanoTime();

      var timeUpdateStream = consumer.onTick(tickCount);

      var tickUpdate = System.nanoTime();
      //  timeUpdateStream.forEach(Runnable::run);
      timeUpdateStream
          .map(tickTaskExecutor::submit)
          .toList()
          .forEach(future -> {
            try {
              future.get();
            } catch (Exception e) {
              throw new RuntimeException(e);
            }
          });

      var tickExecution = System.nanoTime();

      double updateMs = (tickUpdate - start) / 1_000_000.0;
      double executionMs = (tickExecution - tickUpdate) / 1_000_000.0;
      double totalMs = (tickExecution - start) / 1_000_000.0;

      System.out.printf("tick %s statistics: update=%.2f ms, execution=%.2f ms, total=%.2f ms%n",
          tickCount, updateMs, executionMs, totalMs);

      afterTick.accept(tickCount);
    }, 0, 10, TimeUnit.MILLISECONDS);
  }

  /**
   * Gets the total number of ticks that have occurred.
   *
   * @return the tick count
   */
  public BigInteger getTickCount() {
    return tickCount;
  }

  @Override
  public String toString() {
    return "TickTimeModel{" +
        "tickCount=" + tickCount +
        ", consumer=" + consumer +
        '}';
  }

  @Override
  public void close() {
    executor.shutdown();
  }
}
