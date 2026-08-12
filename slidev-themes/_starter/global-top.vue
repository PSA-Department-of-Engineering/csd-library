<!-- Persistent chrome: wordmark, section + page header, legal footer. Registered by
     Slidev automatically because of the filename. It hides the wordmark and header on
     any slide whose frontmatter `class` contains `k-cover`, so covers and section
     dividers stay clean; the footer stays on every slide.

     Set the two constants below and nothing else needs editing. -->
<template>
  <div>
    <div v-if="!isCover" class="cf-mark">{{ WORDMARK }}</div>
    <div v-if="!isCover" class="cf-head">
      <div class="cf-head-section">{{ section }}</div>
      <div class="cf-head-num">{{ page }}</div>
    </div>
    <div class="cf-legal">{{ LEGAL }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNav } from '@slidev/client'

const WORDMARK = 'BRAND'
const LEGAL = 'BRAND © 2026 – ALL RIGHTS RESERVED · CLASSIFICATION: CONFIDENTIAL'

const nav = useNav()

// `section:` is per-page frontmatter; the header reads it rather than the theme
// hard-coding a running title.
const frontmatter = computed(() => nav.currentSlideRoute.value?.meta?.slide?.frontmatter ?? {})
const isCover = computed(() => String(frontmatter.value.class ?? '').includes('k-cover'))
const section = computed(() => frontmatter.value.section ?? '')
const page = computed(() => nav.currentPage.value)
</script>
