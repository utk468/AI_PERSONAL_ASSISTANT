// Web Audio API Custom Bell Synthesizer Alerts (Zero static files loading dependency)
export function playChimeAlert() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Tone 1: High crisp bell tone (D5 to A5 transition)
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        osc1.type = "sine";
        osc1.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
        osc1.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.12); // A5
        
        gain1.gain.setValueAtTime(0.12, ctx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.7);
        
        osc1.connect(gain1);
        gain1.connect(ctx.destination);

        // Tone 2: Synchronous warm baseline chord support (A4)
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = "triangle";
        osc2.frequency.setValueAtTime(440.00, ctx.currentTime); // A4
        
        gain2.gain.setValueAtTime(0.06, ctx.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
        
        osc2.connect(gain2);
        gain2.connect(ctx.destination);

        osc1.start();
        osc2.start();

        osc1.stop(ctx.currentTime + 0.7);
        osc2.stop(ctx.currentTime + 0.5);
    } catch (e) {
        console.warn("Web Audio API alert chime blocked or unsupported by browser:", e);
    }
}
