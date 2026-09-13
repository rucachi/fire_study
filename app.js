const DATA_URL = "theme-bank.json?v=" + new Date().getTime();
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
  "theme-5-fire-electrical-anki": {
    label: "소방설비기사 전기 Anki",
    description: "Anki 전기 학습 자료"
  }
};
const state = {
  allItems: [], selectedSubject: null, questions: [], index: 0,
  selectedAnswer: null, score: 0, answered: 0, lastCount: 20
};
const $ = (id) => document.getElementById(id);

function categoryLabel(key) {
  return (SUBJECT_LABELS[key] || {}).label || key;
}

function show(view) {
  ["setup-view", "quiz-view", "result-view"].forEach((id) => $(id).classList.toggle("hidden", id !== view));
}

function parseMarkdown(text) {
  if (!text) return "";
  // Fix image paths from relative markdown to web root
  let html = text.replace(/\.\.\/images\//g, 'themes/images/');
  // Convert markdown images to HTML
  html = html.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0; display: block;">');
  // Convert bold text
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  return html;
}

function renderSubjects() {
  $("subject-list").innerHTML = SUBJECTS.map((subject) => `
    <button class="subject-card" type="button" data-subject="${subject.key}">
      <strong>${subject.displayLabel}</strong><span>${subject.description}</span>
    </button>
  `).join("");
  document.querySelectorAll("[data-subject]").forEach((button) => button.addEventListener("click", () => {
    state.selectedSubject = SUBJECTS.find((subject) => subject.key === button.dataset.subject);
    document.querySelectorAll(".subject-card").forEach((card) => card.classList.remove("selected"));
    button.classList.add("selected");
    $("start-button").disabled = false;
  }));
}

function shuffle(items) {
  return [...items].sort(() => Math.random() - .5);
}

function startQuiz() {
  const pool = state.selectedSubject.items;
  const selectedCount = $("question-count").value === "all" ? pool.length : Number($("question-count").value);
  state.questions = shuffle(pool).slice(0, selectedCount);
  state.index = 0; state.selectedAnswer = null; state.score = 0; state.answered = 0;
  state.lastCount = selectedCount;
  show("quiz-view");
  renderQuestion();
}

function goHome() {
  state.selectedSubject = null;
  state.questions = [];
  show("setup-view");
}

function renderQuestion() {
  const item = state.questions[state.index];
  state.selectedAnswer = null;
  $("progress-label").textContent = `${state.index + 1} / ${state.questions.length}`;
  $("score-label").textContent = `현재 점수 ${state.score}`;
  $("progress-bar").style.width = `${(state.index / state.questions.length) * 100}%`;
  $("question-category").textContent = categoryLabel(state.selectedSubject.key);
  $("question-id").textContent = `문제 ${state.index + 1}`;
  $("question-text").innerHTML = parseMarkdown(item.question);

  const hasOptions = item.options && item.options.length > 0;

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
    $("submit-button").textContent = "해설 보기";
    $("submit-button").disabled = false;
  }

  $("feedback").className = "feedback hidden";
  $("feedback").textContent = "";
  $("submit-button").classList.remove("hidden");
  $("next-button").classList.add("hidden");
}

function submitAnswer() {
  const item = state.questions[state.index];
  const hasOptions = item.options && item.options.length > 0;

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
    feedback.innerHTML = `<strong>${correct ? "✅ 정답입니다!" : "❌ 오답입니다."}</strong>${answerText}<br>${parseMarkdown(item.explanation) || "해설 준비 중입니다."}<small>출처: ${item.source || "공식 기준 확인 필요"}</small>`;
    $("score-label").textContent = `현재 점수 ${state.score}`;
  } else {
    // Essay/calculation: just reveal the answer and explanation
    state.answered++;
    const feedback = $("feedback");
    feedback.className = "feedback correct";
    const answer = parseMarkdown(item.answerText) || parseMarkdown(item.explanation) || "해설 없음";
    feedback.innerHTML = `<strong>📝 답안 및 해설</strong>${answer}<br>${item.explanation && item.explanation !== item.answerText ? parseMarkdown(item.explanation) : ""}<small>출처: ${item.source || "공식 기준 확인 필요"}</small>`;
  }

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
  const percent = Math.round((state.score / state.questions.length) * 100);
  $("result-summary").textContent = `${state.questions.length}문항 중 ${state.score}문항 정답 (${percent}점)`;
  $("result-breakdown").innerHTML = `
    <div><strong>${state.questions.length}</strong><span>풀이 문항</span></div>
    <div><strong>${state.score}</strong><span>정답</span></div>
    <div><strong>${state.questions.length - state.score}</strong><span>오답</span></div>
  `;
}

async function init() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    SUBJECTS = data.subjects.map((subject) => {
      const metadata = SUBJECT_LABELS[subject.key] || {
        label: subject.key,
        description: "학습 문제"
      };
      return {
        ...subject,
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
$("back-button").addEventListener("click", goHome);
$("result-home-button").addEventListener("click", goHome);
$("home-button").addEventListener("click", goHome);
$("reset-progress").addEventListener("click", () => {
  state.score = 0;
  localStorage.clear();
  alert("학습 기록을 초기화했습니다.");
});
init();
