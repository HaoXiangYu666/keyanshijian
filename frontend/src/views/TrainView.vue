<template>
  <div class="quiz">
    <div class="quiz-head">
      <div>
        <h1>方证练习</h1>
        <p class="muted">看证候，选方剂。共 {{ questions.length }} 题，选完立即出结果。</p>
      </div>
      <div class="progress-pill">{{ answeredCount }} / {{ questions.length }}</div>
    </div>

    <div v-if="loading" class="card">
      <p class="muted">正在准备题目…</p>
    </div>

    <div v-else-if="!questions.length" class="card">
      <p class="muted">题库暂时为空，请确认后端已启动并导入数据。</p>
      <button class="btn primary sm" style="margin-top:12px" @click="load">重试</button>
    </div>

    <template v-else>
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
          <span class="qno">第 {{ current + 1 }} 题</span>
          <span class="chip">{{ questions[current].bookTitle || '中医方证' }}</span>
        </div>

        <p class="qlabel">下列证候，最宜选用哪首方剂？</p>
        <p class="qstem">{{ questions[current].syndrome }}</p>

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
        </div>
      </section>

      <div class="qactions">
        <button class="btn ghost" :disabled="current === 0" @click="current--">上一题</button>
        <button class="btn ghost" :disabled="current >= questions.length - 1" @click="current++">下一题</button>
        <button class="btn primary" @click="reset">重新练习</button>
      </div>

      <div v-if="answeredCount === questions.length" class="card result">
        <h3>练习完成</h3>
        <p>答对 <b>{{ correctCount }}</b> / {{ questions.length }} 题，正确率 {{ Math.round(correctCount / questions.length * 100) }}%</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { search } from '@/api/search'

interface Question {
  id: string
  syndrome: string
  answer: string
  options: string[]
  bookTitle?: string
}

const questions = ref<Question[]>([])
const loading = ref(true)
const current = ref(0)
const answers = reactive<Record<string, string>>({})

const answeredCount = computed(() => Object.keys(answers).length)
const correctCount = computed(() => questions.value.filter(q => answers[q.id] === q.answer).length)

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function cleanText(s: string): string {
  return s.replace(/\s+/g, ' ').replace(/[【】\[\]《》]/g, '').trim()
}

/** 题库来自真实方剂数据：搜常见关键字取方剂，用 meta.syndrome 作题干、方名作答案 */
async function load() {
  loading.value = true
  try {
    const keywords = ['麻黄', '桂枝', '伤寒', '温病', '汤', '证治']
    const results = await Promise.all(
      keywords.map(k => search(k, { size: 40 }).catch(() => ({ list: [] })))
    )
    const pool = new Map<string, { name: string; syndrome: string; bookTitle?: string }>()
    for (const res of results) {
      for (const h of res.list || []) {
        if (h.refType !== 'formula' || !h.title) continue
        const syn = cleanText(String(h.meta?.syndrome || ''))
        if (syn.length < 8 || syn.length > 140) continue
        if (!pool.has(h.title)) {
          pool.set(h.title, { name: h.title, syndrome: syn, bookTitle: h.bookTitle })
        }
      }
    }
    const all = [...pool.values()]
    const names = all.map(x => x.name)
    const picked = shuffle(all).slice(0, 10)
    questions.value = picked.map((item, idx) => {
      const distractors = shuffle(names.filter(n => n !== item.name)).slice(0, 3)
      return {
        id: `q_${idx}`,
        syndrome: item.syndrome,
        answer: item.name,
        options: shuffle([item.name, ...distractors]),
        bookTitle: item.bookTitle
      }
    })
  } finally {
    loading.value = false
  }
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
  for (const k of Object.keys(answers)) delete answers[k]
  current.value = 0
  questions.value = shuffle(questions.value).map(q => ({
    ...q,
    options: shuffle(q.options)
  }))
}

onMounted(load)
</script>

<style scoped>
.quiz { max-width: 860px; margin: 0 auto; }
.quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
.quiz-head h1 { margin: 0 0 4px; font-size: 26px; color: var(--primary-deep); }
.quiz-head p { margin: 0; }
.progress-pill { padding: 8px 18px; border-radius: 999px; font-weight: 700; color: var(--primary-deep);
  background: rgba(255,255,255,.7); border: 1px solid rgba(255,255,255,.9); }

.question-nav { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.qdot { width: 36px; height: 36px; border-radius: 12px; font-size: 13px; font-weight: 700; cursor: pointer;
  background: rgba(255,255,255,.55); border: 1px solid rgba(255,255,255,.8); color: var(--text-2); transition: .15s; }
.qdot.done { background: rgba(10,132,255,.16); color: var(--primary-deep); }
.qdot.right { background: var(--primary); color: #fff; border-color: var(--primary); }
.qdot.cur { outline: 2px solid var(--primary); outline-offset: 2px; }

.qcard { padding: 28px; }
.qmeta { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.qno { font-weight: 700; color: var(--primary-deep); }
.qlabel { font-size: 13px; color: var(--text-2); margin-bottom: 8px; }
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

.qactions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
.result { margin-top: 20px; text-align: center; }
.result h3 { color: var(--primary-deep); margin-bottom: 6px; }

@media(max-width: 620px){ .qcard { padding: 18px; } .qstem { font-size: 16px; } }
</style>
