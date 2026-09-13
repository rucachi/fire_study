const DATA_URL = "theme-bank.json?v=13";
let SUBJECTS = [];
const SUBJECT_LABELS = {
  "theme-1-fire-principles": {
    label: "소방원론",
    description: "연소·화재·소화·위험물"
  },
  "theme-3-fire-laws": {
    label: "소방관계법규",
    description: "소방기본법·시설법·위험물법"
  },
  "theme-4-fire-electrical-facilities": {
    label: "소방전기시설의 구조 및 원리",
    description: "감지·경보·유도등·비상전원"
  },
  "theme-6-fire-electrical-practical": {
    label: "소방전기 실기",
    description: "주관식·계산·서술형 문제"
  }
};
const state = {
  allItems: [], selectedSubject: null, questions: [], index: 0,
  selectedAnswer: null, score: 0, answered: 0, lastCount: 20,
  isEssaySubject: false
};
const $ = (id) => document.getElementById(id);

function categoryLabel(key) {
  return (SUBJECT_LABELS[key] || {}).label || key;
}

function normalizeItem(item) {
  const options = Array.isArray(item.options)
    ? item.options.map((option) => String(option ?? "").trim()).filter(Boolean)
    : [];
  const extraOptions = options.length > 4 ? options.slice(4) : [];
  const explanation = [item.explanation, ...extraOptions].filter(Boolean).join("\n\n");

  return {
    ...item,
    options: options.slice(0, 4),
    explanation
  };
}

function isMultipleChoice(item) {
  return item.options.length === 4
    && Number.isInteger(item.answer)
    && item.answer >= 0
    && item.answer < 4;
}

function show(view) {
  ["setup-view", "quiz-view", "result-view"].forEach((id) => $(id).classList.toggle("hidden", id !== view));
}

/** Escape HTML special characters to prevent XSS */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

function parseMarkdown(text) {
  if (!text) return "";
  // Escape HTML entities first (XSS prevention)
  let html = escapeHtml(text);
  // Fix image paths from relative markdown to web root
  html = html.replace(/\.\.\/images\//g, 'themes/images/');
  // Convert markdown images to HTML (safe because src comes from our own data after escaping)
  html = html.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0; display: block;">');
  // Convert bold text
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  return html;
}

function parseQuestion(text) {
  const withoutImages = String(text || "")
    .replace(/\*\*\[\s*그림\s*\]\*\*/g, "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return parseMarkdown(withoutImages);
}

/** Format date for Korean localization (e.g. 2026년 9월 13일 오후 7시 14분) */
function formatDateTime(date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? '오후' : '오전';
  const displayHours = hours % 12 || 12;
  return `${year}년 ${month}월 ${day}일 ${ampm} ${displayHours}시${minutes}분`;
}

function renderSubjects() {
  $("subject-list").innerHTML = SUBJECTS.map((subject) => `
    <button class="subject-card" type="button" data-subject="${escapeHtml(subject.key)}">
      <strong>${escapeHtml(subject.displayLabel)}</strong><span>${escapeHtml(subject.description)}</span><span>${subject.items.length}문항</span>
    </button>
  `).join("");
  $("total-count").textContent = SUBJECTS.reduce((total, subject) => total + subject.items.length, 0);
  document.querySelectorAll("[data-subject]").forEach((button) => button.addEventListener("click", () => {
    state.selectedSubject = SUBJECTS.find((subject) => subject.key === button.dataset.subject);
    document.querySelectorAll(".subject-card").forEach((card) => card.classList.remove("selected"));
    button.classList.add("selected");
    $("start-button").disabled = false;
  }));
}

function shuffle(items) {
  const array = [...items];
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function startQuiz() {
  if (!state.selectedSubject) return;
  const pool = state.selectedSubject.items;
  if (!pool.length) return;
  const selectedCount = $("question-count").value === "all" ? pool.length : Number($("question-count").value);
  const isRandom = $("question-order") ? $("question-order").value === "random" : true;
  const basePool = isRandom ? shuffle(pool) : [...pool];
  state.questions = basePool.slice(0, selectedCount);
  state.index = 0; state.selectedAnswer = null; state.score = 0; state.answered = 0;
  state.lastCount = selectedCount;
  // Check if this is an essay-only subject (no options on any item)
  state.isEssaySubject = state.questions.every((q) => !isMultipleChoice(q));
  show("quiz-view");
  renderQuestion();
}

/** Confirm before leaving quiz in progress */
function confirmGoHome() {
  if (state.questions.length > 0 && state.answered > 0 && state.answered < state.questions.length) {
    if (!confirm("진행 중인 학습을 종료할까요? 현재까지의 기록은 저장되지 않습니다.")) return;
  }
  goHome();
}

function goHome() {
  state.selectedSubject = null;
  state.questions = [];
  state.isEssaySubject = false;
  document.querySelectorAll(".subject-card").forEach((card) => card.classList.remove("selected"));
  $("start-button").disabled = true;
  show("setup-view");
}

function renderQuestion() {
  const item = state.questions[state.index];
  state.selectedAnswer = null;
  $("progress-label").textContent = `${state.index + 1} / ${state.questions.length}`;
  $("score-label").textContent = state.isEssaySubject ? "주관식" : `현재 점수 ${state.score}`;
  $("progress-bar").style.width = `${(state.index / state.questions.length) * 100}%`;
  updateSessionStats();
  $("question-category").textContent = categoryLabel(state.selectedSubject.key);
  $("question-id").textContent = `문제 ${state.index + 1}`;
  $("question-text").innerHTML = parseQuestion(item.question);

  const hasOptions = isMultipleChoice(item);

  if (hasOptions) {
    // Multiple-choice question: show selectable options
    $("options").innerHTML = item.options.map((option, index) => `
      <button class="option" type="button" data-index="${index}" role="radio" aria-checked="false">
        <span class="option-key">${String.fromCharCode(9312 + index)}</span><span>${parseMarkdown(option) || "보기 내용 확인 필요"}</span>
      </button>
    `).join("");
    document.querySelectorAll(".option").forEach((button) => button.addEventListener("click", () => {
      if ($("feedback").classList.contains("hidden") === false) return;
      state.selectedAnswer = Number(button.dataset.index);
      document.querySelectorAll(".option").forEach((option) => {
        option.classList.toggle("selected", option === button);
        option.setAttribute("aria-checked", option === button ? "true" : "false");
      });
      $("submit-button").disabled = false;
    }));
    $("submit-button").textContent = "정답 확인";
    $("submit-button").disabled = true;
  } else {
    // Essay/calculation question: show a single reveal button
    $("options").innerHTML = "";
    $("submit-button").textContent = "답안 보기";
    $("submit-button").disabled = false;
  }

  $("feedback").className = "feedback hidden";
  $("feedback").textContent = "";
  $("submit-button").classList.remove("hidden");
  $("next-button").classList.add("hidden");
}

function updateSessionStats() {
  const completed = state.answered;
  const total = state.questions.length;
  const progress = total ? Math.round((state.index / total) * 100) : 0;
  $("rail-progress").textContent = `진행률 ${progress}%`;
  $("answered-label").textContent = `${completed} / ${total}`;
  if (state.isEssaySubject) {
    $("accuracy-label").textContent = "주관식";
  } else {
    const accuracy = completed ? Math.round((state.score / completed) * 100) : 0;
    $("accuracy-label").textContent = `${accuracy}%`;
  }
}

function submitAnswer() {
  const item = state.questions[state.index];
  const hasOptions = isMultipleChoice(item);

  if (hasOptions) {
    // Multiple-choice: grade the answer
    const correct = item.answer != null && state.selectedAnswer === item.answer;
    if (correct) state.score++;
    state.answered++;
    document.querySelectorAll(".option").forEach((button) => {
      const index = Number(button.dataset.index);
      button.disabled = true;
      if (index === item.answer) button.classList.add("correct");
      if (index === state.selectedAnswer && !correct) button.classList.add("incorrect");
    });
    const feedback = $("feedback");
    feedback.className = `feedback ${correct ? "correct" : "incorrect"}`;
    const answerText = item.answer == null
      ? `답안: ${parseMarkdown(item.answerText) || "원문 답안 확인 필요"}`
      : `정답: ⓘ ${parseMarkdown(item.options[item.answer])}`;
    feedback.innerHTML = `<strong>${correct ? "✅ 정답입니다!" : "❌ 오답입니다."}</strong>${answerText}<br>${parseMarkdown(item.explanation) || "해설 준비 중입니다."}<small>출처: ${escapeHtml(item.source) || "공식 기준 확인 필요"}</small>`;
    $("score-label").textContent = `현재 점수 ${state.score}`;
  } else {
    // Essay/calculation: just reveal the answer and explanation
    state.answered++;
    const feedback = $("feedback");
    feedback.className = "feedback correct";
    const answer = parseMarkdown(item.answerText) || parseMarkdown(item.explanation) || "해설 없음";
    const extraExplanation = item.explanation && item.explanation !== item.answerText ? parseMarkdown(item.explanation) : "";
    feedback.innerHTML = `<strong>📝 답안 및 해설</strong>${answer}${extraExplanation ? "<br>" + extraExplanation : ""}<small>출처: ${escapeHtml(item.source) || "공식 기준 확인 필요"}</small>`;
  }

  updateSessionStats();

  $("submit-button").classList.add("hidden");
  $("next-button").classList.remove("hidden");
}

function nextQuestion() {
  if (state.index + 1 >= state.questions.length) return showResult();
  state.index++;
  renderQuestion();
}

function showResult() {
  $("progress-bar").style.width = "100%";
  show("result-view");

  const nowStr = formatDateTime(new Date());
  $("result-title").textContent = `학습완료(${nowStr})`;

  if (state.isEssaySubject) {
    $("result-summary").textContent = `${state.questions.length}문항 학습완료`;
    $("result-breakdown").innerHTML = `
      <div><strong>${state.questions.length}</strong><span>풀이 문항</span></div>
      <div><strong>주관식</strong><span>채점 없음</span></div>
      <div><strong>✓</strong><span>학습완료</span></div>
    `;
  } else {
    const percent = state.questions.length ? Math.round((state.score / state.questions.length) * 100) : 0;
    $("result-summary").textContent = `${state.questions.length}문항 중 ${state.score}문항 정답 (${percent}점)`;
    $("result-breakdown").innerHTML = `
      <div><strong>${state.questions.length}</strong><span>풀이 문항</span></div>
      <div><strong>${state.score}</strong><span>정답</span></div>
      <div><strong>${state.questions.length - state.score}</strong><span>오답</span></div>
    `;
  }
}

async function init() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    SUBJECTS = data.subjects.map((subject) => {
      const key = subject.key || subject.id;
      const metadata = SUBJECT_LABELS[key] || {
        label: key,
        description: "학습 문제"
      };
      return {
        ...subject,
        items: (subject.items || []).map(normalizeItem),
        key,
        displayLabel: metadata.label,
        description: metadata.description
      };
    });
    state.allItems = SUBJECTS.flatMap((subject) => subject.items);
    renderSubjects();
  } catch (error) {
    $("subject-list").innerHTML = `<p class="error">문제 데이터를 불러오지 못했습니다. GitHub Pages에서 JSON 파일 경로를 확인하세요.</p>`;
    console.error(error);
  }
}

$("start-button").addEventListener("click", startQuiz);
$("submit-button").addEventListener("click", submitAnswer);
$("next-button").addEventListener("click", nextQuestion);
$("retry-button").addEventListener("click", startQuiz);
$("back-button").addEventListener("click", confirmGoHome);
$("result-home-button").addEventListener("click", goHome);
$("home-button").addEventListener("click", confirmGoHome);
$("reset-progress").addEventListener("click", () => {
  state.score = 0;
  state.answered = 0;
  alert("학습 기록을 초기화했습니다.");
});
init();
