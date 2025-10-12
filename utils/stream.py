import json 
import asyncio

from utils.cost import calculate_cost

async def stream_generator(response, model_name: str):

    try:
        for chunk in response:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0)
    except Exception as e:
        pass
        # print(f"스트리밍 중 오류 발생: {e}")
        # yield f"\n\n오류: 스트리밍 중 문제가 발생했습니다: {e}"

    try:
        # Gemini API는 스트림이 끝나면 usage_metadata를 제공합니다.
        usage_metadata = response.usage_metadata
        input_tokens = usage_metadata.prompt_token_count
        output_tokens = usage_metadata.candidates_token_count
        cost = calculate_cost(model_name, input_tokens, output_tokens)

        metadata = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        metadata_json_string = json.dumps(metadata)
        
        # 프론트엔드와 약속한 구분자와 함께 메타데이터 전송
        yield f"\n<--METADATA-->\n{metadata_json_string}"
        await asyncio.sleep(0)

    except Exception as e:
        print(f"메타데이터 처리 중 오류: {e}")
