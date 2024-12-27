from datetime import datetime
from dotenv import load_dotenv
import yaml

loaded = load_dotenv()
from agents.services.qdrant_manager import MemoryManager


if __name__ == "__main__":
    qdrant_manager = MemoryManager()
    memories = qdrant_manager.dump_memories()

    data = {
        "dump_date": datetime.now().isoformat(),
        "memories": [],
    }
    for m in memories:
        data["memories"].append(
            {
                "id": m.id,
                "payload": m.payload,
            }
        )

    with open("memories.yaml", "w") as f:
        yaml.dump(data, f)
