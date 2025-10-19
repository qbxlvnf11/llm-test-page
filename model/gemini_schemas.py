from pydantic import BaseModel, Field

class GeminiTestQueryRequest(BaseModel):
    query: str = Field(..., description="Gemini 모델에게 보낼 질문(프롬프트)")
    model_name: str = Field("gemini-2.5-flash", description="사용할 모델 이름")
    temperature: float = Field(1.0, ge=0.0, le=2.0, description="창의성 (0.0: 결정적, 2.0: 매우 창의적)")
    max_output_tokens: int = Field(8192, description="최대 출력 토큰 수")
    top_k: int = Field(40, description="Top-K 샘플링")
    top_p: float = Field(1.0, description="Top-P 샘플링")
    stream: bool = False

class GeminiTestQueryResponse(BaseModel):
    response_text: str
    
class UsageMetadata(BaseModel):
    input_tokens: int
    output_tokens: int
    cost: float