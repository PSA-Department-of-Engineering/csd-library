<!-- Persistent chrome for this theme. Richer than the other Celfocus themes: the corporate
     template carries a logo lockup and a two-line header (section over deck name) beside
     the page number, which is what cf-logo / cf-head-titles / cf-head-deck exist for.

     The lockup is BRAND PAYLOAD the catalog does not carry - meta.json declares it under
     requires.assets, and the deck supplies it at public/celfocus-lockup.png. Without it
     the header renders with a broken image, which is the honest failure: the theme says
     out loud what it needs rather than silently dropping the mark.

     Hides the wordmark and header on any slide whose frontmatter `class` contains
     `k-cover`. The classes emitted here are the ones meta.json declares as chrome, and
     check-themes.mjs holds the two in step. -->
<template>
  <div>
    <div v-if="!isCover" class="cf-mark">{{ WORDMARK }}</div>
    <div v-if="!isCover" class="cf-head">
      <img class="cf-logo" src="/celfocus-lockup.png" :alt="WORDMARK" />
      <div class="cf-head-titles">
        <div class="cf-head-section">{{ section }}</div>
        <div class="cf-head-deck">{{ DECK }}</div>
      </div>
      <div class="cf-head-num">{{ page }}</div>
    </div>
    <div class="cf-legal">{{ LEGAL }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNav } from '@slidev/client'

const WORDMARK = 'CELFOCUS'
const DECK = 'Deck title'
const LEGAL = 'CELFOCUS © 2026 – ALL RIGHTS RESERVED · CLASSIFICATION: CONFIDENTIAL'

const nav = useNav()

const frontmatter = computed(() => nav.currentSlideRoute.value?.meta?.slide?.frontmatter ?? {})
const isCover = computed(() => String(frontmatter.value.class ?? '').includes('k-cover'))
const section = computed(() => frontmatter.value.section ?? '')
const page = computed(() => nav.currentPage.value)
</script>
