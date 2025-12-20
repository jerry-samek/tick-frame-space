package eu.jerrysamek.tickspace.model;

public class ModelBreakingException extends RuntimeException {
  public ModelBreakingException(String message) {
    super(message);
  }
  public ModelBreakingException(String message, Throwable cause) {
    super(message, cause);
  }
}
