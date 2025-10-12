from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

from typing import List

import google.generativeai as genai
from google.generativeai.types import generation_types

from model import gemini_schemas
from config.base import settings
from utils.cost import calculate_cost
from utils.stream import stream_generator

# Create an APIRouter instance
router = APIRouter(
    tags=["gemini"]
)

# Configure the location of the template files
templates = Jinja2Templates(directory="templates")

@router.get("/gemini_test_page", response_class=HTMLResponse, summary="API Test Page")
async def get_gemini_test_page(request: Request):

    # Data to be passed to the template
    context = {
        "request": request,
        "title": "Gemini Test Page",
        "content": ""
    }
    return templates.TemplateResponse("gemini_test_page.html", context)


@router.get("/gemini_available_models", response_model=List[str], summary="설정 파일에서 Gemini 모델 목록 조회")
async def get_available_models():

    return settings.GEMINI_MODELS


# @router.post("/gemini_test_query", response_model=gemini_schemas.GeminiTestQueryResponse, summary="Gemini Test Query")
# async def generate_gemini_response(request: gemini_schemas.GeminiTestQueryRequest):
    
#     try:
#         model = genai.GenerativeModel(request.model_name)

#         generation_config = genai.types.GenerationConfig(
#             max_output_tokens=request.max_output_tokens,
#             top_k=request.top_k,
#             top_p=request.top_p,
#             temperature=request.temperature,
#         )

#         response = model.generate_content(
#             request.query,
#             generation_config=generation_config
#         )

#         if not response.candidates or not response.candidates[0].content.parts:
#             finish_reason = response.candidates[0].finish_reason if response.candidates else ''
#             raise HTTPException(status_code=400, detail=f"AI로부터 유효한 텍스트를 받지 못했습니다. 종료 원인: {finish_reason.name}")

#         return {"response_text": response.text}

#     except generation_types.StopCandidateException as e:
#         print(f"Content generation stopped unexpectedly: {e}")
#         raise HTTPException(status_code=400, detail=f"콘텐츠 생성 중단됨: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {e}")

@router.post("/gemini_test_query", summary="Gemini Test Query")
async def generate_gemini_response(request: gemini_schemas.GeminiTestQueryRequest):
    
    try:
        model = genai.GenerativeModel(request.model_name)

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=request.max_output_tokens,
            top_k=request.top_k,
            top_p=request.top_p,
            temperature=request.temperature,
        )

        ## 스트림 요청인지 확인하여 분기
        if request.stream:
            ## 스트리밍 호출
            response_stream = model.generate_content(
                request.query,
                generation_config=generation_config,
                stream=True
            )

            # ## API로부터 받은 각 텍스트 조각을 즉시 yield로 반환
            # for chunk in response_stream:
            #     ## 빈 청크 예외 처리
            #     try:
            #         if chunk.text:
            #             yield chunk.text
            #             ## await asyncio.sleep(0.01) # 로컬에서 테스트 시 스트리밍을 명확히 보려면 주석 해제
            #     except ValueError:
            #         pass ## 유효하지 않은 청크는 건너뜁니다.

            ## StreamingResponse로 제너레이터 함수를 감싸서 반환
            return StreamingResponse(
                stream_generator(response_stream, request.model_name), 
                media_type="text/event-stream"
            )

        else: ## 기존 비스트리밍 로직
            response = model.generate_content(
                request.query,
                generation_config=generation_config,
                stream=False
            )
            
            if not response.text:
                 raise HTTPException(status_code=400, detail="AI로부터 유효한 텍스트를 받지 못했습니다.")

            ## 비스트리밍 응답에도 토큰 및 비용 정보 추가
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            cost = calculate_cost(request.model_name, input_tokens, output_tokens)

            metadata = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }

            return {
                "response_text": response.text,
                "usage_metadata": metadata
            }

    except generation_types.StopCandidateException as e:
        print(f"Content generation stopped unexpectedly: {e}")
        raise HTTPException(status_code=400, detail=f"콘텐츠 생성 중단됨: {e}")
    except Exception as e:
        ## API 키 오류, 모델 이름 오류 등 초기 설정 오류는 여기서 처리됩니다.
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}")
