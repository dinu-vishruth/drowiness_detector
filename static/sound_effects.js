/* ==========================================================================
   AuraFocus - Web Audio API Sound Synthesizer (No external assets required)
   ========================================================================== */

let audioCtx = null;
let sirenOscillator = null;
let sirenLfo = null;
let sirenGain = null;
let isSirenPlaying = false;

function initAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

/**
 * Plays a double chime warning (Level 1 warning).
 */
function playWarningChime() {
    try {
        initAudioContext();
        
        const now = audioCtx.currentTime;
        
        // Chime 1
        const osc1 = audioCtx.createOscillator();
        const gain1 = audioCtx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc1.frequency.exponentialRampToValueAtTime(880.00, now + 0.15); // A5
        gain1.gain.setValueAtTime(0.12, now);
        gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
        
        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.start(now);
        osc1.stop(now + 0.35);
        
        // Chime 2 (delayed slightly)
        setTimeout(() => {
            const osc2 = audioCtx.createOscillator();
            const gain2 = audioCtx.createGain();
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(880.00, audioCtx.currentTime); // A5
            osc2.frequency.exponentialRampToValueAtTime(1174.66, audioCtx.currentTime + 0.15); // D6
            gain2.gain.setValueAtTime(0.12, audioCtx.currentTime);
            gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
            
            osc2.connect(gain2);
            gain2.connect(audioCtx.destination);
            osc2.start(audioCtx.currentTime);
            osc2.stop(audioCtx.currentTime + 0.35);
        }, 150);
        
    } catch (e) {
        console.error("Failed to synthesize warning chime:", e);
    }
}

/**
 * Starts a loud modulating siren (Level 2/3 alarm).
 */
function startSirenAlarm() {
    if (isSirenPlaying) return;
    try {
        initAudioContext();
        
        const now = audioCtx.currentTime;
        sirenOscillator = audioCtx.createOscillator();
        sirenLfo = audioCtx.createOscillator();
        const lfoGain = audioCtx.createGain();
        sirenGain = audioCtx.createGain();
        
        // Setup Carrier Oscillator (Square wave for aggressive sound)
        sirenOscillator.type = 'sawtooth';
        sirenOscillator.frequency.setValueAtTime(600, now);
        
        // Setup LFO to modulate carrier frequency (siren effect)
        sirenLfo.type = 'sine';
        sirenLfo.frequency.setValueAtTime(3.5, now); // 3.5 cycles per second
        lfoGain.gain.setValueAtTime(250, now); // modulate by +/- 250Hz
        
        // Setup Gain (Volume control)
        sirenGain.gain.setValueAtTime(0.15, now);
        
        // Connect LFO
        sirenLfo.connect(lfoGain);
        lfoGain.connect(sirenOscillator.frequency);
        
        // Connect Carrier to Output
        sirenOscillator.connect(sirenGain);
        sirenGain.connect(audioCtx.destination);
        
        // Start Oscillators
        sirenOscillator.start(now);
        sirenLfo.start(now);
        
        isSirenPlaying = true;
    } catch (e) {
        console.error("Failed to start siren alarm:", e);
    }
}

/**
 * Stops the siren alarm.
 */
function stopSirenAlarm() {
    if (!isSirenPlaying) return;
    try {
        const now = audioCtx.currentTime;
        
        // Smoothly ramp down volume to avoid audio click artifacts
        sirenGain.gain.setValueAtTime(sirenGain.gain.value, now);
        sirenGain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        
        setTimeout(() => {
            if (sirenOscillator) {
                sirenOscillator.stop();
                sirenOscillator.disconnect();
                sirenOscillator = null;
            }
            if (sirenLfo) {
                sirenLfo.stop();
                sirenLfo.disconnect();
                sirenLfo = null;
            }
            if (sirenGain) {
                sirenGain.disconnect();
                sirenGain = null;
            }
        }, 120);
        
        isSirenPlaying = false;
    } catch (e) {
        console.error("Failed to stop siren alarm:", e);
    }
}
