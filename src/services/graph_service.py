import os
from neo4j import GraphDatabase
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from dotenv import load_dotenv


load_dotenv()


@dataclass
class ImageNode:
    sum: float
    period_start: str
    period_end: str
    image_path: str
    embedding: list | None = None
    created: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class GraphDBService:
    def __init__(self):
        uri = os.getenv("NEO4j_URI")
        user = os.getenv("NEO4j_USER")
        password = os.getenv("NEO4j_PASSWORD")
        
        if not all([uri, user, password]):
            raise ValueError(
                "Не указаны параметры подключения к Neo4j. "
                "Установите NEO4j_URI, NEO4j_USER, NEO4j_PASSWORD в файле .env"
            )
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            raise ConnectionError(f"Не удалось подключиться к Neo4j: {e}") from e
    
    def close(self):
        """Закрывает соединение с Neo4j"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()
    

    def push_image_node(self, node: ImageNode):
        sum_key = int(
            round(node.sum)
        )  # <- если у тебя всегда int, можно просто int(node.sum)

        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Sum {value: $sum_key})
                MERGE (i:Image {id: $id})
                SET i.sum = $sum,
                    i.period_start = $period_start,
                    i.period_end = $period_end,
                    i.image_path = $path,
                    i.created = datetime($created)
                MERGE (i)-[:HAS_SUM]->(s)
                """,
                id=node.id,
                sum=node.sum,
                sum_key=sum_key,
                period_start=node.period_start,
                period_end=node.period_end,
                path=node.image_path,
                created=node.created.isoformat(),
            )

    def find_similar_by_sum(self, target_id: str, limit: int = 20):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Image {id: $id})-[:HAS_SUM]->(s:Sum)<-[:HAS_SUM]-(other:Image)
                WHERE other.id <> $id
                RETURN other.id AS id, other.sum AS sum, other.image_path AS image_path,
                    other.period_start AS period_start, other.period_end AS period_end,
                    other.created AS created
                ORDER BY other.created DESC
                LIMIT $limit
                """,
                id=target_id,
                limit=limit,
            )
            return [r.data() for r in result]

    # def find_by_sum_range(self, target_sum: float, tolerance=10):
    #     result = session.run(
    #         """
    #         MATCH (img:Image)
    #         WHERE img.sum >= $min_sum AND img.sum <= $max_sum
    #         RETURN img.id AS id, img.sum AS sum, img.image_path AS image_path,
    #             abs(img.sum - $target_sum) AS difference
    #         ORDER BY difference
    #         """,
    #         min_sum=target_sum - tolerance,
    #         max_sum=target_sum + tolerance,
    #         target_sum=target_sum,
    #     )

    #     images = []
    #     for record in result:
    #         images.append(
    #             {
    #                 "id": record["id"],
    #                 "sum": record["sum"],
    #                 "image_path": record["image_path"],
    #                 "difference": record["difference"],
    #             }
    #         )
    #     return images

    # def close(self):
    #     self.driver.close()
