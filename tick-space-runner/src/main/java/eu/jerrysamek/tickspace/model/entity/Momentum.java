package eu.jerrysamek.tickspace.model.entity;

import java.math.BigInteger;
import java.util.Arrays;

public record Momentum(BigInteger cost, BigInteger[] vector) {

  public BigInteger totalCost() {
    return Arrays.stream(vector)
        .map(bigInteger -> bigInteger.multiply(cost))
        .reduce(BigInteger.ZERO, BigInteger::add);
  }
}
