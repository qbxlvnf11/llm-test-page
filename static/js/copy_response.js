

(function () {
  const responseArea = document.getElementById('response-area');
  const copyButton = document.getElementById('copy-button');
  const copyButtonText = document.getElementById('copy-button-text');

  if (!responseArea || !copyButton) return;

  function hasContent() {
    // rendered HTML이 있을 수 있으므로 textContent로 검사
    const txt = responseArea.textContent || '';
    return txt.trim().length > 0 && !/결과가 여기에 표시됩니다/.test(txt);
  }

  function updateButtonState() {
    copyButton.disabled = !hasContent();
  }

  // 복사 함수: responseArea의 텍스트(plain) 복사
  async function copyResponseText() {
    try {
      const textToCopy = responseArea.innerText || responseArea.textContent || '';
      if (!textToCopy || !textToCopy.trim()) {
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        // fallback for older browsers
        const ta = document.createElement('textarea');
        ta.value = textToCopy;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }

      // 시각적 피드백
      const original = copyButtonText.textContent;
      copyButtonText.textContent = '복사됨!';
      setTimeout(() => {
        copyButtonText.textContent = original;
      }, 1500);
    } catch (err) {
      console.error('Copy failed', err);
      // 에러 피드백
      const original = copyButtonText.textContent;
      copyButtonText.textContent = '복사 실패';
      setTimeout(() => {
        copyButtonText.textContent = original;
      }, 1500);
    }
  }

  copyButton.addEventListener('click', copyResponseText);

  // MutationObserver로 response-area 내부 변경 감지 (내부 HTML 변경 시에도 동작)
  const observer = new MutationObserver(() => {
    updateButtonState();
  });

  observer.observe(responseArea, { childList: true, subtree: true, characterData: true });

  // 초기 상태 설정
  updateButtonState();

  // 선택적으로, 페이지가 내용을 덮어쓰는 다른 스크립트와 충돌 시
  // 간단한 인터벌로도 상태 갱신을 보장
  setInterval(updateButtonState, 2000);
})();