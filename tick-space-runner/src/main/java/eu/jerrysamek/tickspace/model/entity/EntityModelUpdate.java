package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.util.stream.Stream;

public interface EntityModelUpdate {

  Stream<EntityModel> update(SubstrateModel model);
}
