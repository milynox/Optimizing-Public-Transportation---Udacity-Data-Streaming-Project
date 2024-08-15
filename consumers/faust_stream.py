"""Defines trends calculations for stations"""
import logging
from dataclasses import dataclass

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
@dataclass
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
@dataclass
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str



app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")

topic = app.topic("postgres-stations", value_type=Station)

out_topic = app.topic("org.chicago.cta.stations.table.v1", partitions=1)
counts = app.Table('click_counts', default=int)
transformed_station_table = app.Table(
   "tranformed_stations",
   default=int,
   partitions=1,
   changelog_topic=out_topic,
)


def line_color(station):
    if (station.red):
        return "red"
    elif (station.blue):
        return "blue"
    elif (station.green):
        return "green"
    else:
        return ""


@app.agent(topic)
async def truncate_stream(stations):
    
    async for station in stations:
        line = line_color(station)
        
        transformed_stations = TransformedStation(
            station_id=station.station_id,
            station_name=station.station_name,
            order=station.order,
            line=line,
        )
        transformed_station_table[station.station_id] = transformed_stations
        
        logger.info(f"{station.station_id}: {transformed_station_table[station.station_id]}")

if __name__ == "__main__":
    app.main()
