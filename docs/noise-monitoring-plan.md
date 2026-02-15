# Noise Monitoring Feature — Implementation Plan

## Overview

Add real-time ambient noise monitoring to Baby O'Clock that listens via the device microphone, displays sound levels on a reactive meter, and shows pediatric-safe decibel ranges so parents can ensure the nursery environment is appropriate.

---

## Technical Approach

All processing is **client-side JavaScript** using the Web Audio API. No new Flask endpoints are needed for the core feature.

### Core Pipeline

```
getUserMedia (mic) → AudioContext → MediaStreamSource → AnalyserNode → RMS calculation → dB conversion → UI update via requestAnimationFrame
```

### Key Code Pattern

```javascript
// 1. Request microphone access
const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

// 2. Set up the audio processing graph
const audioCtx = new AudioContext();
const source = audioCtx.createMediaStreamSource(stream);
const analyser = audioCtx.createAnalyser();
analyser.fftSize = 2048;
source.connect(analyser);

// 3. Read amplitude data each frame
const dataArray = new Float32Array(analyser.fftSize);

function update() {
    analyser.getFloatTimeDomainData(dataArray);

    // Calculate RMS (root mean square) amplitude
    let sumSquares = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sumSquares += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sumSquares / dataArray.length);

    // Convert to decibels (with calibration offset)
    // The offset accounts for mic sensitivity differences across devices
    const CALIBRATION_OFFSET = 30;
    const db = 20 * Math.log10(rms) + CALIBRATION_OFFSET;

    // Update the UI with the dB value
    updateMeter(db);

    requestAnimationFrame(update);
}

update();
```

---

## Library Evaluation

| Library | Stars | Verdict | Notes |
|---|---|---|---|
| **DIY with `AnalyserNode`** | — | **Recommended** | ~30-40 lines of JS. No deps. Matches app's zero-npm philosophy. Full UI control. |
| [`web-audio-peak-meter`](https://github.com/esonderegger/web-audio-peak-meter) | 136 | Best packaged option | ITU-R BS.1770 metering, configurable dB range/colors/gradient. Would require CDN or build step. |
| [`db-meter`](https://github.com/takispig/db-meter) | — | Good reference | Pure JS, no deps. Uses `20*log10(rms) + offset` with configurable calibration offset (default 30 dB). |
| [`volume-meter`](https://www.npmjs.com/package/volume-meter) | — | Usable | Wraps `AnalyserNode.getByteTimeDomainData()`, returns volume as percentage with tweening. |
| [`decibel-meter`](https://www.npmjs.com/package/decibel-meter) | — | Skip | Last published 8+ years ago. Stale/unmaintained. |

### Why DIY Is the Right Choice

- Baby O'Clock has **zero npm dependencies** — just Flask + openpyxl on the backend and a single Chart.js CDN on the frontend
- The core metering logic is only ~30-40 lines of JavaScript
- The app already has the `getUserMedia` pattern (voice input feature flag)
- Full control over the "approved range" visualization, colors, and thresholds
- No build step, no bundler — just inline JS like everything else in `index.html`

---

## Safe Decibel Ranges for Babies

Based on pediatric and audiological guidelines:

| Level | dB Range | Color | Guidance |
|---|---|---|---|
| **Ideal (sleep)** | 30–45 dB | Green | Quiet nursery, soft white noise |
| **Acceptable** | 45–50 dB | Green/Yellow | Hospital NICU standard limit |
| **Caution** | 50–60 dB | Yellow/Orange | CDC upper limit for infants |
| **Dangerous** | 60–70 dB | Red | Risk of hearing damage over time |
| **Never exceed** | 70+ dB | Deep Red | Hearing Health Foundation absolute ceiling |

### Sources

- [Melody Audiology — What decibel level is safe for babies?](https://melodyaudiology.com/faqs/what-decibel-level-is-safe-for-babies/)
- [Decibel Pro — Safe Decibel Levels for Babies](https://decibelpro.app/blog/safe-decibel-levels-for-babies/)
- [SNOOZ — Safe Decibel Levels for Infants](https://getsnooz.com/blogs/snoozweek/safe-decibel-levels-for-infants)
- [Nanit — How Loud Is Too Loud for a Baby?](https://www.nanit.com/blogs/parent-confidently/how-loud-is-too-loud-for-a-baby)
- [Hatch — Safe Sleep Sounds](https://www.hatch.co/blog/sound-machine-safety-baby)

---

## UI Design

### Placement

Add a **"Noise" tab** alongside the existing Tracker and Charts tabs (reuse the existing swipe/tab navigation).

### Meter Design

A vertical or arc-shaped meter with:

- **Real-time bar** that reacts to current dB level (updates every animation frame)
- **Color-coded zones** painted on the meter background:
  - Green zone: 0–50 dB (safe)
  - Yellow zone: 50–60 dB (caution)
  - Red zone: 60+ dB (dangerous)
- **Current dB readout** displayed as a large number (e.g., "42 dB")
- **Zone label** below the readout (e.g., "Safe for baby" / "Getting loud" / "Too loud!")
- **"Approved range" bracket** visually marked on the meter (30–50 dB highlighted)

### Controls

- **Start/Stop toggle button** — big touch target, consistent with existing button styles
  - Manages mic permissions and battery life
  - Shows mic status (active/inactive)
- **Calibration note** — small text explaining readings are approximate

### Visual Consistency

- Match existing dark mode color scheme
- Use the same font sizes, border radius, and spacing as existing cards
- Reuse the CSS variable system already in place

### Mockup (ASCII)

```
┌─────────────────────────────┐
│  🔇  Nursery Noise Monitor  │
│                             │
│     ┌───┐                   │
│     │   │  ← Red (60+ dB)  │
│     │   │                   │
│     │   │  ← Yellow (50-60) │
│     │▓▓▓│                   │
│     │▓▓▓│  ← Green (30-50) │
│     │▓▓▓│                   │
│     │▓▓▓│                   │
│     └───┘                   │
│                             │
│        42 dB                │
│    ✅ Safe for baby         │
│                             │
│   [ 🎙 Stop Listening ]    │
│                             │
│  Readings are approximate.  │
│  Place phone near baby's    │
│  sleep area for best        │
│  results.                   │
└─────────────────────────────┘
```

---

## Implementation Steps

### Step 1: Add the Noise Tab to Navigation

In `templates/index.html`, extend the tab system:

- Add a third tab button ("Noise") to the tab bar
- Add a new tab content container (`noise-tab`)
- Update the swipe/tab switching logic to handle three tabs

### Step 2: Build the Noise Monitor UI

Inside the new tab container, add:

- A `<canvas>` element for the meter (or styled `<div>` elements)
- The dB readout display
- The zone status label
- The start/stop button
- Informational text about calibration

### Step 3: Implement the Audio Pipeline

```javascript
// Feature flag (like the existing voice input flag)
const FEATURE_FLAGS = {
    VOICE_INPUT_ENABLED: false,
    NOISE_MONITOR_ENABLED: true  // New flag
};
```

Core implementation:

1. **`startNoiseMonitor()`** — requests mic access, creates AudioContext + AnalyserNode, begins the update loop
2. **`stopNoiseMonitor()`** — stops the mic stream, closes AudioContext, cancels animation frame
3. **`calculateDecibels(analyser)`** — reads float time-domain data, computes RMS, converts to dB with calibration offset
4. **`updateMeter(db)`** — updates the canvas/div meter position and the dB readout text
5. **`getNoiseZone(db)`** — returns the zone info (label, color, icon) for a given dB level

### Step 4: Draw the Meter

Option A — **Canvas-based** (smoother animation):

```javascript
function drawMeter(ctx, db, width, height) {
    const zones = [
        { max: 50, color: '#4CAF50' },  // Green
        { max: 60, color: '#FFC107' },  // Yellow
        { max: 100, color: '#F44336' }  // Red
    ];

    // Draw background zones
    // Draw current level bar
    // Draw "approved range" bracket (30-50 dB)
    // Draw tick marks and labels
}
```

Option B — **CSS-based** (simpler, matches existing app style):

```html
<div class="noise-meter">
    <div class="meter-zone meter-red"></div>
    <div class="meter-zone meter-yellow"></div>
    <div class="meter-zone meter-green"></div>
    <div class="meter-level" style="height: 42%"></div>
</div>
```

### Step 5: Handle Edge Cases

- **Permission denied**: Show a friendly message explaining why mic access is needed
- **AudioContext suspended**: Call `audioCtx.resume()` on user gesture (required by iOS Safari)
- **Browser not supported**: Check for `navigator.mediaDevices` and show fallback message
- **HTTPS requirement**: `getUserMedia` requires a secure context — the app runs on localhost which qualifies, but document this for remote access scenarios
- **Battery/performance**: Stop the monitor when the tab is hidden (`visibilitychange` event)

### Step 6: Optional — Log Noise Events to Excel

If desired, add a Flask endpoint to record peak noise events:

```
POST /api/noise-log
Body: { peak_db, avg_db, duration_seconds, timestamp }
```

This would create entries in the Excel file with Type = "Noise (Peak: 65 dB)" for historical review. This is an optional enhancement — the core feature works entirely client-side.

---

## Browser Compatibility

| Browser | getUserMedia | AudioContext | AnalyserNode | Status |
|---|---|---|---|---|
| **Safari (iOS)** | ✅ | ✅ (needs user gesture to resume) | ✅ | Works — primary target |
| **Chrome (Android)** | ✅ | ✅ | ✅ | Works — primary target |
| **Chrome (Desktop)** | ✅ | ✅ | ✅ | Works |
| **Firefox** | ✅ | ✅ | ✅ | Works (unlike Speech API) |
| **Edge** | ✅ | ✅ | ✅ | Works |

### iOS Safari Caveats

1. **User gesture required**: `AudioContext` must be created or resumed in response to a tap (the Start button handles this)
2. **Audio routing**: When mic is active, iOS may route audio to the speaker instead of headphones — this is a known WebKit bug but doesn't affect metering
3. **Permission persistence**: Safari's mic permissions are less persistent than Chrome — users may need to re-grant on revisit

---

## Calibration Note

Web-based dB readings are **relative, not absolute**. Every phone mic has different sensitivity and frequency response. The calibration offset (default +30 dB based on the `db-meter` library's research) gets readings into the right ballpark, but this will never match a professional sound level meter.

For the use case of "is the nursery environment roughly appropriate?" — this level of accuracy is more than sufficient. The meter should display a disclaimer like:

> *Readings are approximate. For precise measurements, use a dedicated sound level meter.*

A potential future enhancement would be a user-facing calibration step (e.g., "tap here while in a quiet room to calibrate") that adjusts the offset.

---

## Reference Links

- [Measuring Audio Volume in JavaScript](https://jameshfisher.com/2021/01/18/measuring-audio-volume-in-javascript/) — cleanest DIY tutorial
- [`web-audio-peak-meter` (GitHub)](https://github.com/esonderegger/web-audio-peak-meter) — best packaged library
- [`db-meter` (GitHub)](https://github.com/takispig/db-meter) — good reference with calibration offset
- [MDN — Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [MDN — getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [MDN — AnalyserNode](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode)
- [Getting Started with getUserMedia (2025)](https://blog.addpipe.com/getusermedia-getting-started/)
- [Can I Use — Web Audio API](https://caniuse.com/audio-api)
