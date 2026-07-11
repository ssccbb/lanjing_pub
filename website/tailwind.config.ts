import type { Config } from 'tailwindcss'

export default <Config>{
  theme: {
    extend: {
      colors: {
        // 背景色
        'app-bg': '#141414',
        'app-bg-secondary': '#1a1a1a',
        'app-bg-tertiary': '#333333',
        'app-bg-hover': '#2a2a2a',

        // 主题色（蓝色）
        'app-primary': 'rgb(229, 37, 235)',
        'app-primary-hover': 'hsl(297, 76%, 48%)',
        'app-primary-light': 'hsl(291, 94%, 68%)',
        'app-primary-lighter': 'rgba(235, 37, 182, 0.2)',

        // 滚动条
        'app-scrollbar': '#404040',
        'app-scrollbar-hover': '#525252',

        // 保留原有的black配置
        black: '#141414'
      }
    }
  }
}