package eu.jerrysamek.tickspace.runner;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeModel;

public class LocalApp {

  static void main(String[] args) {

    var entitiesRegistry = new EntitiesRegistry();

    var substrate = new SubstrateModel(3, entitiesRegistry);

    new TickTimeModel(substrate, tick -> {
      System.out.printf("tick %s entity count: %d%n", tick, entitiesRegistry.count());

    }).start();

  }
}
