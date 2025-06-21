import os
import asyncio
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger

setup_logger("lightrag", level="INFO")

WORKING_DIR = os.getenv("WORKING_DIR", "./rag_storage")
GRAPH_STORAGE = os.getenv("LIGHTRAG_GRAPH_STORAGE", "NetworkXStorage")

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

MAPPING_FILE = os.path.join(os.path.dirname(__file__), "mapping_synonyms.txt")


async def initialize_rag_instance():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage=GRAPH_STORAGE,
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag


async def main():
    rag = await initialize_rag_instance()
    try:
        if not os.path.exists(MAPPING_FILE):
            print(f"Mapping file not found: {MAPPING_FILE}")
            return
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entities = [e.strip() for e in line.split(";") if e.strip()]
                if not entities:
                    continue
                print(f"\n=== Entities in line: {entities} ===")
                entity_goc = entities[0]
                synonyms = entities[1:]
                # In thông tin từng entity trước khi merge
                for entity in entities:
                    info = await rag.get_entity_info(entity, include_vector_data=True)
                    entity_name = info.get("entity_name", "")
                    description = ""
                    graph_data = info.get("graph_data", {})
                    if isinstance(graph_data, dict):
                        description = graph_data.get("description", "")
                    print(f"Entity: {entity_name}")
                    print(f"Description: {description}\n")
                # Chỉ merge các synonym vào entity gốc
                if synonyms:
                    # Lọc synonym thực sự tồn tại
                    valid_synonyms = []
                    for s in synonyms:
                        try:
                            info = await rag.get_entity_info(s)
                            if info.get("graph_data"):
                                valid_synonyms.append(s)
                        except Exception:
                            continue
                    if not valid_synonyms:
                        print(
                            f"No valid synonyms to merge for '{entity_goc}'. Skipping."
                        )
                        continue
                    print(f"Merging {valid_synonyms} into '{entity_goc}' ...")
                    merge_strategy = {
                        "description": "concatenate",
                        "entity_type": "keep_first",
                        "source_id": "join_unique",
                    }
                    try:
                        result = await rag.amerge_entities(
                            source_entities=valid_synonyms,
                            target_entity=entity_goc,
                            merge_strategy=merge_strategy,
                        )
                        print(f"Merge result for '{entity_goc}':")
                        print(result)
                    except Exception as e:
                        print(f"Error merging: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
