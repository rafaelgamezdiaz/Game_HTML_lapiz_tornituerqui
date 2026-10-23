// Web Audio Procedural Synthesizer for "La Gran Carrera del Barquito de Vania"
class SoundManager {
    constructor() {
        this.ctx = null;
        this.muted = false;
        this.musicPlaying = false;
        this.musicTimer = null;
        this.waterGain = null;
        this.waterSource = null;
    }

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioCtx();
            this.startWaterLoop();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    startWaterLoop() {
        if (!this.ctx || this.waterSource) return;
        try {
            const bufferSize = 2 * this.ctx.sampleRate;
            const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
            const output = noiseBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }
            const whiteNoise = this.ctx.createBufferSource();
            whiteNoise.buffer = noiseBuffer;
            whiteNoise.loop = true;

            const filter = this.ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(450, this.ctx.currentTime);
            filter.Q.setValueAtTime(1.8, this.ctx.currentTime);

            this.waterGain = this.ctx.createGain();
            this.waterGain.gain.setValueAtTime(0.04, this.ctx.currentTime);

            whiteNoise.connect(filter);
            filter.connect(this.waterGain);
            this.waterGain.connect(this.ctx.destination);
            whiteNoise.start();
            this.waterSource = whiteNoise;
        } catch (e) {
            console.warn('Water audio loop init error', e);
        }
    }

    playButton() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(580, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
    }

    playJump() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(780, now + 0.22);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.26);
    }

    playStar() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 arpeggio
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + idx * 0.05);

            gain.gain.setValueAtTime(0, now + idx * 0.05);
            gain.gain.linearRampToValueAtTime(0.12, now + idx * 0.05 + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.05 + 0.25);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now + idx * 0.05);
            osc.stop(now + idx * 0.05 + 0.3);
        });
    }

    playGear() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(1320, now + 0.12);

        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.22);
    }

    playWindBoost() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const bufferSize = this.ctx.sampleRate * 1.5;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = noiseBuffer;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(200, now);
        filter.frequency.exponentialRampToValueAtTime(1600, now + 0.4);
        filter.frequency.exponentialRampToValueAtTime(300, now + 1.4);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.25, now + 0.3);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        noise.start(now);
        noise.stop(now + 1.5);
    }

    playPencilBridge() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        // Whimsical drawing chirp + glissando
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(350, now);
        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.35);

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1500, now);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.5);
    }

    playRepair() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        // "Clinc-clanc" two-tone metallic tap
        const freqs = [1760, 2340];
        freqs.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            const startTime = now + idx * 0.08;
            osc.frequency.setValueAtTime(freq, startTime);
            osc.frequency.exponentialRampToValueAtTime(freq * 0.7, startTime + 0.15);

            gain.gain.setValueAtTime(0.2, startTime);
            gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.18);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(startTime);
            osc.stop(startTime + 0.2);
        });
    }

    playObstacleHit() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.exponentialRampToValueAtTime(70, now + 0.25);

        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.32);
    }

    playJump() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.exponentialRampToValueAtTime(850, now + 0.28);

        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
    }

    playSplash() {
        if (!this.ctx || this.muted) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(450, now);
        osc.frequency.exponentialRampToValueAtTime(140, now + 0.2);

        gain.gain.setValueAtTime(0.16, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.28);
    }

    playWinFanfare() {
        if (!this.ctx || this.muted) return;
        const melody = [
            { f: 523.25, d: 0.15 }, // C5
            { f: 659.25, d: 0.15 }, // E5
            { f: 783.99, d: 0.15 }, // G5
            { f: 1046.50, d: 0.4 }  // C6
        ];
        let offset = 0;
        const now = this.ctx.currentTime;
        melody.forEach(item => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(item.f, now + offset);

            gain.gain.setValueAtTime(0, now + offset);
            gain.gain.linearRampToValueAtTime(0.2, now + offset + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + offset + item.d);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now + offset);
            osc.stop(now + offset + item.d + 0.05);

            offset += item.d + 0.05;
        });
    }

    toggleMusic() {
        if (this.musicPlaying) {
            this.stopMusic();
        } else {
            this.startMusic();
        }
        return this.musicPlaying;
    }

    startMusic() {
        if (!this.ctx) this.init();
        if (this.musicPlaying) return;
        this.musicPlaying = true;

        const bassLine = [261.63, 329.63, 392.00, 329.63]; // C4, E4, G4, E4
        const leadNotes = [523.25, 587.33, 659.25, 783.99, 880.00, 783.99, 659.25, 587.33];
        let step = 0;

        const tick = () => {
            if (!this.musicPlaying || this.muted) {
                this.musicTimer = setTimeout(tick, 220);
                return;
            }
            const now = this.ctx.currentTime;

            // Soft bass pluck
            if (step % 2 === 0) {
                const bFreq = bassLine[(step / 2) % bassLine.length];
                const bOsc = this.ctx.createOscillator();
                const bGain = this.ctx.createGain();
                bOsc.type = 'triangle';
                bOsc.frequency.setValueAtTime(bFreq / 2, now);
                bGain.gain.setValueAtTime(0.07, now);
                bGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
                bOsc.connect(bGain);
                bGain.connect(this.ctx.destination);
                bOsc.start(now);
                bOsc.stop(now + 0.38);
            }

            // Lead marimba-like beep
            const leadFreq = leadNotes[step % leadNotes.length];
            const lOsc = this.ctx.createOscillator();
            const lGain = this.ctx.createGain();
            lOsc.type = 'sine';
            lOsc.frequency.setValueAtTime(leadFreq, now);
            lGain.gain.setValueAtTime(0.045, now);
            lGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
            lOsc.connect(lGain);
            lGain.connect(this.ctx.destination);
            lOsc.start(now);
            lOsc.stop(now + 0.2);

            step++;
            this.musicTimer = setTimeout(tick, 220);
        };

        tick();
    }

    stopMusic() {
        this.musicPlaying = false;
        if (this.musicTimer) {
            clearTimeout(this.musicTimer);
            this.musicTimer = null;
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        if (this.waterGain) {
            this.waterGain.gain.setValueAtTime(this.muted ? 0 : 0.04, this.ctx.currentTime);
        }
        return this.muted;
    }
}

window.soundManager = new SoundManager();
