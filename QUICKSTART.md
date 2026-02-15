# 🚀 Quick Start Guide

Get Jarvis up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /Users/vy/jarvis
npm run install-all
```

This installs dependencies for both server and client.

## Step 2: Configure API Key

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Get your Claude API key:
   - Go to https://console.anthropic.com/
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key

3. Add the key to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

## Step 3: Start Jarvis

```bash
npm run dev
```

This starts both:
- Server on http://localhost:3001
- Client on http://localhost:5173

## Step 4: Open in Browser

Navigate to **http://localhost:5173**

You should see the Jarvis interface! 🎉

## Using Jarvis

### Text Mode (💬)
- Type messages in the input box
- Press Enter or click ➤ to send
- Responses stream in real-time
- Click 🗑️ Clear to start a new conversation

### Voice Mode (🎤)
- Click "🎤 Talk to Jarvis" to start speaking
- Your words appear as you speak
- Jarvis responds with voice and text
- Click "🔇 Mute" to stop audio playback

### Try These Commands:
- "What time is it?"
- "Give me system info"
- "Tell me about yourself"
- "What can you do?"

## Mobile Access

1. Find your computer's IP address:
```bash
# On macOS/Linux
ifconfig | grep "inet "

# On Windows
ipconfig
```

2. On your phone (same WiFi network):
   - Open browser
   - Go to `http://YOUR_IP:5173`
   - Install as app (Add to Home Screen)

## Troubleshooting

### Server won't start
- Check if port 3001 is available
- Verify Node.js is v18+
- Check `.env` file exists

### Client won't start
- Check if port 5173 is available
- Try `cd client && npm install`

### Voice not working
- Use Chrome or Edge (best support)
- Allow microphone permissions
- Check browser console for errors

### API errors
- Verify Claude API key is correct
- Check you have API credits
- Look at server console for details

## Next Steps

- Read `PLUGIN_GUIDE.md` to add custom capabilities
- Check `README.md` for full documentation
- Explore the code in `server/` and `client/src/`

Need help? Check the console logs or open an issue!
