<template>
  <footer class="py-6 text-center text-xs text-gray-500">
    <p>© 2026 {{ appName }} 版权所有</p>
  </footer>
</template>

<script setup>
const appName = useBrandName()
</script>
