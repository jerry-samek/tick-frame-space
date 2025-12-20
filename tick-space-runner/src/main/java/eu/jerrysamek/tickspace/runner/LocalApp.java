package eu.jerrysamek.tickspace.runner;

import eu.jerrysamek.tickspace.model.entity.CollidingEntityModel;
import eu.jerrysamek.tickspace.model.entity.EntitiesRegistryLegacy;
import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.entity.Momentum;
import eu.jerrysamek.tickspace.model.entity.SingleEntityModel;
import eu.jerrysamek.tickspace.model.exportimport.BinarySnapshotWriter;
import eu.jerrysamek.tickspace.model.exportimport.SimulationSnapshot;
import eu.jerrysamek.tickspace.model.exportimport.SnapshotManager;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeModel;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Collection;
import java.util.LinkedList;
import java.util.Queue;
import java.util.UUID;

public class LocalApp {

  static void main(String[] args) {
    final Queue<SimulationSnapshot> snapshots = new LinkedList<>();

    var entitiesRegistry = new EntitiesRegistryLegacy();
    var substrate = new SubstrateModel(3, entitiesRegistry);
    var seedEntity = createSeed(substrate);

    entitiesRegistry.addEntity(seedEntity.getPosition(), seedEntity);

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
                .createSnapshot(snapshot.tickCount(), entitiesRegistry, substrate.getDimensionalSize().getDimensionCount());

            var totalEnergyBalance = snapshot.entities().stream().map(entityModel -> entityModel
                    .getEnergy(snapshot.tickCount()).divide(snapshot.tickCount())
                    .subtract(entityModel.getMomentum().totalCost()))
                .reduce(FlexInteger.ZERO, FlexInteger::add);

            System.out.println(" - total energy balance: " + totalEnergyBalance);

            System.out.println(" - total energy loss by annihilation: " + CollidingEntityModel.totalEnergyLoss);

            try {
              new BinarySnapshotWriter().write(sim, Path.of("W:\\data\\snapshots\\time-frame." + snapshot.tickCount() + ".snap"));
            } catch (IOException e) {
              throw new RuntimeException(e);
            }
            System.out.println(" - new snapshot generated for tick " + snapshot.tickCount());
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

      if (tick.remainder(FlexInteger.of(100)).equals(FlexInteger.ZERO)) {
        System.out.println(" - preparing new snapshot ...");

        synchronized (snapshots) {
          snapshots.add(new SimulationSnapshot(tick, substrate.getDimensionalSize().getDimensionCount(), snapshot));
          snapshots.notifyAll();
        }
      }
    }).start();

  }

  private static SingleEntityModel createSeed(SubstrateModel substrate) {
    var dimensionCount = substrate.getDimensionalSize().getDimensionCount();
    var position = new Position(Vector.zero(dimensionCount));
    var momentum = new Momentum(FlexInteger.ONE, Vector.zero(dimensionCount));

    return new SingleEntityModel(substrate, UUID.randomUUID(), FlexInteger.ONE, position, FlexInteger.ONE, momentum);
  }
}
