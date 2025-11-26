package eu.jerrysamek.tickspace.runner;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeModel;

import java.io.IOException;
import java.io.OutputStream;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.LinkedList;
import java.util.Queue;

public class LocalApp {

  private record Snapshot(BigInteger tick, Collection<EntityModel> entities) {
  }

  static void main(String[] args) {
    var mapper = new ObjectMapper();
    mapper.disable(SerializationFeature.CLOSE_CLOSEABLE);
    //mapper.registerModule(JsonTickFrameEntitiesModule.module());

    final Queue<Snapshot> snapshots = new LinkedList<>();

    var entitiesRegistry = new EntitiesRegistry();

    var substrate = new SubstrateModel(3, entitiesRegistry);

    Thread.ofPlatform().daemon(false).start(() -> {
      while (true) {
        synchronized (snapshots) {
          if (snapshots.isEmpty()) {
            try {
              snapshots.wait();
            } catch (InterruptedException e) {
              throw new RuntimeException(e);
            }
          }

          var snapshot = snapshots.poll();
          if (snapshot != null) {
            try (OutputStream fileOutputStream = Files.newOutputStream(Path.of("W:\\data\\snapshots\\time-frame." + snapshot.tick + ".json"))) {
              mapper.writeValue(fileOutputStream, snapshot.entities);
            } catch (IOException e) {
              throw new RuntimeException(e);
            }
          }
        }
      }
    });

    new TickTimeModel(substrate, tick -> {
      // after tick processing
      System.out.println("====== tick " + tick + " ======");
      System.out.println(" - dimensional bounds: " + substrate.getDimensionalSize());
      var count = entitiesRegistry.count();
      System.out.println(" - entities: " + count);
      var snapshot = entitiesRegistry.snapshot();

      var totalEnergyBalance = snapshot.stream().map(entityModel -> entityModel
              .getEnergy().divide(tick)
              .subtract(entityModel.getMomentum().totalCost()))
          .reduce(BigInteger.ZERO, BigInteger::add);

      System.out.println(" - total energy balance: " + totalEnergyBalance);

      if (BigInteger.ZERO.equals(tick.remainder(BigInteger.valueOf(1000)))) {
        System.out.println(" - new snapshot generated");

        synchronized (snapshots) {
          snapshots.add(new Snapshot(tick, snapshot));
          snapshots.notifyAll();
        }
      }
    }).start();

  }
}
