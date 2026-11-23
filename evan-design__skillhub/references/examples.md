# WorkBuddy 视觉规范 · 完整可运行示例

本文件提供**可直接复制改造**的成品界面片段，弥补「规则齐全但缺示例」的短板。所有示例均引用 `assets/tokens.css` 的语义变量、颜色采用 v1.1.0 修正后的达标值、并内建无障碍。复制时只需引入 tokens.css，无需改动色值。

> 通用前置：每个示例前先 `<link rel="stylesheet" href="tokens.css">`（或把变量并入你的样式入口）。

---

## 示例 1 · 按钮组（主/次/危险 + 状态无障碍）

演示：主按钮实心、次按钮描边、危险按钮用朱砂且**附图标 + 文字**三重编码、全部引用 Token、焦点环可见。

```html
<div class="demo-row">
  <button class="czl-btn czl-btn--primary">导出报表</button>
  <button class="czl-btn czl-btn--secondary">取消</button>
  <button class="czl-btn czl-btn--danger">
    <svg class="czl-icon" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      <path d="M4 4 L12 12 M12 4 L4 12" stroke="currentColor" fill="none"/>
    </svg>
    删除
  </button>
</div>
```

```css
.demo-row { display: flex; gap: var(--space-2); flex-wrap: wrap; }

.czl-btn {
  min-height: var(--touch-target-min);           /* 44px 触摸目标 */
  padding: var(--space-2) var(--space-4);          /* 8×21 */
  border-radius: var(--radius-card);              /* 10px */
  font-family: var(--font-family-zh-body);
  font-size: var(--font-size-body);               /* 16px */
  cursor: pointer;
  transition: opacity var(--duration-micro) ease-out;
}
.czl-btn--primary {
  background: var(--color-accent);               /* 靛青，白字 8.57:1 */
  color: var(--color-bg-base);
  border: 1px solid var(--color-accent);
}
.czl-btn--secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-subtle);
}
.czl-btn--danger {
  background: transparent;
  color: var(--color-danger);                    /* 朱砂 5.67:1 */
  border: 1px solid var(--color-danger);
  display: inline-flex; align-items: center; gap: var(--space-2);
}
.czl-btn:focus-visible {                          /* 焦点环，tokens.css 已内建 */
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}
```

**校验点**：触摸目标 ≥44px ✓ · 危险态「颜色+✕图标+文字」三重编码 ✓ · 焦点环可见 ✓ · 无硬编码色值 ✓。

---

## 示例 2 · 状态提示卡（成功/警告/危险，不依赖单一颜色）

演示 v1.1.0 新增的**冗余编码**规则：每种状态都有独立图标、状态文字与无障碍文本。

```html
<div class="czl-notice czl-notice--success" role="status">
  <span class="czl-notice__icon" aria-hidden="true">✓</span>
  <span>保存成功</span>
</div>
<div class="czl-notice czl-notice--warning" role="status">
  <span class="czl-notice__icon" aria-hidden="true">!</span>
  <span>配置即将过期</span>
</div>
<div class="czl-notice czl-notice--danger" role="alert">
  <span class="czl-notice__icon" aria-hidden="true">✕</span>
  <span>校验失败，请检查输入</span>
</div>
```

```css
.czl-notice {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-card);
  background: var(--color-bg-surface);
  box-shadow: var(--shadow-soft);               /* ≥3 层柔和阴影（气）*/
  margin-block-end: var(--space-3);
  font-size: var(--font-size-body);
  line-height: var(--line-height-body);
}
.czl-notice__icon {
  display: inline-grid; place-items: center;
  width: var(--icon-size-md); height: var(--icon-size-md); /* 21px 三档之一 */
  border-radius: 50%; color: #FAF8F3; font-weight: 700;
  flex: 0 0 auto;
}
.czl-notice--success { color: var(--color-text-primary); }
.czl-notice--success .czl-notice__icon { background: var(--color-success); } /* 苔绿 5.44:1 底+白字 */
.czl-notice--warning .czl-notice__icon { background: var(--color-warning); } /* 深藤黄 4.64:1 */
.czl-notice--danger  .czl-notice__icon { background: var(--color-danger); }  /* 朱砂 5.67:1 */
```

> 提示：图标底色上的白字对比见 design-system 4.5 节；深藤黄/朱砂/苔绿对白字均 ≥4.5:1。若换成原藤黄 #D4A017，白字仅约 2.5:1，不达标——这正是 v1.1.0 调暗它的原因。

---

## 示例 3 · 数据卡片（间/气/并 + 破格点缀）

演示：留白、多层阴影、斐波那契间距、以及**唯一一处**破格（`--accent-ha`），其余元素 100% 守规。

```html
<article class="czl-card">
  <p class="czl-card__label">跳出率</p>
  <p class="czl-card__value">38.2%</p>
  <p class="czl-card__delta czl-ha-accent">↑ 2.4%</p>  <!-- 全屏唯一破格 -->
  <p class="czl-card__note">较上周同期</p>
</article>
```

```css
.czl-card {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-container);         /* 12px */
  box-shadow: var(--shadow-soft);                 /* 3 层柔和阴影（气）*/
  padding: var(--space-5);                        /* 34px 呼吸边距（间）*/
  inline-size: 21rem;
}
.czl-card__label {
  font-family: var(--font-family-zh-body);
  font-size: var(--font-size-caption); color: var(--color-text-secondary); /* 淡墨 6.5:1 */
  margin: 0 0 var(--space-2);
}
.czl-card__value {
  font-family: var(--font-family-zh-title);
  font-size: var(--font-size-h1); line-height: var(--line-height-h1);
  color: var(--color-text-primary); margin: 0;
}
.czl-card__delta {                                 /* 破格：朱砂点缀，5.67:1 达标 */
  font-size: var(--font-size-h3);
  margin: var(--space-2) 0 0;
}
.czl-card__note { font-size: var(--font-size-caption); color: var(--color-text-secondary); margin: var(--space-3) 0 0; }
```

**校验点**：唯一破格（其余 100% 守规）✓ · 破格色朱砂对宣纸白 5.67:1 ✓ · 3 层阴影 ✓ · 呼吸边距 ≥21px ✓。若整屏还有第二处高饱和/超规元素，即为「破格泛滥」反模式，须删除。

---

## 示例 4 · 表单与校验（焦点、标签、错误态）

演示：标签关联、可见焦点环、错误态「颜色+图标+文字」、触摸目标。

```html
<form class="czl-form" novalidate>
  <label class="czl-field">
    <span class="czl-field__label">邮箱</span>
    <input class="czl-field__input" type="email" aria-invalid="true"
           aria-describedby="email-err" value="bad@">
    <span class="czl-field__error" id="email-err" role="alert">
      <span aria-hidden="true">✕</span> 邮箱格式不正确
    </span>
  </label>
</form>
```

```css
.czl-field { display: block; margin-block-end: var(--space-5); }
.czl-field__label { display: block; font-size: var(--font-size-body); margin-block-end: var(--space-2); }
.czl-field__input {
  min-height: var(--touch-target-min);
  inline-size: 100%;
  padding: var(--space-2) var(--space-3);
  border: none; border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-surface);
  font-size: var(--font-size-body); color: var(--color-text-primary);
  border-radius: var(--radius-input) var(--radius-input) 0 0;
}
.czl-field__input:focus-visible {                  /* 聚焦靛青线，不禁用 outline */
  outline: 2px solid var(--color-focus-ring); outline-offset: 2px;
  border-bottom-color: var(--color-accent);
}
.czl-field__error {
  display: flex; align-items: center; gap: var(--space-2);
  margin-block-start: var(--space-2);
  font-size: var(--font-size-caption);
  color: var(--color-danger);                     /* 朱砂 + ✕ + 文字 */
}
```

---

## 示例 5 · 冬季节主题的正确用法（浅色不承文字）

演示评测指出的「浅季节色不协调」如何修正：月白只作背景，文字用深青灰。

```html
<section data-season="winter" class="winter-hero">
  <h2>冬 · 藏</h2>
  <p>万物收藏，静待春生。</p>
</section>
```

```css
.winter-hero {
  background: var(--season-winter-bg);            /* 月白 #C9D2D3 仅作背景 */
  color: var(--color-accent);                     /* 冬季 accent 已设为深青灰 #5E7075，4.88:1 */
  padding: var(--space-7);
  border-radius: var(--radius-container);
}
/* 错误做法：color: #C9D2D3 写在浅底上（1.45:1，不可读）——严禁 */
```

---

## 示例 6 · 完整仪表盘首屏（综合）

组合以上全部规则的最小完整页：单主 CTA（秘）、61.8:38.2 版心（并）、斐波那契间距（间）、状态冗余编码、唯一破格。

```html
<!doctype html>
<html lang="zh-CN" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>数据概览</title>
  <link rel="stylesheet" href="tokens.css">
  <style>
    body { margin: 0; background: var(--color-bg-base);
           color: var(--color-text-primary);
           font-family: var(--font-family-zh-body); }
    .page { display: grid; grid-template-columns: 61.8fr 38.2fr;
            gap: var(--grid-gap); max-width: var(--container-max);
            margin: 0 auto; padding: var(--page-margin); }
    .hero { padding-block: var(--space-6); }
    .hero h1 { font-family: var(--font-family-zh-title);
               font-size: var(--font-size-h1); margin: 0 0 var(--space-4); }
    .hero p  { color: var(--color-text-secondary); max-inline-size: var(--reading-width); }
    .cards { display: grid; gap: var(--space-4); }
    @media (max-width: 768px) { .page { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>数据概览</h1>
      <p>以留白承载信息，用节奏引导视线。</p>
      <button class="czl-btn czl-btn--primary">导出报表</button> <!-- 首屏唯一主 CTA -->
    </section>
    <aside class="cards">
      <!-- 复用示例 3 的 .czl-card；全屏仅一处 .czl-ha-accent -->
    </aside>
  </main>
</body>
</html>
```

**交付前自检**：对照 SKILL.md 第四节速查表 + 八意识联检 + 第六节无障碍，逐项打勾后再交付。
