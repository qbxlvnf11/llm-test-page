import json
from pydantic import Field
from typing import List
from pathlib import Path

def load_models_from_file() -> List[str]:
    root_dir = Path(__file__).parent.parent.parent
    model_file = "metadata/gemini_models.txt" #root_dir / "gemini_models.txt"
    
    with open(model_file, "r", encoding="utf-8") as f:
        models = [line.strip() for line in f if line.strip()]
    return models

def load_pricing_from_file(file_path: Path = Path("metadata/gemini_pricing.json")) -> dict:

    if not file_path.exists():
        print(f"경고: 요금 정보 파일 '{file_path}'를 찾을 수 없습니다. 기본값으로 빈 사전을 사용합니다.")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)