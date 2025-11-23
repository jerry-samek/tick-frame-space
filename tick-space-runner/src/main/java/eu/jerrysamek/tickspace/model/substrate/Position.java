package eu.jerrysamek.tickspace.model.substrate;

import java.math.BigInteger;
import java.util.Arrays;

public record Position(BigInteger[] coordinates) {
  @Override
  public String toString() {
    return "Position{" +
        "coordinates=" + Arrays.toString(coordinates) +
        '}';
  }

  @Override
  public boolean equals(Object o) {
    if (!(o instanceof Position position)) return false;

    return Arrays.equals(coordinates, position.coordinates);
  }

  @Override
  public int hashCode() {
    return Arrays.hashCode(coordinates);
  }

  public Position offset(BigInteger[] offsets) {
    if (offsets.length != coordinates.length) {
      throw new IllegalArgumentException("Offsets length must be equal to coordinates length");
    }

    var newCoordinates = new BigInteger[coordinates.length];

    for (int i = 0; i < offsets.length; i++) {
      newCoordinates[i] = coordinates[i].add(offsets[i]);
    }
    return new Position(newCoordinates);
  }
}
