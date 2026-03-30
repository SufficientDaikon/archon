# Gemini API — Image Generation Quick Reference

## Authentication

```bash
# Get free API key
# https://aistudio.google.com/apikey

# Set environment variable
export GEMINI_API_KEY=your_key_here

# Or add to .env.local
echo "GEMINI_API_KEY=your_key_here" >> .env.local
```

## Models

| Model            | ID                                 | Best For                          | Speed   |
| ---------------- | ---------------------------------- | --------------------------------- | ------- |
| Nano Banana 2    | `gemini-3.1-flash-image-preview`   | General generation + editing      | Fast    |
| Nano Banana Pro  | `gemini-3-pro-image-preview`       | Highest quality (uses "thinking") | Medium  |
| Nano Banana      | `gemini-2.5-flash-image`           | High-volume, low-latency          | Fastest |
| Flash (text)     | `gemini-2.0-flash`                 | Vision/analysis (no image output) | Fastest |
| Imagen 3         | `imagen-3.0-generate-002`          | Batch generation (1-4 images)     | Medium  |

## Aspect Ratios

| Ratio  | Name          | Use Case                     |
| ------ | ------------- | ---------------------------- |
| `1:1`  | Square        | Avatars, icons, social posts |
| `3:4`  | Portrait      | Cards, mobile screens        |
| `4:3`  | Standard      | Cards, slides                |
| `9:16` | Tall Portrait | Mobile hero, stories         |
| `16:9` | Landscape     | Hero backgrounds, banners    |

## Node.js SDK

### Install

```bash
npm install @google/genai
```

### Generate Image

```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const response = await ai.models.generateContent({
  model: "gemini-3.1-flash-image-preview",
  contents: "your prompt here",
  config: {
    responseModalities: ["TEXT", "IMAGE"],
  },
});

// Extract image data
for (const part of response.candidates[0].content.parts) {
  if (part.inlineData) {
    const buffer = Buffer.from(part.inlineData.data, "base64");
    fs.writeFileSync("output.png", buffer);
  }
  if (part.text) {
    console.log(part.text);
  }
}
```

### Analyze Image (Vision)

```typescript
const imageData = fs.readFileSync("image.png");
const base64 = imageData.toString("base64");

const response = await ai.models.generateContent({
  model: "gemini-2.0-flash",
  contents: [
    {
      role: "user",
      parts: [
        { inlineData: { data: base64, mimeType: "image/png" } },
        { text: "Describe what you see in this image" },
      ],
    },
  ],
});
```

### Edit Image

```typescript
const imageData = fs.readFileSync("source.png");
const base64 = imageData.toString("base64");

const response = await ai.models.generateContent({
  model: "gemini-3.1-flash-image-preview",
  contents: [
    {
      role: "user",
      parts: [
        { inlineData: { data: base64, mimeType: "image/png" } },
        { text: "Make the background darker and add a cyan glow effect" },
      ],
    },
  ],
  config: {
    responseModalities: ["TEXT", "IMAGE"],
  },
});
```

## Python SDK

### Install

```bash
pip install google-genai
```

### Generate

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="your prompt here",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    ),
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("output.png", "wb") as f:
            f.write(part.inline_data.data)
```

## Error Handling

| Error Code | Meaning         | Fix                                        |
| ---------- | --------------- | ------------------------------------------ |
| 401        | Invalid API key | Check GEMINI_API_KEY                       |
| 403        | API not enabled | Enable Gemini API in Google Cloud console  |
| 429        | Rate limited    | Wait and retry (exponential backoff)       |
| 400        | Bad request     | Check prompt (may contain blocked content) |
| 500        | Server error    | Retry after delay                          |

## Rate Limits (Free Tier)

| Resource          | Limit     |
| ----------------- | --------- |
| Requests/min      | 15        |
| Requests/day      | 1,500     |
| Input tokens/min  | 1,000,000 |
| Output tokens/min | 250,000   |

## Tips

1. **Prompt length matters** — Longer, more detailed prompts = better results
2. **Be specific about style** — Reference real cameras, film stocks, artists
3. **Avoid text in images** — AI renders text poorly, use CSS/SVG instead
4. **Iterate via editing** — Generate base → edit → edit → refine
5. **Multi-turn works** — Start a conversation and refine step by step
6. **responseModalities is required** — Must include "IMAGE" for image generation
7. **Check for text response** — Model may return text explaining why it couldn't generate
