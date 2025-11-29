package eu.jerrysamek.tickspace.model.ticktime;

import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.stream.Stream;

/**
 * Interface for consumers that respond to time tick events.
 */
public interface TickTimeConsumer<E> {

  enum TickActionType {
    WAIT, UPDATE
  }

  record TickAction<E>(TickActionType type, E action) {

  }

  /**
   * Called when a tick occurs.
   */
  Stream<TickAction<E>> onTick(FlexInteger tickCount);
}
