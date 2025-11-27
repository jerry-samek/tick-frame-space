package eu.jerrysamek.tickspace.model.entity;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;

public class EnergyState {
  private BigInteger energy;

  public static EnergyState zero() {
    return new EnergyState(BigInteger.ZERO);
  }

  public EnergyState(BigInteger energy) {
    this.energy = energy;
  }

  public BigInteger increase() {
    energy = energy.add(BigInteger.ONE);

    return energy;
  }

  public BigInteger getEnergy() {
    return energy;
  }

  public EnergyState merge(EnergyState other) {
    return new EnergyState(energy.add(other.energy));
  }

  public BigDecimal normalized(BigInteger tickCount) {
    BigDecimal normalized = new BigDecimal(energy);
    BigDecimal count = new BigDecimal(tickCount);

    return normalized.divide(count, 10, RoundingMode.HALF_UP);
  }

  @Override
  public String toString() {
    return "EnergyState{" +
        "value=" + energy +
        '}';
  }
}
