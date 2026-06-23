---
title: 专题分析
sidebar: true
---

<script setup>
import { ref } from 'vue'

const reports = ref([
  {
    date: '2026-06-20',
    title: '半导体产业链全景分析：国产替代进程加速',
    summary: '深度梳理半导体设计、制造、封测全产业链，分析国产替代在各环节的进展与瓶颈，梳理核心标的。',
    tags: ['半导体', '国产替代', '产业链'],
    size: '3.5 MB',
  },
  {
    date: '2026-06-10',
    title: '中报前瞻：哪些行业有望超预期？',
    summary: '基于Q1财报和Q2高频数据，筛选中报业绩可能超预期的行业与个股，提前布局中报行情。',
    tags: ['中报', '业绩预增', '选股'],
    size: '2.8 MB',
  }
])
</script>

# 🎯 专题分析

<div class="data-panel">
  <h3>🔬 专题说明</h3>
  <p style="margin:0;color:var(--vp-c-text-2);">
    不定期发布的深度研究报告，聚焦产业链分析、事件驱动、投资策略等主题。
    每篇专题报告力求深度与广度兼顾，提供独特的分析视角。
  </p>
</div>

## 最新专题

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
        <span v-for="t in r.tags" :key="t" class="report-tag special">{{ t }}</span>
      </div>
    </div>
  </div>
</div>

::: tip 专题选题
专题由周报中的关键发现触发，自动提取最具分析价值的主题进行深入研究。
也欢迎通过 GitHub Issues 提交你想研究的专题方向。
:::
