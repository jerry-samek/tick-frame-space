package eu.jerrysamek.tickspace.model.ticktime;

import eu.jerrysamek.tickspace.model.ModelBreakingException;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.math.BigInteger;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;
import java.util.stream.Gatherers;

/**
 * Simple tick-based time model that fires updates to TimeTickConsumers.
 * Each tick increments a dimensional length in the consumer by 1 point.
 */
public class TickTimeModel implements AutoCloseable {

  private final ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();

  private final TickTimeConsumer<TickTimeUpdate> consumer;
  private BigInteger tickCount = BigInteger.ZERO;
  private final BiConsumer<TickTimeModel, BigInteger> afterTick;

  /**
   * Creates a TickTimeModel with the associated TickTimeConsumer.
   *
   * @param consumer the consumer to update on each tick
   */
  public TickTimeModel(final TickTimeConsumer<TickTimeUpdate> consumer, final BiConsumer<TickTimeModel, BigInteger> afterTick) {
    if (consumer == null) {
      throw new IllegalArgumentException("TickTimeConsumer cannot be null");
    }
    this.consumer = consumer;
    this.afterTick = afterTick;
  }

  public void stop() {
    executor.shutdownNow();
  }

  /**
   * Starts tick updates
   * This fires an update to the consumer, incrementing all dimensions by 1.
   */
  public void start() {
    var threadNumber = Runtime.getRuntime().availableProcessors() * 2;
    var tickTaskExecutor = Executors.newWorkStealingPool(threadNumber);

    executor.scheduleWithFixedDelay(() -> {
      tickCount = tickCount.add(BigInteger.ONE);
      try {
        var start = System.nanoTime();

        var timeUpdateStream = consumer.onTick(tickCount);

        var tickUpdate = System.nanoTime();

        // Batch actions before submitting to reduce executor overhead
        // Instead of 3.2M individual tasks, submit ~320 batch tasks
        var BATCH_SIZE = 1_000;

        timeUpdateStream
            .filter(action -> action.type() == TickTimeConsumer.TickActionType.UPDATE)
            .parallel()
            .map(TickTimeConsumer.TickAction::action)
            .gather(Gatherers.windowFixed(BATCH_SIZE))
            .map(batch ->  // Submit one task per batch that executes all actions sequentially
                tickTaskExecutor.submit(() -> batch.forEach(Runnable::run)))
            .gather(Gatherers.windowFixed(threadNumber))
            .forEach(futures -> {
              // Wait for all batch tasks to complete
              for (var future : futures) {
                try {
                  future.get();
                } catch (Exception e) {
                  throw new ModelBreakingException("Issue during tick processing!", e);
                }
              }
            });

        // CRITICAL: Flip buffers AFTER all futures complete
        // This ensures double-buffering works correctly for EntitiesRegistry
        if (consumer instanceof SubstrateModel substrate) {
          substrate.flip();
        }

        var tickExecution = System.nanoTime();

        final double updateMs = (tickUpdate - start) / 1_000_000.0;
        final double executionMs = (tickExecution - tickUpdate) / 1_000_000.0;
        final double totalMs = (tickExecution - start) / 1_000_000.0;

        afterTick.accept(this, tickCount);

        System.out.printf(" - statistics: update=%.2f ms, execution=%.2f ms, total=%.2f ms%n", updateMs, executionMs, totalMs);
      } catch (Exception e) {
        e.printStackTrace();
      }
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
