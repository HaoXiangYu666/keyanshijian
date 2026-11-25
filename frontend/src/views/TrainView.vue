<template>
  <div class="quiz">
    <div class="quiz-head">
      <div>
        <h1>方证练习</h1>
        <p class="muted">选题分类，即时判分。真实典籍数据，随手练一练。</p>
      </div>
      <div class="score-pill" v-if="answeredCount">正确 {{ correctCount }}/{{ answeredCount }}</div>
    </div>

    <!-- 分类标签 -->
    <div class="cat-tabs" role="tablist" aria-label="题型分类">
      <button
        v-for="c in categories"
        :key="c.key"
        class="cat-tab"
        :class="{ active: activeCat === c.key }"
        role="tab"
        :aria-selected="activeCat === c.key"
        @click="switchCat(c.key)"
      >
        <span class="cat-name">{{ c.name }}</span>
        <span class="cat-count">{{ c.count }}</span>
      </button>
    </div>

    <div v-if="loading" class="card"><p class="muted">正在加载题库…</p></div>

    <template v-else-if="questions.length">
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
          <span class="chip">{{ activeCatName }}</span>
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

        <div v-if="isRevealed(questions[current])" class="explain">
          <b>正确答案：{{ questions[current].answer }}</b>
          <span v-if="answers[questions[current].id] === questions[current].answer" class="ok">回答正确</span>
          <span v-else class="no">你选了：{{ answers[questions[current].id] }}</span>
          <span v-if="questions[current].hint" class="hint">{{ questions[current].hint }}</span>
        </div>
      </section>

      <div class="qactions">
        <button class="btn ghost" :disabled="current === 0" @click="current--">上一题</button>
        <button class="btn ghost" :disabled="current >= questions.length - 1" @click="current++">下一题</button>
        <button class="btn primary" @click="reset">重新练习</button>
      </div>
    </template>

    <div v-else class="card"><p class="muted">该分类暂无题目，可切换其他分类。</p></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import bank from '@/data/quizbank.json'

interface Question {
  id: string
  category: string
  stem: string
  answer: string
  options: string[]
  hint?: string
}

const allQuestions: Question[] = (bank.questions as Omit<Question, 'id'>[]).map((q, i) => ({
  ...q,
  id: `q_${i}`,
}))

const categories = computed(() => {
  const names: Record<string, string> = {
    '辨证选方': '辨证选方', '条文选方': '条文选方',
    '典籍归属': '典籍归属', '方药对应': '方药对应',
  }
  return Object.keys(names).map(key => ({
    key,
    name: names[key],
    count: allQuestions.filter(q => q.category === key).length,
  }))
})

const activeCat = ref('辨证选方')
const activeCatName = computed(() => categories.value.find(c => c.key === activeCat.value)?.name || '')
const questions = ref<Question[]>([])
const loading = ref(true)
const current = ref(0)
const answers = reactive<Record<string, string>>({})

const answeredCount = computed(() => questions.value.filter(q => answers[q.id] !== undefined).length)
const correctCount = computed(() => questions.value.filter(q => answers[q.id] === q.answer).length)

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function load(cat: string) {
  loading.value = true
  questions.value = shuffle(allQuestions.filter(q => q.category === cat))
  current.value = 0
  for (const k of Object.keys(answers)) delete answers[k]
  loading.value = false
}

function switchCat(cat: string) {
  activeCat.value = cat
  load(cat)
}

function isRevealed(q: Question) {
  return answers[q.id] !== undefined
}

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

function reset() {
  load(activeCat.value)
}

onMounted(() => load(activeCat.value))
</script>

<style scoped>
.quiz { max-width: 880px; margin: 0 auto; }
.quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.quiz-head h1 { margin: 0 0 4px; font-size: 27px; color: var(--primary-deep); }
.quiz-head p { margin: 0; }
.score-pill { padding: 8px 18px; border-radius: 999px; font-weight: 700; color: var(--primary-deep);
  background: rgba(255,255,255,.7); border: 1px solid rgba(255,255,255,.9); }

.cat-tabs { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.cat-tab { display: flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 999px; font-size: 14px; font-weight: 700;
  color: var(--text-2); background: rgba(255,255,255,.58); border: 1px solid rgba(255,255,255,.85);
  -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); transition: .18s var(--ease); }
.cat-tab:hover { transform: translateY(-2px); background: rgba(255,255,255,.8); }
.cat-tab.active { color: #fff; border-color: transparent;
  background: linear-gradient(135deg,#3AA0FF,#0A6FE8); box-shadow: 0 8px 22px rgba(10,111,232,.32); }
.cat-count { font-size: 12px; padding: 1px 8px; border-radius: 999px; background: rgba(10,132,255,.12); color: var(--primary-deep); }
.cat-tab.active .cat-count { background: rgba(255,255,255,.25); color: #fff; }

.question-nav { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.qdot { width: 36px; height: 36px; border-radius: 12px; font-size: 13px; font-weight: 700; cursor: pointer;
  background: rgba(255,255,255,.55); border: 1px solid rgba(255,255,255,.8); color: var(--text-2); transition: .15s; }
.qdot.done { background: rgba(10,132,255,.16); color: var(--primary-deep); }
.qdot.right { background: var(--primary); color: #fff; border-color: var(--primary); }
.qdot.cur { outline: 2px solid var(--primary); outline-offset: 2px; }

.qcard { padding: 28px; }
.qmeta { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.qno { font-weight: 700; color: var(--primary-deep); }
.qstem { font-size: 18px; font-weight: 600; line-height: 1.7; margin-bottom: 24px; color: var(--text); }

.options { display: grid; gap: 12px; }
.option { display: flex; align-items: center; gap: 14px; text-align: left; padding: 14px 16px; border-radius: 14px;
  background: rgba(255,255,255,.62); border: 1px solid rgba(255,255,255,.85); font-size: 15px; color: var(--text);
  cursor: pointer; transition: .16s var(--ease); }
.option:hover:not(:disabled) { transform: translateX(4px); border-color: var(--primary); background: rgba(255,255,255,.85); }
.option:disabled { cursor: default; }
.optkey { flex: none; width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center;
  font-weight: 800; background: rgba(10,132,255,.12); color: var(--primary-deep); }
.opttext { flex: 1; }
.mark { font-weight: 800; color: #1E8E3E; }
.mark.wrong { color: var(--error); }
.option.correct { background: rgba(52,199,89,.16); border-color: rgba(52,199,89,.55); }
.option.correct .optkey { background: #34C759; color: #fff; }
.option.wrong { background: rgba(255,69,58,.13); border-color: rgba(255,69,58,.5); }
.option.wrong .optkey { background: var(--error); color: #fff; }

.explain { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-top: 20px; padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,.8); font-size: 14px; }
.explain b { color: var(--primary-deep); }
.ok { color: #1E8E3E; font-weight: 700; }
.no { color: var(--error); font-weight: 700; }
.hint { color: var(--text-3); }

.qactions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }

@media(max-width: 620px){ .qcard { padding: 18px; } .qstem { font-size: 16px; } }
</style>
