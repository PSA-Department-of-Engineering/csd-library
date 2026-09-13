<template><div class="ds-ambient" aria-hidden="true"><div class="ds-glow"></div><svg class="ds-stream" viewBox="0 0 980 552" preserveAspectRatio="xMidYMid slice"><path d="M 720 -90 C 450 70 970 190 710 335 S 560 540 860 680"/><path d="M 731 -90 C 458 70 976 190 722 335 S 570 540 868 680"/><path d="M 742 -90 C 466 70 982 190 734 335 S 580 540 876 680"/><path d="M 753 -90 C 474 70 988 190 746 335 S 590 540 884 680"/><path d="M 764 -90 C 482 70 994 190 758 335 S 600 540 892 680"/><path d="M 775 -90 C 490 70 1000 190 770 335 S 610 540 900 680"/><path d="M 786 -90 C 498 70 1006 190 782 335 S 620 540 908 680"/><path d="M 797 -90 C 506 70 1012 190 794 335 S 630 540 916 680"/><path d="M 808 -90 C 514 70 1018 190 806 335 S 640 540 924 680"/></svg><div class="ds-embers"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></div><div class="ds-brand"><span class="ds-wordmark">psa<span class="ds-dot">.</span></span></div></template>
<script setup>
import { onMounted, onUnmounted } from 'vue'
const syncVisibility = () => { document.documentElement.dataset.dsHidden = String(document.hidden) }
onMounted(() => { syncVisibility(); document.addEventListener('visibilitychange', syncVisibility) })
onUnmounted(() => document.removeEventListener('visibilitychange', syncVisibility))
</script>
