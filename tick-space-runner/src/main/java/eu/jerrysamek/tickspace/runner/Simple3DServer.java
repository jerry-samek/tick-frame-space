package eu.jerrysamek.tickspace.runner;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.undertow.Undertow;
import io.undertow.websockets.WebSocketProtocolHandshakeHandler;
import io.undertow.websockets.core.WebSocketChannel;
import io.undertow.websockets.core.WebSockets;
import io.undertow.websockets.spi.WebSocketHttpExchange;

import java.util.List;
import java.util.concurrent.Executors;

public class Simple3DServer {
  static ObjectMapper mapper = new ObjectMapper();

  static void main(String[] args) {
    var executor = Executors.newVirtualThreadPerTaskExecutor();

    var server = Undertow.builder()
        .addHttpListener(8080, "0.0.0.0")
        .setHandler(exchange -> {
          WebSocketProtocolHandshakeHandler handler =
              new WebSocketProtocolHandshakeHandler(
                  (WebSocketHttpExchange ex, WebSocketChannel channel) -> {
                    executor.submit(() -> handleClient(channel));
                  });
          handler.handleRequest(exchange);
        })
        .build();

    server.start();

    System.out.println("WebSocket server started on ws://localhost:8080/viewcone");
  }

  static void handleClient(WebSocketChannel channel) {
    var tick = 0;

    while (channel.isOpen()) {
      try {
        // Build a dummy 3D brick payload
        Brick brick = new Brick(
            new int[]{0, 0, 0},
            new byte[]{16, 16, 16},
            generateEnergy(),
            new byte[0],
            new short[0]
        );
        ViewconePacket packet = new ViewconePacket(
            tick,
            new float[]{0, 0, 100},
            new float[]{0, 0, -1},
            (byte) 16,
            List.of(brick)
        );

        String json = mapper.writeValueAsString(packet);
        WebSockets.sendText(json, channel, null);

        tick++;
        Thread.sleep(100); // pace
      } catch (Exception e) {
        e.printStackTrace();
        break;
      }
    }
  }

  static byte[] generateEnergy() {
    byte[] arr = new byte[16 * 16 * 16];
    for (int i = 0; i < arr.length; i++) {
      arr[i] = (byte) (Math.random() * 255);
    }
    return arr;
  }

  // --- Data records ---
  public record Brick(int[] origin, byte[] dims, byte[] energyU8,
                      byte[] parityBits, short[] momentumQ) {
  }

  public record ViewconePacket(long tick, float[] camPos, float[] camDir,
                               byte brickSize, List<Brick> bricks) {
  }
}
