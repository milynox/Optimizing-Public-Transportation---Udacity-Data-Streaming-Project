"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic

logger = logging.getLogger(__name__)
SCHEMA_REGISTRY_URL = "http://localhost:8081/"
BROKER_URL = "PLAINTEXT://localhost:9092"
# ,PLAINTEXT://localhost:9093,PLAINTEXT://localhost:9094

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        self.broker_properties = {
            "bootstrap.servers": BROKER_URL,
            "new": "old"
        }
        self.client = AdminClient(self.broker_properties)

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        avro_config = {
            "schema.registry.url": SCHEMA_REGISTRY_URL,
            "bootstrap.servers": BROKER_URL,
        }
        self.producer = avro.AvroProducer(
            config=avro_config,
            default_key_schema=self.key_schema,
            default_value_schema=self.value_schema,
        )
        logger.info("topic creation kafka successfully")

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        self.client.create_topics([
            NewTopic(
                topic=self.topic_name,
                num_partitions=self.num_partitions,
                replication_factor=self.num_replicas
            ),
        ])

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.producer.flush()
        logger.info("producer close complete")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
