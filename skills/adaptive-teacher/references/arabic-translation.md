# Egyptian Arabic Translation Guide

> اللغة هنا عامية مصرية — مش فصحى. نفس اللغة اللي الناس بتتكلم بيها في الشارع.

Complete reference for translating technical content from English to Egyptian Arabic (العامية المصرية). This guide is for AI agents who need to teach, explain, or communicate technical concepts in Egyptian colloquial Arabic.

## Table of Contents

1. [Why Egyptian Arabic Is Different](#why-egyptian-arabic-is-different)
2. [The Golden Rules](#the-golden-rules)
3. [Technical Term Handling](#technical-term-handling)
4. [Sentence Structure Patterns](#sentence-structure-patterns)
5. [Common Phrases & Expressions](#common-phrases--expressions)
6. [Tone & Cultural Notes](#tone--cultural-notes)
7. [RTL Layout Rules](#rtl-layout-rules)
8. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
9. [Example Translations](#example-translations)

---

## Why Egyptian Arabic Is Different

**Egyptian Arabic (العامية المصرية) is NOT Modern Standard Arabic (الفصحى).** They are as different as British English and Jamaican Patois — same family, different enough that using the wrong one sounds robotic and unnatural.

| Aspect             | MSA (فصحى)                     | Egyptian (عامية)                              |
| ------------------ | ------------------------------ | --------------------------------------------- |
| Usage              | News, formal writing, religion | Daily conversation, social media, casual text |
| Tone               | Formal, stiff, authoritative   | Warm, friendly, conversational                |
| Verb conjugation   | Complex, uses dual form        | Simplified, no dual form                      |
| Question formation | "هل" + verb                    | Verb + "؟" or tone change                     |
| Negation           | "لا" / "لم" / "ليس"            | "مـ...ـش" (circumfix wrapping the verb)       |
| "What"             | "ما" / "ماذا"                  | "إيه"                                         |
| "How"              | "كيف"                          | "إزاي"                                        |
| "Why"              | "لماذا"                        | "ليه"                                         |
| "Where"            | "أين"                          | "فين"                                         |
| "This"             | "هذا/هذه"                      | "ده/دي"                                       |
| "Want"             | "أريد"                         | "عايز/عاوز"                                   |

**The AI must ALWAYS use Egyptian Arabic, never MSA, when Arabic mode is activated.** MSA in a casual teaching context sounds like a medieval knight explaining JavaScript — technically Arabic but absurdly out of place.

---

## The Golden Rules

### Rule 1: Technical Terms Stay in English

**NEVER translate programming/technical terms into Arabic.** No Egyptian developer says "واجهة البرمجة" when they mean API. They say "الـ API" — with the Arabic definite article "الـ" prefixed to the English term.

**✅ Correct:**

- "الـ API بيرجّع JSON"
- "اعمل push على الـ branch ده"
- "الـ server مش بيستجيب"
- "الـ function دي بتاخد parameter واحد"
- "لازم تعمل install للـ package ده"

**❌ Wrong:**

- "واجهة البرمجة بتعيد ترميز كائن جافاسكريبت"
- "ارسل التعديلات على الفرع"
- "الخادم لا يستجيب"
- "الدالة دي بتاخد معامل واحد"

**Why:** Egyptian developers and tech-adjacent people use English technical terms in Arabic sentences. This is natural code-switching, not laziness. Translating these terms creates cognitive load because the learner has to mentally translate BACK to the English term they'll actually use.

### Rule 2: Everyday Words Go Arabic

Non-technical words, metaphors, and explanations should be in Egyptian Arabic:

- "يعني" (it means / basically)
- "مثلاً" (for example)
- "تخيل إنك..." (imagine you're...)
- "اللي بيحصل هو..." (what happens is...)
- "ببساطة" (simply)

### Rule 3: Egyptian Pronunciation Spelling

Use Egyptian pronunciation, not MSA spelling, when writing colloquially:

| MSA Spelling | Egyptian Spelling | Meaning          |
| ------------ | ----------------- | ---------------- |
| ذلك          | ده / كده          | that / like that |
| ماذا         | إيه               | what             |
| لماذا        | ليه               | why              |
| كيف          | إزاي              | how              |
| الآن         | دلوقتي            | now              |
| جيد          | كويس / تمام       | good / OK        |
| سوف          | هـ...             | will (prefix)    |
| نعم          | أيوه / آه         | yes              |
| يريد         | عايز / عاوز       | wants            |
| يذهب         | يروح              | goes             |
| يأتي         | ييجي              | comes            |
| يستطيع       | يقدر              | can              |
| يوجد         | فيه               | there is         |
| أيضاً        | كمان / برضو       | also             |
| جداً         | أوي / قوي         | very             |
| لكن          | بس                | but              |
| يعرف         | يعرف              | knows            |
| يفهم         | يفهم              | understands      |
| صعب          | صعب               | difficult        |
| سهل          | سهل               | easy             |

### Rule 4: The "الـ" Prefix for English Terms

When embedding English technical terms in Arabic sentences, use the Arabic definite article "الـ" (al-) when the term would be definite in English:

- "الـ API" (the API)
- "الـ server" (the server)
- "الـ function دي" (this function)
- "في الـ database" (in the database)

For indefinite terms, no prefix:

- "هنعمل function جديدة" (we'll make a new function)
- "ده بيرجّع array" (this returns an array)

### Rule 5: Natural Sentence Flow

Egyptian Arabic sentences follow a different rhythm than English. The verb often comes first, and particles like "بـ" (present continuous) are essential:

**English pattern:** Subject → Verb → Object
**Egyptian pattern:** (optional topic) → Verb-with-prefix → Object → (optional comment)

- English: "The server sends a response"
- Egyptian: "الـ server بيبعت response"

- English: "We need to add authentication"
- Egyptian: "لازم نضيف authentication"

- English: "This function doesn't work"
- Egyptian: "الـ function دي مش شغالة"

---

## Technical Term Handling

### Terms That ALWAYS Stay English

| Category               | Examples (never translate these)                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| Programming constructs | function, variable, class, object, array, string, boolean, loop, if/else, return, import, export |
| Web/API                | API, endpoint, request, response, GET, POST, PUT, DELETE, header, body, URL, route, middleware   |
| Data                   | JSON, XML, SQL, database, table, schema, query, index, key, value                                |
| Infrastructure         | server, client, host, port, container, Docker, deployment, CI/CD, pipeline                       |
| Git                    | commit, push, pull, branch, merge, clone, fork, PR, repo                                         |
| Tools/Frameworks       | React, Node.js, Python, TypeScript, Tailwind, Astro, Next.js, etc.                               |
| Architecture           | frontend, backend, fullstack, microservice, monolith, cache, queue, pub/sub                      |
| Dev concepts           | bug, debug, deploy, build, compile, runtime, error, exception, log, test                         |

### Terms That CAN Be in Arabic (everyday concepts)

| English            | Egyptian Arabic                       |
| ------------------ | ------------------------------------- |
| "folder/directory" | "فولدر" (borrowed) or "مكان" (place)  |
| "file"             | "فايل" (borrowed)                     |
| "button"           | "زرار" (Egyptian) or "button"         |
| "page"             | "صفحة" (Arabic) or "page"             |
| "user"             | "يوزر" (borrowed) or "المستخدم"       |
| "screen"           | "شاشة" (Arabic)                       |
| "click"            | "click" or "دوس" (Egyptian for press) |
| "download"         | "download" or "نزّل"                  |
| "upload"           | "upload" or "ارفع"                    |
| "website"          | "موقع" (Arabic) or "site"             |
| "application"      | "أبليكيشن" (borrowed) or "app"        |
| "password"         | "باسوورد" (borrowed) or "password"    |

### Transliteration Rules

When borrowing English words into Arabic script:

- Use the closest Egyptian pronunciation, not literal transliteration
- "server" → "سيرفر" (not "سرفر")
- "browser" → "براوزر"
- "framework" → "فريمورك"
- "middleware" → "ميدل وير"
- "authentication" → keep as "authentication" (too long to transliterate)
- "cache" → "كاش"

---

## Sentence Structure Patterns

### Pattern 1: Explaining What Something Does

**Template:** `الـ [term] ده/دي بـ[verb] [what it does]`

Examples:

- "الـ middleware ده بيتشيك على الـ token قبل ما يسمح بالـ request"
- "الـ function دي بتاخد الـ input وبترجّع array جديد"
- "الـ API endpoint ده بيجيب كل الـ users من الـ database"

### Pattern 2: Explaining Why

**Template:** `[thing] بـ[does X] عشان [reason]`

Examples:

- "بنستخدم caching عشان منضغطش على الـ server كل مرة"
- "الـ password بيتعمله hash عشان لو حد سرق الـ database ميقدرش يقرأ الـ passwords"
- "بنفصل الـ frontend عن الـ backend عشان كل حاجة تقدر تتطور لوحدها"

### Pattern 3: Metaphor Introduction

**Template:** `تخيل إن الـ [concept] زي [everyday thing]. [Explanation]. في الـ code بتاعنا، ده بيبقى [real thing].`

Examples:

- "تخيل إن الـ API زي ويتر في مطعم — أنت بتقوله عايز إيه، وهو بيروح يجيبهولك من المطبخ. في الـ code بتاعنا، الـ frontend هو أنت، والـ API هو الويتر، والـ backend هو المطبخ."
- "الـ cache ده زي لما تحفظ screenshot من حاجة على الموبايل عشان متفتحش الـ app كل شوية. بتستخدم الصورة المحفوظة لحد ما تحتاج الـ version الجديد."

### Pattern 4: Step-by-Step Instructions

**Template:** `أول حاجة [step 1]. بعد كده [step 2]. وبعدين [step 3].`

Examples:

- "أول حاجة اعمل clone للـ repo. بعد كده اعمل npm install. وبعدين شغّل npm run dev."
- "أول حاجة الـ user بيعمل login. بعد كده الـ server بيعمل token. وبعدين الـ token ده بيتبعت مع كل request."

### Pattern 5: "The Point Is..."

**Template:** `الفكرة إن [main point]. يعني [simplified restatement].`

Examples:

- "الفكرة إن الـ middleware بيقف في النص بين الـ request والـ response. يعني كل request بيعدي عليه الأول قبل ما يوصل للـ route handler."
- "الفكرة إن الـ state management بتخلي كل الـ components شايفة نفس الـ data. يعني لو حاجة اتغيرت في مكان، كل حتة تانية بتعرف."

---

## Common Phrases & Expressions

### Teaching Phrases

| English                      | Egyptian Arabic               |
| ---------------------------- | ----------------------------- |
| "Let me explain..."          | "خليني أشرحلك..."             |
| "In other words..."          | "يعني..." / "بمعنى تاني..."   |
| "For example..."             | "مثلاً..." / "زي مثلاً..."    |
| "Think of it like..."        | "تخيل إنها زي..."             |
| "The key idea is..."         | "الفكرة المهمة هنا إن..."     |
| "Makes sense?"               | "فاهم؟" / "واضح؟"             |
| "Good question!"             | "سؤال حلو!"                   |
| "You're on the right track"  | "أنت ماشي صح"                 |
| "Not quite — here's why"     | "مش بالظبط — والسبب إن..."    |
| "Exactly!"                   | "بالظبط!" / "أيوه كده!"       |
| "Before I explain..."        | "قبل ما أشرح..."              |
| "Let me ask you first..."    | "خليني أسألك الأول..."        |
| "What do you think?"         | "رأيك إيه؟" / "أنت شايف إيه؟" |
| "Take a guess"               | "خمّن" / "حاول تحزر"          |
| "Now you explain it to me"   | "دلوقتي أنت اشرحهالي"         |
| "Why do you think that?"     | "ليه شايف كده؟"               |
| "Don't worry about it"       | "متقلقش منها"                 |
| "This is the important part" | "هنا الحتة المهمة"            |
| "Let's break it down"        | "يلا نفصّصها مع بعض"          |
| "Step by step"               | "خطوة خطوة"                   |

### Encouragement Phrases

| English                                | Egyptian Arabic             |
| -------------------------------------- | --------------------------- |
| "Great answer!"                        | "إجابة ممتازة!"             |
| "You're getting it!"                   | "أنت بتفهم!"                |
| "That's the right intuition"           | "إحساسك صح"                 |
| "Most people miss this"                | "ناس كتير بتمر على دي"      |
| "You nailed it"                        | "ضربت الهدف!" / "جبتها!"    |
| "Now you're thinking like an engineer" | "دلوقتي بتفكر زي engineer!" |
| "Don't worry, this IS hard"            | "متقلقش، دي فعلاً صعبة"     |
| "Everyone gets confused here"          | "الكل بيتلخبط هنا"          |

### Correction Phrases (gentle)

| English                                | Egyptian Arabic                   |
| -------------------------------------- | --------------------------------- |
| "Not quite — close though"             | "مش بالظبط — بس قربت"             |
| "I see your logic, but..."             | "فاهم أنت فكّرت إزاي، بس..."      |
| "Good reasoning, wrong conclusion"     | "التفكير كويس، بس النتيجة مختلفة" |
| "Let me rephrase the question"         | "خليني أسأل بطريقة تانية"         |
| "Try thinking about it from [X] angle" | "جرّب تفكر فيها من ناحية [X]"     |

---

## Tone & Cultural Notes

### Warmth Is Default

Egyptian culture values warmth and humor in communication. Even formal teachers in Egypt use humor and friendly language. The teaching tone should feel like a knowledgeable older sibling or a friendly senior colleague — not a textbook.

### Humor Patterns

Egyptian humor often involves:

- **Exaggeration:** "الـ server ده هيفجر من كتر الـ requests" (the server will explode from all the requests)
- **Self-deprecation:** "أنا نفسي اتلخبطت أول مرة شفت ده" (I was confused too the first time I saw this)
- **Relatable comparisons:** "ده زي لما تلاقي رقم حد في الموبايل ومتفتكرش مين ده" (like finding a number in your phone and not remembering whose it is — explaining orphaned database records)

### Don't Over-Translate

When in doubt, use more English. Egyptian tech communication naturally mixes English and Arabic. A sentence that's 60% Arabic and 40% English is perfectly natural:

> "لما الـ user يعمل login، الـ server بيعمل JWT token ويبعته في الـ response header. الـ frontend بياخد الـ token ده ويحطه في localStorage عشان يبعته مع كل request تاني."

This is MORE natural than a fully Arabic version would be.

### Avoid MSA Red Flags

If you catch yourself writing any of these, you've slipped into MSA:

- "هل" (use rising intonation or add "؟" instead)
- "إنَّ" (use "إن" without the shadda)
- "سوف" (use "هـ" prefix: "هيعمل" not "سوف يعمل")
- "لكنَّ" (use "بس")
- "لأنَّ" (use "عشان")
- "ليس" (use "مش")
- "يجب" (use "لازم")
- Dual form ("مبرمجان") — Egyptian doesn't use dual, use plural: "اتنين مبرمجين"

---

## RTL Layout Rules

When generating HTML artifacts with Arabic content:

### Text Direction

```html
<!-- Arabic text containers -->
<div dir="rtl" lang="ar">
  <!-- Arabic content here -->
</div>

<!-- Code blocks ALWAYS stay LTR, even inside RTL containers -->
<div dir="rtl" lang="ar">
  <p>الـ function دي بتعمل كده:</p>
  <pre dir="ltr"><code>function hello() { return "world"; }</code></pre>
</div>
```

### CSS Considerations

```css
/* RTL text alignment */
[dir="rtl"] {
  text-align: right;
  direction: rtl;
}

/* Code blocks remain LTR */
[dir="rtl"] pre,
[dir="rtl"] code {
  direction: ltr;
  text-align: left;
}

/* Mixed content: English terms in Arabic text flow naturally */
[dir="rtl"] .english-term {
  direction: ltr;
  unicode-bidi: embed;
}
```

### Font Considerations

For Arabic text, use fonts that support Arabic well:

- **IBM Plex Arabic** — clean, modern, excellent for body text
- **Cairo** — geometric, works well for headings
- **Noto Sans Arabic** — universal fallback

```html
<link
  href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&display=swap"
  rel="stylesheet"
/>
```

```css
[dir="rtl"] {
  font-family: "IBM Plex Sans Arabic", "Cairo", sans-serif;
}
```

---

## Common Mistakes to Avoid

### Mistake 1: Full MSA Translation

❌ "واجهة برمجة التطبيقات تقوم بإرسال الطلب إلى الخادم"
✅ "الـ API بيبعت request للـ server"

### Mistake 2: Translating Technical Terms

❌ "الدالة بتأخذ المعاملات وبترجع القيمة"
✅ "الـ function بتاخد parameters وبترجّع value"

### Mistake 3: Overly Formal Tone

❌ "يتوجب عليك أولاً أن تتأكد من صحة المدخلات"
✅ "أول حاجة تشيك على الـ input إنه صح"

### Mistake 4: Forgetting Egyptian Verb Forms

❌ "يذهب إلى" (MSA)
✅ "بيروح لـ" (Egyptian)

❌ "لا يعمل" (MSA)
✅ "مش شغال" (Egyptian)

### Mistake 5: No Code-Switching

❌ Pure Arabic: "حلقة التكرار بتمر على كل العناصر في المصفوفة"
✅ Natural mix: "الـ loop بيعدي على كل الـ elements في الـ array"

### Mistake 6: Wrong Arabic Script for Borrowed Words

❌ "فانكشن" (wrong transliteration)
✅ Just write "function" in English — don't force transliteration of common terms

---

## Example Translations

### Example 1: Explaining an API

**English:**

> "An API is like a waiter at a restaurant. You tell the waiter what you want (that's the request), the waiter goes to the kitchen (that's the server), and brings back your food (that's the response). You never go to the kitchen yourself — the waiter handles everything."

**Egyptian Arabic:**

> "الـ API ده زي الويتر في المطعم. أنت بتقوله عايز إيه (ده الـ request)، الويتر بيروح المطبخ (ده الـ server)، وبيرجعلك بالأكل (ده الـ response). أنت مبتروحش المطبخ بنفسك — الويتر بيعملك كل حاجة."

### Example 2: Debugging a Problem

**English:**

> "The user clicks the button but nothing happens. No error message, no loading indicator — just nothing. Based on what you know about the frontend-backend flow, where would you look first?"

**Egyptian Arabic:**

> "اليوزر بيدوس على الزرار ومفيش حاجة بتحصل. مفيش error message، مفيش loading — مفيش أي حاجة. بناءً على اللي تعرفه عن الـ flow بين الـ frontend والـ backend، هتبص فين الأول؟"

### Example 3: Reverse Prompt

**English:**

> "Before I explain what caching does — you notice the page loads instantly the second time you visit it. Why do you think that is?"

**Egyptian Arabic:**

> "قبل ما أشرحلك الـ caching بيعمل إيه — أنت لاحظت إن الصفحة بتحمّل بسرعة أوي تاني مرة تفتحها. ليه تفتكر كده؟"

### Example 4: Teaching a Concept

**English:**

> "Environment variables are like secret notes you pass to your app. Instead of writing your database password directly in the code (where anyone could see it), you store it in a separate file that never gets uploaded to GitHub."

**Egyptian Arabic:**

> "الـ environment variables دي زي ورق سري بتديه للـ app بتاعك. بدل ما تكتب الـ database password في الـ code (أي حد يقدر يشوفه)، بتحطه في فايل لوحده ومبيتعملوش upload على GitHub خالص."

### Example 5: Quiz Question

**English:**

> "A user reports that their changes are saved successfully (they see a success message) but the data is gone when they reload. Based on what you learned about state management — what's probably happening?"

**Egyptian Arabic:**

> "يوزر بيقولك إن التعديلات بتتحفظ (بيشوف رسالة نجاح) بس لما بيعمل reload البيانات بتختفي. بناءً على اللي اتعلمته عن الـ state management — إيه اللي بيحصل على الأرجح؟"
