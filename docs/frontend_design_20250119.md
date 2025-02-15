# WriteWorld 前端设计文档

## 1. 设计原则

基于 RICH（Relevant实用、Immediate即时、Comfortable舒适、Humanistic人性化）设计范式，我们的设计需要：
- 实用：功能直观，操作简单
- 即时：实时反馈，流畅交互
- 舒适：视觉优雅，体验流畅
- 人性化：符合用户心智，关注细节

## 2. 页面布局

### 2.1 翻译页面布局
```
+------------------------------------------+
|                Header                     |
|  [Logo] [登录/注册] [Language Switcher]   |
+------------------------------------------+
|              Intro Banner                 |
| "体验优雅的跨语言文学表达"                  |
+------------------------------------------+
|            Translation Area              |
| +------------------+------------------+  |
| |   Source Text    |   Target Text    |  |
| |   [TextArea]     |   [TextArea]     |  |
| |                  |                  |  |
| | Lang: [Select]   | Lang: [Select]   |  |
| +------------------+------------------+  |
|                                         |
|         [Translate Button]              |
+------------------------------------------+
|           Translation Process            |
| +------------------------------------+  |
| |     Translation Steps Display      |  |
| | 1. Initial Translation            |  |
| | 2. Literary Enhancement           |  |
| | 3. Cultural Adaptation            |  |
| +------------------------------------+  |
+------------------------------------------+
|           Example Showcase              |
| [优美的翻译案例展示，突出诗意性]           |
+------------------------------------------+

## 3. 交互设计

### 3.1 输入区域
- 支持长文本输入
- 字数统计
- 自动语言检测
- 优雅的占位文本（如古诗、名句）

### 3.2 翻译过程
- 实时展示翻译的思考过程
- 优雅的加载动画（如水墨效果）
- 展示不同翻译版本的对比
- 突出显示关键词和意境

### 3.3 结果展示
- 分步骤展示翻译过程
- 提供多个可能的翻译版本
- 支持朗读功能
- 提供文化背景注释

## 4. 视觉设计

### 4.1 配色方案
```css
:root {
  /* 主色调：水墨风 */
  --primary-color: #363945;  /* 墨色 */
  --secondary-color: #8B9DAF; /* 淡墨 */
  --accent-color: #E6B422;   /* 金色点缀 */

  /* 背景色 */
  --bg-primary: #FAFAFA;     /* 宣纸色 */
  --bg-secondary: #F5F5F5;   /* 浅灰 */

  /* 文字颜色 */
  --text-primary: #333333;
  --text-secondary: #666666;
}
```

### 4.2 字体选择
```css
/* 中文 */
--font-cn: 'Noto Serif SC', serif;
/* 英文 */
--font-en: 'Crimson Pro', serif;
```

## 5. 组件设计

### 5.1 TranslationInput
```typescript
interface TranslationInput {
  value: string;
  language: string;
  placeholder: string;
  onChange: (value: string) => void;
  onLanguageChange: (lang: string) => void;
}
```

### 5.2 TranslationProcess
```typescript
interface TranslationStep {
  type: 'init' | 'enhance' | 'cultural';
  content: string;
  timestamp: number;
}

interface TranslationProcess {
  steps: TranslationStep[];
  currentStep: number;
  isLoading: boolean;
}
```

### 5.3 TranslationResult
```typescript
interface TranslationResult {
  originalText: string;
  translatedText: string;
  culturalNotes?: string[];
  alternatives?: string[];
}
```

## 6. 动画效果
- 翻译过程使用优雅的过渡动画
- 加载状态使用水墨晕开效果
- 结果展示使用渐显效果

## 7. 技术栈
- Next.js
- TypeScript
- Ant Design
- Tailwind CSS
- Framer Motion (动画)
