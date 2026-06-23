---
title: 周度研报
sidebar: true
---

<script setup>
import { ref } from 'vue'

const reports = ref([
  {
    date: '2026-06-22',
    title: '第26周市场回顾：震荡分化加剧，关注中报预期',
    summary: '本周A股延续震荡格局，上证指数周跌0.8%，创业板指周涨1.2%。板块分化明显，新能源、半导体板块资金持续流入，传统消费板块承压。',
    tags: ['周报', '资金流向', '板块轮动'],
    size: '1.2 MB',
  },
  {
    date: '2026-06-15',
    title: '第25周市场回顾：政策窗口期临近，市场情绪回暖',
    summary: '政策预期升温推动市场反弹，两市成交额日均重返万亿。北向资金本周净流入超200亿元，为近3个月最大周度净流入。',
    tags: ['周报', '政策', '北向资金'],
    size: '1.1 MB',
  }
])
</script>

# 📈 周度研报

<div class="data-panel">
  <h3>📋 周报说明</h3>
  <p style="margin:0;color:var(--vp-c-text-2);">
    每周日发布，涵盖本周市场回顾、资金流向全景、板块轮动分析、技术面研判、
    下周关键事件日历及策略展望。适合用于中长期投资决策参考。
  </p>
</div>

## 最新周报

<div class="report-list">
  <div v-for="r in reports" :key="r.date" class="report-item">
    <div class="report-date">
      <span class="day">{{ r.date.split('-')[2] }}</span>
      <span>{{ r.date.split('-')[1] }}月</span>
    </div>
    <div class="report-info">
      <h4>{{ r.title }}</h4>
      <p style="margin:0.25rem 0;font-size:0.85rem;color:var(--vp-c-text-2);">{{ r.summary }}</p>
      <div class="meta">
        <span>📅 {{ r.date }}</span>
        <span>📄 {{ r.size }}</span>
        <span v-for="t in r.tags" :key="t" class="report-tag weekly">{{ t }}</span>
      </div>
    </div>
  </div>
</div>

::: info 查看历史
更多历史周报请访问 [历史归档](/research/weekly/archive)。
:::
