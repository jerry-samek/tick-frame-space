package eu.jerrysamek.tickspace.model.ticktime;

import java.math.BigInteger;
import java.util.stream.Stream;

/**
 * Interface for consumers that respond to time tick events.
 */
public interface TickTimeConsumer<E> {

    /**
     * Called when a tick occurs.
     */
    Stream<E> onTick(BigInteger tickCount);
}
