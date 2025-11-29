package eu.jerrysamek.tickspace.runner;

import eu.jerrysamek.tickspace.model.entity.CollidingEntityModel;
import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.exportimport.BinarySnapshotWriter;
import eu.jerrysamek.tickspace.model.exportimport.SnapshotManager;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeModel;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.nio.file.Path;
import java.util.Collection;
import java.util.LinkedList;
import java.util.Queue;

public class LocalApp {

  private record Snapshot(BigInteger tick, Collection<EntityModel> entities) {
  }

  static void main(String[] args) {
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
              Thread.currentThread().interrupt();
              throw new RuntimeException(e);
            }
          }

          var snapshot = snapshots.poll();
          if (snapshot != null) {
            var sim = new SnapshotManager()
                .createSnapshot(snapshot.tick, entitiesRegistry, substrate.getDimensionalSize().getDimensionCount());

            var totalEnergyBalance = snapshot.entities.stream().map(entityModel -> entityModel
                    .getEnergy().normalized(snapshot.tick)
                    .subtract(new BigDecimal(entityModel.getMomentum().totalCost())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

            System.out.println(" - total energy balance: " + totalEnergyBalance);

            System.out.println(" - total energy loss by annihilation: " + CollidingEntityModel.totalEnergyLoss);

            try {
              new BinarySnapshotWriter().write(sim, Path.of("W:\\data\\snapshots\\time-frame." + snapshot.tick + ".snap"));
            } catch (IOException e) {
              throw new RuntimeException(e);
            }
            System.out.println(" - new snapshot generated for tick " + snapshot.tick);
          }
        }
      }
    });

    new TickTimeModel(substrate, (_, tick) -> {
      // after tick processing
      System.out.println("====== tick " + tick + " ======");
      System.out.println(" - dimensional bounds: " + substrate.getDimensionalSize());
      var count = entitiesRegistry.count();
      System.out.println(" - entities: " + count);
      var snapshot = entitiesRegistry.snapshot();

      if (tick.remainder(BigInteger.valueOf(100)).equals(BigInteger.ZERO)) {
        System.out.println(" - preparing new snapshot ...");

        synchronized (snapshots) {
          snapshots.add(new Snapshot(tick, snapshot));
          snapshots.notifyAll();
        }
      }
    }).start();

  }
}
