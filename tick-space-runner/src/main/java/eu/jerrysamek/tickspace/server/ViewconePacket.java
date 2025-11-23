package eu.jerrysamek.tickspace.server;

import java.util.List;

public record ViewconePacket(long tick, float[] camPos, float[] camDir,
     byte brickSize, List<Brick> bricks) {
}
