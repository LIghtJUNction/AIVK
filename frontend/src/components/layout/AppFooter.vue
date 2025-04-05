<template>
  <footer class="app-footer">
    <div class="footer-content">
      <span class="copyright">© {{ currentYear }} AIVK Team. 保留所有权利。</span>
      
      <div class="footer-links">
        <a href="#" class="footer-link">隐私政策</a>
        <a href="#" class="footer-link">使用条款</a>
        <a href="#" class="footer-link">帮助中心</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

// 当前年份
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  border-top: 1px solid var(--border-color);
  padding: 15px 20px;
  background-color: var(--bg-secondary);
  font-size: 14px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.copyright {
  color: var(--text-secondary);
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-link {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-speed) ease;
}

.footer-link:hover {
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .footer-links {
    gap: 15px;
  }
}
</style>
