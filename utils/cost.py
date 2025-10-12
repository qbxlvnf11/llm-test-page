from config.base import settings

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    
    pricing = settings.MODEL_PRICING.get(model_name)
    # pricing = MODEL_PRICING.get(model_name.replace('models/', ''), MODEL_PRICING.get("gemini-2.5-flash")) 
    if not pricing:
        return 0.0
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost