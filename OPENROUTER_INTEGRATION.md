# OpenRouter Integration for Enhanced Comic Script Generation

## Overview
Integrated OpenRouter API to use **Claude 3.5 Sonnet** - the best available model for creative writing and comedy scripts.

## Configuration

### API Key Setup
Added to `.env`:
```env
OPENROUTER_API_KEY=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
```

## Models Research Results

### Top 5 Models for Creative Writing & Comedy

1. **Claude 3.5 Sonnet** ⭐ (Selected)
   - Model ID: `anthropic/claude-3.5-sonnet:beta`
   - **Best for**: Poetry, artistic expression, nuanced humor
   - **Strengths**: Less generic, more creative responses, human-like dialogue
   - **Why chosen**: Superior creative writing, better humor understanding

2. **Mistral Nemo 12B Celeste**
   - Model ID: `nothingiisreal/mn-celeste-12b`
   - Specialized for story writing and roleplaying
   - Fine-tuned on Reddit Writing Prompts

3. **Midnight Rose 70B**
   - Model ID: `sophosympatheia/midnight-rose-70b`
   - Best for long-form creative content
   - Produces lengthy, detailed output

4. **GPT-4o (November 2024)**
   - Model ID: `openai/gpt-4o-2024-11-20`
   - Most versatile, recent creative improvements
   - Good for switching between styles

5. **Llama 3 Lunaris**
   - Best for imaginative flair and quirky comedy
   - Poetic style with creative edge

## Implementation

### New Files Created
- `src/image_generator_openrouter.py` - Enhanced image generator with OpenRouter support

### Key Features
1. **Primary Model**: Claude 3.5 Sonnet via OpenRouter for comic scripts
2. **Fallback**: Gemini exp-1121 if OpenRouter unavailable
3. **Image Generation**: Still uses Gemini 2.5 Flash Image (unchanged)

### Usage Flow
1. Comic script generation uses Claude 3.5 Sonnet (superior creativity)
2. Cartoon concepts use Gemini exp-1121 (already upgraded)
3. Image generation uses Gemini 2.5 Flash Image (visual output)

## Benefits

### Immediate Improvements
- **Better Humor**: Claude 3.5 Sonnet excels at comedy and wit
- **Richer Scripts**: More detailed panel descriptions and visual gags
- **Better Dialogue**: More natural, engaging speech bubbles
- **Creative Edge**: Less generic, more original concepts

### Technical Advantages
- Automatic fallback to Gemini if OpenRouter fails
- Clear model attribution in UI ("✨ Comic script generated using anthropic/claude-3.5-sonnet")
- Temperature and parameters optimized for creative writing

## Testing

Run the app to test the new integration:
```bash
streamlit run app.py
```

Look for:
- "✨ Using OpenRouter-enhanced image generator with Claude 3.5 Sonnet" in console
- "✨ Comic script generated using anthropic/claude-3.5-sonnet" in the UI during generation

## API Costs

- **Claude 3.5 Sonnet**: ~$3 per million input tokens, $15 per million output tokens
- **Average comic script**: ~500-1000 tokens output
- **Estimated cost**: ~$0.015 per comic script generation

## Future Enhancements

Consider experimenting with:
- **Mistral Nemo Celeste** for story-heavy cartoons
- **Midnight Rose 70B** for longer, more detailed scripts
- **Model switching** based on cartoon style preferences

## Troubleshooting

If OpenRouter fails:
- Check API key in `.env`
- Verify OpenRouter service status
- System automatically falls back to Gemini exp-1121

## Summary

The integration of Claude 3.5 Sonnet via OpenRouter represents a significant upgrade in comic script quality. The model's superior creative writing abilities, nuanced humor understanding, and natural dialogue generation make it ideal for creating engaging, funny cartoon scripts that translate well to visual media.