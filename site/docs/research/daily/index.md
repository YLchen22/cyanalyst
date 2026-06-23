---
title: 每日简报
sidebar: true
outline: false
---

<script setup>
import { ref, computed } from 'vue'

// 模拟简报数据 — 实际由 Python 脚本自动生成
const reports = ref([
  {
    date: '2026-06-23',
    title: '盘前简报：政策利好持续发酵，科技板块领涨预期升温',
    type: 'morning',
    tags: ['科技', '政策', '资金面'],
    size: '245 KB',
    url: '/research/daily/2026-06-23-morning.docx'
  },
  {
    date: '2026-06-22',
    title: '盘后复盘：两市缩量调整，北向资金逆势加仓新能源',
    type: 'evening',
    tags: ['新能源', '北向资金', '缩量'],
    size: '312 KB',
    url: '/research/daily/2026-06-22-evening.docx'
  },
  {
    date: '2026-06-22',
    title: '盘前简报：隔夜美股反弹，A 股高开预期',
    type: 'morning',
    tags: ['美股', '技术面', '高开'],
    size: '198 KB',
    url: '/research/daily/2026-06-22-morning.docx'
  }
])

const typeLabel = (t) => t === 'morning' ? '盘前' : '盘后'
const typeClass = (t) => t === 'morning' ? 'up' : 'down'
</script>

# 📊 每日简报

<div class="data-panel">
  <h3>📬 简报说明</h3>
  <p style="margin:0;color:var(--vp-c-text-2);">
    每个交易日自动生成 <strong>盘前简报</strong>（9:00）和 <strong>盘后复盘</strong>（15:30），
    覆盖市场概况、资金流向、技术面分析、重点标的跟踪等核心内容。
    点击下方条目可直接下载 <code>.docx</code> 或 <code>.pdf</code> 格式的完整报告。
  </p>
</div>

## 最新简报

<div class="report-list">
  <a v-for="r in reports" :key="r.date + r.type" class="report-item" :href="r.url" target="_blank">
    <div class="report-date">
      <span class="day">{{ r.date.split('-')[2] }}</span>
      <span>{{ r.date.split('-')[1] }}月</span>
    </div>
    <div class="report-info">
      <h4>
        <span :class="typeClass(r.type)">{{ typeLabel(r.type) }}</span>
        {{ r.title }}
      </h4>
      <div class="meta">
        <span>📅 {{ r.date }}</span>
        <span>📄 {{ r.size }}</span>
        <span v-for="t in r.tags" :key="t" class="report-tag daily">{{ t }}</span>
      </div>
    </div>
  </a>
</div>

::: info 提示
简报文件托管在 **Cloudflare R2** 对象存储上。如需查看历史简报，请访问 [历史归档](/research/daily/archive)。
:::
