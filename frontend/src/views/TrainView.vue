<template>
  <div class="quiz">
    <div class="quiz-head">
      <div class="page-head" style="margin:0">
        <span class="ph-bar"></span>
        <h1 class="serif">方证练习</h1>
      </div>
      <div class="score-pill" v-if="answeredCount">正确 {{ correctCount }}/{{ answeredCount }}</div>
    </div>

    <!-- 章节筛选 -->
    <div class="filter-group">
      <span class="filter-label">章节</span>
      <div class="chips">
        <button
          v-for="ch in chapterOptions"
          :key="ch"
          class="chip-btn"
          :class="{ active: activeChapter === ch }"
          @click="selectChapter(ch)"
        >{{ ch }}</button>
      </div>
    </div>

    <!-- 题型分类 -->
    <div class="filter-group">
      <span class="filter-label">题型</span>
      <div class="chips">
        <button
          v-for="c in categoryOptions"
          :key="c"
          class="chip-btn small"
          :class="{ active: activeCategory === c }"
          @click="selectCategory(c)"
        >{{ c }}</button>
      </div>
    </div>

    <div v-if="loading" class="card"><p class="muted">正在加载题库…</p></div>

    <template v-else-if="questions.length && !finished">
      <div class="question-nav">
        <button
          v-for="(q, i) in questions"
          :key="q.id"
          class="qdot"
          :class="{ cur: i === current, done: answers[q.id] !== undefined, right: answers[q.id] === q.answer }"
          :title="`第 ${i + 1} 题`"
          @click="current = i"
        >{{ i + 1 }}</button>
      </div>

      <section class="card qcard">
        <div class="qmeta">
          <span class="qno">第 {{ current + 1 }} / {{ questions.length }} 题</span>
          <span class="chip">{{ questions[current].chapter }}</span>
          <span class="chip subtle">{{ questions[current].category }}</span>
        </div>

        <p class="qstem">{{ questions[current].stem }}</p>

        <div class="options">
          <button
            v-for="(opt, i) in questions[current].options"
            :key="opt"
            class="option"
            :class="optionClass(opt, questions[current])"
            :disabled="answers[questions[current].id] !== undefined"
            @click="choose(questions[current], opt)"
          >
            <span class="optkey">{{ 'ABCD'[i] }}</span>
            <span class="opttext">{{ opt }}</span>
            <span v-if="isRevealed(questions[current]) && opt === questions[current].answer" class="mark">✓</span>
            <span v-else-if="isRevealed(questions[current]) && opt === answers[questions[current].id]" class="mark wrong">✕</span>
          </button>
        </div>

        <!-- 答对答错都显示解析 -->
        <div v-if="isRevealed(questions[current])" class="explain-box" :class="isCorrect(questions[current]) ? 'right' : 'wrongbox'">
          <div class="explain-head">
            <span class="verdict">{{ isCorrect(questions[current]) ? '✓ 回答正确' : '✕ 回答错误' }}</span>
            <span>正确答案：<b>{{ questions[current].answer }}</b></span>
            <span v-if="!isCorrect(questions[current])">你选了：{{ answers[questions[current].id] }}</span>
          </div>
          <div class="explain-body">
            <span class="explain-tag">解析</span>
            <span>{{ questions[current].explain }}</span>
          </div>
        </div>
      </section>

      <div class="qactions">
        <button class="btn ghost" :disabled="current === 0" @click="current--">上一题</button>
        <button class="btn ghost" :disabled="current >= questions.length - 1" @click="current++">下一题</button>
        <button class="btn primary" @click="submit" :disabled="answeredCount < questions.length">交卷汇总</button>
        <button class="btn ghost" @click="reset">重新练习</button>
      </div>
    </template>

    <!-- 汇总页 -->
    <template v-else-if="finished">
      <section class="card summary">
        <div class="sum-head">
          <h2>练习汇总</h2>
          <p class="muted">{{ activeChapter }} · {{ activeCategory }} · 共 {{ questions.length }} 题</p>
        </div>
        <div class="sum-score">
          <div class="ring" :style="{ '--pct': correctPct + '%' }">
            <div class="ring-in"><b>{{ correctPct }}%</b><span>正确率</span></div>
          </div>
          <div class="sum-stats">
            <div><b>{{ correctCount }}</b><span>答对</span></div>
            <div><b>{{ questions.length - correctCount }}</b><span>答错</span></div>
            <div><b>{{ questions.length }}</b><span>总题数</span></div>
          </div>
        </div>
        <div class="sum-list">
          <div v-for="(q, i) in questions" :key="q.id" class="sum-item" :class="answers[q.id] === q.answer ? 'ok' : 'bad'">
            <div class="sum-item-head">
              <span class="sum-no">{{ i + 1 }}</span>
              <span class="sum-badge">{{ answers[q.id] === q.answer ? '正确' : '错误' }}</span>
              <span class="sum-stem">{{ q.stem }}</span>
            </div>
            <div class="sum-detail">
              正确答案：<b>{{ q.answer }}</b><span v-if="answers[q.id] !== q.answer"> · 你选了：{{ answers[q.id] }}</span>
            </div>
            <div class="sum-explain"><span class="explain-tag">解析</span>{{ q.explain }}</div>
          </div>
        </div>
        <div class="qactions center">
          <button class="btn primary" @click="reset">再练一组</button>
          <button class="btn ghost" @click="finished = false">返回查看题目</button>
        </div>
      </section>
    </template>

    <div v-else class="card"><p class="muted">该筛选下暂无题目，试试切换章节或题型。</p></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import bank from '@/data/quizbank.json'

interface Question {
  id: string
  category: string
  chapter: string
  stem: string
  answer: string
  options: string[]
  explain: string
}

const allQuestions: Question[] = (bank.questions as Omit<Question, 'id'>[]).map((q, i) => ({
  ...q,
  id: `q_${i}`,
}))

const chapterOptions = ['全部章节', '伤寒论', '温病学', '金匮要略']
const categoryOptions = ['全部题型', '辨证选方', '条文选方', '典籍归属', '方药对应']
const activeChapter = ref('全部章节')
const activeCategory = ref('全部题型')

const questions = ref<Question[]>([])
const loading = ref(true)
const current = ref(0)
const answers = reactive<Record<string, string>>({})
const finished = ref(false)

const answeredCount = computed(() => questions.value.filter(q => answers[q.id] !== undefined).length)
const correctCount = computed(() => questions.value.filter(q => answers[q.id] === q.answer).length)
const correctPct = computed(() => questions.value.length ? Math.round(correctCount.value / questions.value.length * 100) : 0)

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function load() {
  loading.value = true
  finished.value = false
  let pool = allQuestions
  if (activeChapter.value !== '全部章节') pool = pool.filter(q => q.chapter === activeChapter.value)
  if (activeCategory.value !== '全部题型') pool = pool.filter(q => q.category === activeCategory.value)
  // 抽满一组（最多 12 题），保证题量充足
  questions.value = shuffle(pool).slice(0, 12)
  current.value = 0
  for (const k of Object.keys(answers)) delete answers[k]
  loading.value = false
}

function selectChapter(ch: string) { activeChapter.value = ch; load() }
function selectCategory(c: string) { activeCategory.value = c; load() }
function reset() { load() }

function isRevealed(q: Question) { return answers[q.id] !== undefined }
function isCorrect(q: Question) { return answers[q.id] === q.answer }
function optionClass(opt: string, q: Question) {
  const chosen = answers[q.id]
  if (chosen === undefined) return ''
  if (opt === q.answer) return 'correct'
  if (opt === chosen) return 'wrong'
  return ''
}
function choose(q: Question, opt: string) {
  if (answers[q.id] !== undefined) return
  answers[q.id] = opt
}
function submit() {
  if (answeredCount.value < questions.value.length) return
  finished.value = true
}

onMounted(load)
</script>

<style scoped>
.quiz { max-width: 900px; margin: 0 auto; }
.quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.quiz-head h1 { margin: 0 0 4px; font-size: 27px; color: var(--primary-deep); }
.quiz-head p { margin: 0; }
.score-pill { padding: 8px 18px; border-radius: 999px; font-weight: 700; color: var(--primary-deep);
  background: rgba(255,255,255,.7); border: 1px solid rgba(255,255,255,.9); }

.filter-group { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.filter-label { font-size: 13px; font-weight: 700; color: var(--text-2); min-width: 34px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip-btn { padding: 8px 18px; border-radius: 999px; font-size: 14px; font-weight: 700; color: var(--text-2);
  background: rgba(255,255,255,.62); border: 1px solid rgba(255,255,255,.88);
  -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); transition: .18s var(--ease); }
.chip-btn.small { padding: 6px 14px; font-size: 13px; }
.chip-btn:hover { transform: translateY(-2px); background: rgba(255,255,255,.85); }
.chip-btn.active { color: #fff; border-color: transparent;
  background: linear-gradient(135deg,#3AA0FF,#0A6FE8); box-shadow: 0 8px 20px rgba(10,111,232,.3); }

.question-nav { display: flex; gap: 8px; flex-wrap: wrap; margin: 20px 0 18px; }
.qdot { width: 36px; height: 36px; border-radius: 12px; font-size: 13px; font-weight: 700; cursor: pointer;
  background: rgba(255,255,255,.6); border: 1px solid rgba(255,255,255,.85); color: var(--text-2); transition: .15s; }
.qdot.done { background: rgba(10,132,255,.16); color: var(--primary-deep); }
.qdot.right { background: var(--primary); color: #fff; border-color: var(--primary); }
.qdot.cur { outline: 2px solid var(--primary); outline-offset: 2px; }

.qcard { padding: 30px; }
.qmeta { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; flex-wrap: wrap; }
.qno { font-weight: 700; color: var(--primary-deep); margin-right: 4px; }
.qstem { font-size: 18px; font-weight: 600; line-height: 1.7; margin-bottom: 24px; color: var(--text); }

.options { display: grid; gap: 12px; }
.option { display: flex; align-items: center; gap: 14px; text-align: left; padding: 15px 18px; border-radius: 14px;
  background: rgba(255,255,255,.65); border: 1px solid rgba(255,255,255,.9); font-size: 15px; color: var(--text);
  cursor: pointer; transition: .16s var(--ease); }
.option:hover:not(:disabled) { transform: translateX(4px); border-color: var(--primary); background: rgba(255,255,255,.88); }
.option:disabled { cursor: default; }
.optkey { flex: none; width: 32px; height: 32px; border-radius: 9px; display: grid; place-items: center;
  font-weight: 800; background: rgba(10,132,255,.12); color: var(--primary-deep); }
.opttext { flex: 1; }
.mark { font-weight: 800; color: #1E8E3E; }
.mark.wrong { color: var(--error); }
.option.correct { background: rgba(52,199,89,.16); border-color: rgba(52,199,89,.55); }
.option.correct .optkey { background: #34C759; color: #fff; }
.option.wrong { background: rgba(255,69,58,.13); border-color: rgba(255,69,58,.5); }
.option.wrong .optkey { background: var(--error); color: #fff; }

.explain-box { margin-top: 22px; padding: 16px 18px; border-radius: 14px; border: 1px solid rgba(255,255,255,.9); }
.explain-box.right { background: rgba(52,199,89,.1); }
.explain-box.wrongbox { background: rgba(255,69,58,.08); }
.explain-head { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; font-size: 14px; margin-bottom: 10px; }
.explain-head .verdict { font-weight: 800; }
.explain-box.right .verdict { color: #1E8E3E; }
.explain-box.wrongbox .verdict { color: var(--error); }
.explain-head b { color: var(--primary-deep); }
.explain-body { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.7; color: var(--text); }
.explain-tag { flex: none; padding: 1px 9px; border-radius: 6px; font-size: 12px; font-weight: 700;
  color: var(--primary-deep); background: rgba(10,132,255,.14); }

.qactions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 22px; }
.qactions.center { justify-content: center; }

/* 汇总 */
.summary { padding: 32px; }
.sum-head { text-align: center; margin-bottom: 24px; }
.sum-head h2 { font-size: 24px; color: var(--primary-deep); margin-bottom: 4px; }
.sum-head p { margin: 0; }
.sum-score { display: flex; align-items: center; justify-content: center; gap: 48px; flex-wrap: wrap; margin-bottom: 28px; }
.ring { width: 150px; height: 150px; border-radius: 50%; display: grid; place-items: center;
  background: conic-gradient(var(--primary) var(--pct), rgba(10,132,255,.12) 0); }
.ring-in { width: 120px; height: 120px; border-radius: 50%; background: rgba(255,255,255,.92);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.ring-in b { font-size: 34px; color: var(--primary-deep); }
.ring-in span { font-size: 13px; color: var(--text-2); }
.sum-stats { display: flex; gap: 32px; }
.sum-stats div { display: flex; flex-direction: column; align-items: center; }
.sum-stats b { font-size: 28px; color: var(--primary-deep); }
.sum-stats span { font-size: 13px; color: var(--text-2); }
.sum-list { display: grid; gap: 12px; }
.sum-item { padding: 16px 18px; border-radius: 14px; border: 1px solid rgba(255,255,255,.9);
  background: rgba(255,255,255,.66); }
.sum-item.ok { border-left: 4px solid #34C759; }
.sum-item.bad { border-left: 4px solid var(--error); }
.sum-item-head { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; }
.sum-no { flex: none; width: 24px; height: 24px; border-radius: 8px; display: grid; place-items: center;
  font-size: 12px; font-weight: 800; background: rgba(10,132,255,.12); color: var(--primary-deep); }
.sum-badge { flex: none; padding: 1px 8px; border-radius: 6px; font-size: 12px; font-weight: 700; }
.sum-item.ok .sum-badge { background: rgba(52,199,89,.16); color: #1E8E3E; }
.sum-item.bad .sum-badge { background: rgba(255,69,58,.14); color: var(--error); }
.sum-stem { flex: 1; font-weight: 600; }
.sum-detail { margin: 8px 0 0 34px; font-size: 13.5px; color: var(--text-2); }
.sum-detail b { color: var(--primary-deep); }
.sum-explain { margin: 6px 0 0 34px; font-size: 13.5px; line-height: 1.6; display: flex; gap: 8px; align-items: flex-start; }

@media(max-width: 620px){ .qcard,.summary { padding: 18px; } .qstem { font-size: 16px; } .sum-score { gap: 24px; } .sum-stats { gap: 18px; } }
</style>
