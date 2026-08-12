<!-- Persistent chrome for this theme: wordmark, running header (section, deck name, page
     number), legal footer. Slidev registers it by filename. It hides the wordmark and
     header on any slide whose frontmatter `class` contains `k-cover`, so the cover and
     the close stay clean; the legal line stays on every slide.

     This theme's header carries a deck-name slot (cf-head-deck) that the dark showcase
     does not - the pale stage gives the header room for it. The classes emitted here are
     the ones meta.json declares as chrome, and check-themes.mjs holds the two in step.
     Set the constants below; nothing else here needs editing. -->
<template>
  <div>
    <div v-if="!isCover" class="cf-mark">{{ WORDMARK }}</div>
    <div v-if="!isCover" class="cf-head">
      <div class="cf-head-section">{{ section }}</div>
      <div class="cf-head-deck">{{ DECK }}</div>
      <div class="cf-head-num">{{ page }}</div>
    </div>
    <div class="cf-legal">{{ LEGAL }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNav } from '@slidev/client'

const WORDMARK = 'BRAND'
const DECK = 'Deck title'
const LEGAL = 'BRAND © 2026 – ALL RIGHTS RESERVED · CLASSIFICATION: CONFIDENTIAL'

const nav = useNav()

// `section:` is per-page frontmatter, so the running header reads the page rather than
// the theme hard-coding a title.
const frontmatter = computed(() => nav.currentSlideRoute.value?.meta?.slide?.frontmatter ?? {})
const isCover = computed(() => String(frontmatter.value.class ?? '').includes('k-cover'))
const section = computed(() => frontmatter.value.section ?? '')
const page = computed(() => nav.currentPage.value)
</script>
