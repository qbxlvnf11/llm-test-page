marked.setOptions({
  breaks: true,
  gfm: true,
  smartLists: true,
  mangle: false,
  headerIds: false
});

function renderMarkdown(rawText) {
  return marked.parse(rawText);
  // const parts = rawText.split(/(```[\s\S]*?```)/g);
  // const escaped = parts.map((part) => {
  //   if (part.startsWith("```") && part.endsWith("```")) {
  //     return part; // 코드블록 그대로
  //   } else {
  //     return part
  //       .replace(/\\/g, '\\\\')
  //       .replace(/(?<=^|\n)- /g, '\\- ')
  //       .replace(/(?<=^|\n)\* /g, '\\* ')
  //       .replace(/_/g, '\\_')
  //       .replace(/`/g, '\\`')
  //       .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
  //       .replace(/  /g, '&nbsp;&nbsp;');
  //   }
  // });
  // return marked.parse(escaped.join(''));
}

const modelSelect = document.getElementById('model-select');
const promptInput = document.getElementById('prompt-input');
const submitButton = document.getElementById('submit-button');
const buttonText = document.getElementById('button-text');
const buttonSpinner = document.getElementById('button-spinner');
const responseArea = document.getElementById('response-area');
const streamCheckbox = document.getElementById('stream-checkbox');
const temperatureSlider = document.getElementById('temperature');
const temperatureValue = document.getElementById('temperature-value');
const topPSlider = document.getElementById('top-p');
const topPValue = document.getElementById('top-p-value');
const topKInput = document.getElementById('top-k');
const maxTokensInput = document.getElementById('max-tokens');
const usageInfo = document.getElementById('usage-info');
const inputTokens = document.getElementById('input-tokens');
const outputTokens = document.getElementById('output-tokens');
const estimatedCost = document.getElementById('estimated-cost');
const inferenceTime = document.getElementById('inference-time');

window.onload = async () => {
  try {
    const response = await fetch('/gemini_available_models');
    const models = await response.json();
    models.forEach(model => {
      const opt = document.createElement('option');
      opt.value = model;
      opt.textContent = model.replace('models/', '');
      modelSelect.appendChild(opt);
    });
    modelSelect.value = 'models/gemini-2.5-flash';
  } catch (e) {
    modelSelect.innerHTML = '<option>모델 로딩 실패</option>';
  }
};

temperatureSlider.addEventListener('input', e => temperatureValue.textContent = e.target.value);
topPSlider.addEventListener('input', e => topPValue.textContent = e.target.value);

submitButton.addEventListener('click', async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) return alert('질문을 입력해주세요.');
  setLoading(true);
  resetUsageInfo();

  const requestBody = {
    query: prompt,
    model_name: modelSelect.value,
    temperature: parseFloat(temperatureSlider.value),
    top_p: parseFloat(topPSlider.value),
    top_k: parseInt(topKInput.value),
    max_output_tokens: parseInt(maxTokensInput.value),
    stream: streamCheckbox.checked
  };

  try {
    const response = await fetch('/gemini_test_query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (streamCheckbox.checked) await handleStreamResponse(response);
    else await handleNormalResponse(response);
  } catch (e) {
    responseArea.innerHTML = `<p class='text-red-600'>오류 발생: ${e.message}</p>`;
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  buttonText.style.display = isLoading ? 'none' : 'inline';
  buttonSpinner.style.display = isLoading ? 'inline-block' : 'none';
  if (isLoading) responseArea.innerHTML = '<p class="text-gray-500">AI가 생각 중입니다...</p>';
}

function resetUsageInfo() {
  usageInfo.classList.add('hidden');
  inputTokens.textContent = '0';
  outputTokens.textContent = '0';
  estimatedCost.textContent = '$0.000000';
  inferenceTime.textContent = '0ms';
}

function updateUsageInfo(metadata) {
  if (!metadata) return;
  inputTokens.textContent = metadata.input_tokens || 'N/A';
  outputTokens.textContent = metadata.output_tokens || 'N/A';
  estimatedCost.textContent = metadata.cost ? `$${metadata.cost.toFixed(6)}` : 'N/A';
  inferenceTime.textContent = metadata.inference_time || 'N/A';
  usageInfo.classList.remove('hidden');
}

async function handleNormalResponse(response) {
  const data = await response.json();
  responseArea.innerHTML = renderMarkdown(data.response_text); 
  updateUsageInfo(data.usage_metadata);
}

async function handleStreamResponse(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullText = '';
  responseArea.innerHTML = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    fullText += chunk;
    responseArea.innerHTML = renderMarkdown(fullText); 
    responseArea.scrollTop = responseArea.scrollHeight;
  }

  const metadataSeparator = "\n<--METADATA-->\n";
  const idx = fullText.lastIndexOf(metadataSeparator);
  if (idx !== -1) {
    const textPart = fullText.substring(0, idx);
    const meta = fullText.substring(idx + metadataSeparator.length);
    try {
      const metadata = JSON.parse(meta);
      responseArea.innerHTML = renderMarkdown(textPart); 
      updateUsageInfo(metadata);
    } catch (e) { console.error('메타데이터 파싱 실패', e); }
  }
}
