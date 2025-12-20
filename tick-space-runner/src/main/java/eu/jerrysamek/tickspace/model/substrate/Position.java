package eu.jerrysamek.tickspace.model.substrate;

public value record Position(Vector coordinates) {

  public Position offset(Vector offset) {
    return new Position(coordinates.add(offset));
  }

  @Override
  public String toString() {
    return "Position{" + coordinates + "}";
  }
}
