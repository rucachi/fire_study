const DATA_URL = "independent-fire-safety-bank-900.json";
const SUBJECTS = [
  { key: "소방법규", label: "소방법규", prefix: "LG-", description: "법령·관리·점검·안전관리" },
  { key: "소방설비 전기", label: "소방설비 전기", prefix: "EL-", description: "전기회로·감지·경보·비상전원" },
  { key: "소방설비 기계", label: "소방설비 기계", prefix: "ME-", description: "소화설비·배관·펌프·수리계산" }
];
const state = {
  allItems: [], selectedSubject: null, questions: [], index: 0,
  selectedAnswer: null, score: 0, answered: 0, lastCount: 20
};
const $ = (id) => document.getElementById(id);

function show(view) {
  ["setup-view", "quiz-view", "result-view"].forEach((id) => $(id).classList.toggle("hidden", id !== view));
}

function renderSubjects() {
  $("subject-list").innerHTML = SUBJECTS.map((subject) => `
    <button class="subject-card" type="button" data-subject="${subject.key}">
      <strong>${subject.label}</strong><span>${subject.description}</span>
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
  const pool = state.allItems.filter((item) => item.id.startsWith(state.selectedSubject.prefix));
  const selectedCount = $("question-count").value === "all" ? pool.length : Number($("question-count").value);
  state.questions = shuffle(pool).slice(0, selectedCount);
  state.index = 0; state.selectedAnswer = null; state.score = 0; state.answered = 0;
  state.lastCount = selectedCount;
  show("quiz-view");
  renderQuestion();
}

function renderQuestion() {
  const item = state.questions[state.index];
  state.selectedAnswer = null;
  $("progress-label").textContent = `${state.index + 1} / ${state.questions.length}`;
  $("score-label").textContent = `현재 점수 ${state.score}`;
  $("progress-bar").style.width = `${(state.index / state.questions.length) * 100}%`;
  $("question-category").textContent = item.category;
  $("question-id").textContent = item.id;
  $("question-text").textContent = item.question;
  $("options").innerHTML = item.options.map((option, index) => `
    <button class="option" type="button" data-index="${index}" role="radio" aria-checked="false">
      <span class="option-key">${String.fromCharCode(9312 + index)}</span><span>${option || "보기 내용 확인 필요"}</span>
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
  $("feedback").className = "feedback hidden";
  $("feedback").textContent = "";
  $("submit-button").classList.remove("hidden");
  $("submit-button").disabled = true;
  $("next-button").classList.add("hidden");
}

function submitAnswer() {
  const item = state.questions[state.index];
  const correct = state.selectedAnswer === item.answer;
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
  const answerText = item.answer == null ? "정답 미확정 — 원문 또는 공식 기준을 확인하세요." : `정답: ${item.options[item.answer]}`;
  feedback.innerHTML = `<strong>${correct ? "정답입니다." : "오답입니다."}</strong>${answerText}<br>${item.explanation || "해설 준비 중입니다."}<small>출처: ${item.source || "공식 기준 확인 필요"}</small>`;
  $("submit-button").classList.add("hidden");
  $("next-button").classList.remove("hidden");
  $("score-label").textContent = `현재 점수 ${state.score}`;
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
    state.allItems = Array.isArray(data) ? data : data.items;
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
$("back-button").addEventListener("click", () => show("setup-view"));
$("result-home-button").addEventListener("click", () => show("setup-view"));
$("reset-progress").addEventListener("click", () => {
  state.score = 0;
  localStorage.clear();
  alert("학습 기록을 초기화했습니다.");
});
init();
