package eu.jerrysamek.tickspace.runner;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.Module;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.module.SimpleModule;
import eu.jerrysamek.tickspace.model.entity.EnergyState;
import eu.jerrysamek.tickspace.model.entity.Momentum;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.Vector;

import java.io.IOException;

public final class JsonTickFrameEntitiesModule {
  private JsonTickFrameEntitiesModule() {
  }

  public static Module module() {
    return new SimpleModule()
        .addSerializer(Momentum.class, new MomentumSerializer())
        .addSerializer(Vector.class, new VectorNdSerializer())
        .addSerializer(EnergyState.class, new EnergyVectorNdSerializer())
        .addSerializer(Position.class, new PositionSerializer());
  }

  private static class MomentumSerializer extends JsonSerializer<Momentum> {

    @Override
    public void serialize(Momentum value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
      gen.writeStartObject();
      gen.writeObjectField("cost", value.cost());
      gen.writeObjectField("vector", value.vector());
      gen.writeEndObject();
    }
  }

  private static class VectorNdSerializer extends JsonSerializer<Vector> {

    @Override
    public void serialize(Vector value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
      gen.writeObject(value.toArray());
    }
  }

  private static class EnergyVectorNdSerializer extends JsonSerializer<EnergyState> {

    @Override
    public void serialize(EnergyState value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
      gen.writeObject(value.value());
    }
  }

  private static class PositionSerializer extends JsonSerializer<Position> {
    @Override
    public void serialize(Position value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
      gen.writeObject(value.coordinates());
    }
  }
}
