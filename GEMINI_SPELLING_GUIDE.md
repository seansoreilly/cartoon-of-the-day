# Quick Reference: Gemini Spelling Accuracy Guide

## Problem
Gemini can misspell words in both text generation (JSON) and image generation (visuals).

## Solutions Implemented

### ✅ Text Generation (JSON Concepts)
Use **Structured Output** to guarantee spelling consistency:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "why_funny": {"type": "string"}
    }
}

generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
    response_schema=schema,
    temperature=0.4  # Lower = more consistent
)

model = genai.GenerativeModel('gemini-2.0-flash-exp', 
                             generation_config=generation_config)
```

**Benefits:**
- 100% valid JSON output
- Consistent spelling in all fields
- No regex parsing needed
- Schema-enforced accuracy

---

### ✅ Image Generation (Text in Cartoons)
Use **enhanced prompts** with explicit text rendering requirements:

```python
prompt = f"""
Create a cartoon with title: "{title}"

TEXT RENDERING REQUIREMENTS (CRITICAL):
- If text appears in the cartoon, spell it EXACTLY: {title}
- Use clear, bold, sans-serif fonts
- Make text large and well-spaced
- Avoid stylized fonts
- Double-check all word spellings
"""

generation_config = genai.GenerationConfig(
    temperature=0.3  # Lower = more deterministic
)

model = genai.GenerativeModel('gemini-2.5-flash-image',
                             generation_config=generation_config)
```

**Benefits:**
- Explicit text rendering guidance
- Lower temperature for consistency
- Font style specifications
- Spelling verification instructions

---

## Quick Checklist

### For JSON/Text Output
- [ ] Use `response_mime_type="application/json"`
- [ ] Define `response_schema` with required fields
- [ ] Set `temperature=0.4` or lower
- [ ] Remove regex-based parsing
- [ ] Test with mocked responses

### For Image Output
- [ ] Quote exact text: `Title: "{title}"`
- [ ] Add TEXT RENDERING REQUIREMENTS section
- [ ] Specify font styles descriptively
- [ ] Include spelling verification instruction
- [ ] Use `temperature=0.3` for consistency

---

## Model Recommendations

| Model | Use Case | Temperature | Notes |
|-------|----------|-------------|-------|
| `gemini-2.0-flash-exp` | Text/JSON generation | 0.4 | Structured output recommended |
| `gemini-2.5-flash-image` | Image generation | 0.3 | Good text rendering capabilities |
| `gemini-2.0-flash` | Comic scripting | Default | No text rendering needed |
| `imagen-3.0` | Text-heavy images | 0.3 | Specialized for typography |

---

## Common Issues & Fixes

### Issue: JSON Parsing Errors
**Cause:** Model adds markdown or extra text  
**Fix:** Use structured output with `response_mime_type="application/json"`

### Issue: Misspelled Words in Images
**Cause:** Low contrast fonts or generic instructions  
**Fix:** Use quotes, specify "bold sans-serif", lower temperature to 0.3

### Issue: Inconsistent Concept Titles
**Cause:** High temperature (default 1.0)  
**Fix:** Lower to 0.4 with structured output

### Issue: Text Rendering in Wrong Font
**Cause:** No font specification in prompt  
**Fix:** Add descriptive font guidance: "clean, bold, sans-serif"

---

## Testing Tips

1. **Test Prompt Variations** - Try different phrasings
2. **Monitor Temperature** - Lower = more consistent, less creative
3. **Validate Schema** - Ensure all fields are required and typed
4. **Sample Multiple Generations** - Check consistency across runs
5. **Use OCR Validation** - Verify text accuracy programmatically

```python
# Example: Validate image text
import pytesseract
extracted = pytesseract.image_to_string(image)
is_correct = expected_title.lower() in extracted.lower()
```

---

## References
- [Google's Prompting Guide](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Structured Output Docs](https://firebase.google.com/docs/ai-logic/generate-structured-output)
- [Image Generation Best Practices](https://ai.google.dev/gemini-api/docs/image-generation)

---
**Last Updated:** November 7, 2025
