package eu.jerrysamek.tickspace.server;

// --- Data records ---
public record Brick(int[] origin, byte[] dims, byte[] energyU8,
                    byte[] parityBits, short[] momentumQ) {
}
