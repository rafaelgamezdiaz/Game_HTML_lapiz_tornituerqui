// Game Engine: "La Gran Carrera del Barquito de Vania"
class VaniaBoatGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Game State
        this.state = 'title'; // 'title', 'racing', 'celebration', 'shop'
        this.lastTime = 0;
        this.distance = 0;
        this.trackLength = 5000; // units per lap
        this.totalLaps = 2;
        this.currentLap = 1;
        this.raceFinished = false;

        // Happy Points & Currency
        this.happyPoints = parseInt(localStorage.getItem('vania_happy_points') || '0', 10);
        this.starsCollected = 0;
        this.gearsCollected = 0;

        // Customization
        this.selectedSkin = localStorage.getItem('vania_skin') || 'rainbow';
        this.selectedHat = localStorage.getItem('vania_hat') || 'none';
        this.unlockedSkins = JSON.parse(localStorage.getItem('vania_unlocked_skins') || '["rainbow"]');
        this.unlockedHats = JSON.parse(localStorage.getItem('vania_unlocked_hats') || '["none"]');

        // Player Boat Properties (Enlarged for 3D visibility)
        this.player = {
            x: 0, // relative to river center (-riverWidth/2 to riverWidth/2)
            y: 0,
            width: 148,
            height: 184,
            vx: 0,
            tilt: 0,
            baseSpeed: 210,
            speed: 210,
            maxSpeed: 420,
            speedRatio: 0.5,
            jumpZ: 0,
            jumpVz: 0,
            isJumping: false,
            invulnerableTime: 0,
            shieldTime: 0,
            boostTime: 0,
            bridgeAnimation: null
        };

        // Competitors (Enlarged for 3D visibility)
        this.competitors = [
            {
                id: 'leck',
                name: 'Barquito Leck',
                type: 'carton',
                x: -120,
                dist: 140,
                speed: 200,
                width: 115,
                height: 145,
                tilt: 0
            },
            {
                id: 'can',
                name: 'Lata Veloz',
                type: 'soda',
                x: 120,
                dist: 90,
                speed: 208,
                width: 120,
                height: 140,
                tilt: 0
            }
        ];

        // Powers Cooldowns & Status
        this.powers = {
            wind: { name: 'Soplo de Viento', ready: true, cd: 0, maxCd: 6, duration: 3.5, active: false },
            pencil: { name: 'Impulso de Lápiz', ready: true, cd: 0, maxCd: 8, duration: 2.2, active: false },
            repair: { name: 'Súper Reparación', ready: true, cd: 0, maxCd: 5, active: false }
        };

        // Inputs for Parent-Child Coop
        this.inputs = {
            steerLeft: false,
            steerRight: false,
            accelerate: false,
            power1: false,
            power2: false,
            power3: false
        };

        // World Objects
        this.riverWidth = 320;
        this.obstacles = [];
        this.collectibles = [];
        this.particles = [];
        this.ripples = [];
        this.waterfalls = [];

        // Viewport & Scale
        this.cameraY = 0;
        this.scale = 1;

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.setupInputListeners();
        this.populateTrack();
        this.updateHUD();

        requestAnimationFrame((t) => this.gameLoop(t));
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        // Utilize the full width of the screen for the 3D river
        this.riverWidth = Math.max(680, this.canvas.width * 0.90);
    }

    project(worldX, worldDist, worldZ = 0) {
        const horizonY = this.canvas.height * 0.26;
        const bottomY = this.canvas.height * 0.96;
        const cameraLead = 130;
        const relDist = worldDist - (this.distance - cameraLead);

        if (relDist < -80 || relDist > 1600) return null;

        // Normalized perspective depth
        const depth = Math.max(0.001, (relDist + 150) / 150);
        const scale = 1 / depth;

        // Non-linear perspective curve for rich 3D depth
        const p = Math.pow(scale, 0.88);
        const screenY = horizonY + (bottomY - horizonY) * p - (worldZ * scale * 2.6);

        // Gentle 3D meandering river curves
        const curveOffset = Math.sin(worldDist * 0.0016) * (65 * scale);

        // Projected X coordinate
        const screenX = (this.canvas.width * 0.5) + (worldX * scale * 1.02) + curveOffset;

        // River width at this perspective distance (utilizes screen width at foreground)
        const riverSpan = this.canvas.width * (0.22 + 0.70 * p);

        return { screenX, screenY, scale, depth, riverSpan, p, curveOffset };
    }

    setupInputListeners() {
        // Keyboard mapping
        window.addEventListener('keydown', (e) => {
            if (window.soundManager && !window.soundManager.ctx) {
                window.soundManager.init();
            }

            switch (e.code) {
                // J1 (Hijo) - Timón
                case 'ArrowLeft':
                case 'KeyA':
                    this.inputs.steerLeft = true;
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                case 'KeyD':
                    this.inputs.steerRight = true;
                    e.preventDefault();
                    break;
                case 'ArrowUp':
                case 'KeyW':
                    this.inputs.accelerate = true;
                    e.preventDefault();
                    break;

                // J2 (Padre) - Poderes
                case 'Digit1':
                case 'KeyZ':
                case 'KeyJ':
                    this.triggerPower('wind');
                    e.preventDefault();
                    break;
                case 'Digit2':
                case 'KeyX':
                case 'KeyK':
                    this.triggerPower('pencil');
                    e.preventDefault();
                    break;
                case 'Digit3':
                case 'KeyC':
                case 'KeyL':
                    this.triggerPower('repair');
                    e.preventDefault();
                    break;
                case 'Space':
                    // Smart helper: triggers available power in order of need
                    this.autoTriggerHelp();
                    e.preventDefault();
                    break;
            }
        });

        window.addEventListener('keyup', (e) => {
            switch (e.code) {
                case 'ArrowLeft':
                case 'KeyA':
                    this.inputs.steerLeft = false;
                    break;
                case 'ArrowRight':
                case 'KeyD':
                    this.inputs.steerRight = false;
                    break;
                case 'ArrowUp':
                case 'KeyW':
                    this.inputs.accelerate = false;
                    break;
            }
        });

        // Touch & On-Screen Button Binding
        this.bindTouchControls();
    }

    bindTouchControls() {
        // Steer Left Button (J1)
        const btnLeft = document.getElementById('btn-steer-left');
        const btnRight = document.getElementById('btn-steer-right');
        const btnAccel = document.getElementById('btn-accelerate');

        const addPressRelease = (el, onDown, onUp) => {
            if (!el) return;
            const down = (e) => {
                e.preventDefault();
                if (window.soundManager) window.soundManager.init();
                onDown();
            };
            const up = (e) => {
                e.preventDefault();
                onUp();
            };
            el.addEventListener('mousedown', down);
            el.addEventListener('mouseup', up);
            el.addEventListener('touchstart', down, { passive: false });
            el.addEventListener('touchend', up, { passive: false });
        };

        addPressRelease(btnLeft, () => (this.inputs.steerLeft = true), () => (this.inputs.steerLeft = false));
        addPressRelease(btnRight, () => (this.inputs.steerRight = true), () => (this.inputs.steerRight = false));
        addPressRelease(btnAccel, () => (this.inputs.accelerate = true), () => (this.inputs.accelerate = false));

        // Power Buttons (J2)
        const btnWind = document.getElementById('btn-power-wind');
        const btnPencil = document.getElementById('btn-power-pencil');
        const btnRepair = document.getElementById('btn-power-repair');

        if (btnWind) {
            btnWind.addEventListener('click', () => this.triggerPower('wind'));
            btnWind.addEventListener('touchstart', (e) => { e.preventDefault(); this.triggerPower('wind'); }, { passive: false });
        }
        if (btnPencil) {
            btnPencil.addEventListener('click', () => this.triggerPower('pencil'));
            btnPencil.addEventListener('touchstart', (e) => { e.preventDefault(); this.triggerPower('pencil'); }, { passive: false });
        }
        if (btnRepair) {
            btnRepair.addEventListener('click', () => this.triggerPower('repair'));
            btnRepair.addEventListener('touchstart', (e) => { e.preventDefault(); this.triggerPower('repair'); }, { passive: false });
        }

        // Direct drag / touch steering on the left half of the screen
        let isTouchingSteer = false;
        let touchStartX = 0;

        window.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            if (touch.clientX < window.innerWidth * 0.5) {
                isTouchingSteer = true;
                touchStartX = touch.clientX;
            }
        }, { passive: true });

        window.addEventListener('touchmove', (e) => {
            if (!isTouchingSteer) return;
            const touch = e.touches[0];
            const deltaX = touch.clientX - touchStartX;
            if (deltaX < -15) {
                this.inputs.steerLeft = true;
                this.inputs.steerRight = false;
            } else if (deltaX > 15) {
                this.inputs.steerRight = true;
                this.inputs.steerLeft = false;
            } else {
                this.inputs.steerLeft = false;
                this.inputs.steerRight = false;
            }
        }, { passive: true });

        window.addEventListener('touchend', () => {
            isTouchingSteer = false;
            this.inputs.steerLeft = false;
            this.inputs.steerRight = false;
        });
    }

    startRace() {
        if (window.soundManager) {
            window.soundManager.init();
            window.soundManager.startMusic();
        }
        this.state = 'racing';
        this.distance = 0;
        this.currentLap = 1;
        this.raceFinished = false;
        this.player.x = 0;
        this.player.speed = this.player.baseSpeed;
        this.player.jumpZ = 0;
        this.player.isJumping = false;
        this.player.invulnerableTime = 0;
        this.player.shieldTime = 0;
        this.player.boostTime = 0;

        this.competitors[0].dist = 80;
        this.competitors[1].dist = 50;

        this.populateTrack();

        document.getElementById('title-screen').classList.add('hidden');
        document.getElementById('victory-screen').classList.add('hidden');
        document.getElementById('shop-screen').classList.add('hidden');
        document.getElementById('game-hud').classList.remove('hidden');

        this.showSpeechBubble("¡Vamos en equipo! ¡A ganar la carrera!");
    }

    populateTrack() {
        this.obstacles = [];
        this.collectibles = [];
        this.waterfalls = [];

        const totalDist = this.trackLength * this.totalLaps;
        let curDist = 300;

        // Generate track obstacles and collectibles
        while (curDist < totalDist - 400) {
            curDist += 90 + Math.random() * 80;

            const laneX = (Math.random() * 2 - 1) * (this.riverWidth * 0.36);

            // Waterfall / Sidewalk jump ramp every ~800 units
            if (curDist % 850 < 120 && curDist > 600) {
                this.waterfalls.push({
                    dist: curDist,
                    height: 24
                });
                curDist += 80;
                continue;
            }

            const rand = Math.random();
            if (rand < 0.45) {
                // Collectibles
                const type = Math.random() < 0.5 ? 'star' : (Math.random() < 0.75 ? 'gear' : 'candy');
                const gearColor = ['#e74c3c', '#2ecc71', '#3498db', '#9b59b6'][Math.floor(Math.random() * 4)];
                this.collectibles.push({
                    dist: curDist,
                    x: laneX,
                    type: type,
                    color: gearColor,
                    collected: false,
                    rot: Math.random() * Math.PI
                });
            } else {
                // Obstacles
                const obsTypes = ['leaf_brown', 'leaf_green', 'twig', 'bottle_cap'];
                const obsType = obsTypes[Math.floor(Math.random() * obsTypes.length)];
                this.obstacles.push({
                    dist: curDist,
                    x: laneX,
                    type: obsType,
                    size: obsType === 'twig' ? 44 : 26,
                    rot: Math.random() * Math.PI * 2,
                    active: true
                });
            }
        }
    }

    triggerPower(type) {
        if (this.state !== 'racing') return;
        const p = this.powers[type];
        if (!p || !p.ready) return;

        if (type === 'wind') {
            // Vania's Wind Boost
            p.ready = false;
            p.cd = p.maxCd;
            p.active = true;
            this.player.boostTime = p.duration;
            if (window.soundManager) window.soundManager.playWindBoost();
            this.showSpeechBubble("¡Vania: ¡Soplo de Viento a toda marcha!");
            this.spawnWindParticles();
        } else if (type === 'pencil') {
            // Lápiz's Rainbow Bridge & Jump
            p.ready = false;
            p.cd = p.maxCd;
            p.active = true;
            this.player.jumpVz = 18;
            this.player.isJumping = true;
            this.player.bridgeAnimation = {
                progress: 0,
                startX: this.player.x,
                startY: 0
            };
            if (window.soundManager) {
                window.soundManager.playPencilBridge();
                window.soundManager.playJump();
            }
            this.showSpeechBubble("¡Lápiz: ¡Dibujando un gran puente de colores!");
        } else if (type === 'repair') {
            // Tornituerqui's Super Repair / Instant Shield
            p.ready = false;
            p.cd = p.maxCd;
            this.player.shieldTime = 4.0;
            this.player.speed = Math.max(this.player.speed, this.player.baseSpeed);
            if (window.soundManager) window.soundManager.playRepair();
            this.showSpeechBubble("¡Tornituerqui: ¡Clinc-clanc! ¡Barquito como nuevo!");
            this.spawnRepairSparks();
        }

        this.updatePowerUI();
    }

    autoTriggerHelp() {
        // Player 2 smart trigger
        if (this.powers.repair.ready && this.player.speed < this.player.baseSpeed * 0.9) {
            this.triggerPower('repair');
        } else if (this.powers.pencil.ready && this.hasNearbyObstacle()) {
            this.triggerPower('pencil');
        } else if (this.powers.wind.ready) {
            this.triggerPower('wind');
        } else if (this.powers.repair.ready) {
            this.triggerPower('repair');
        }
    }

    hasNearbyObstacle() {
        return this.obstacles.some(
            (o) => o.active && o.dist > this.distance + 40 && o.dist < this.distance + 220 && Math.abs(o.x - this.player.x) < 45
        );
    }

    spawnWindParticles() {
        for (let i = 0; i < 25; i++) {
            this.particles.push({
                x: this.player.x + (Math.random() - 0.5) * 40,
                y: -10 + Math.random() * 20,
                vx: (Math.random() - 0.5) * 60,
                vy: -150 - Math.random() * 120,
                size: 5 + Math.random() * 8,
                color: 'rgba(255, 255, 255, 0.8)',
                life: 0.6 + Math.random() * 0.5,
                maxLife: 1.1,
                isBubble: true
            });
        }
    }

    spawnRepairSparks() {
        for (let i = 0; i < 20; i++) {
            const angle = Math.random() * Math.PI * 2;
            const spd = 60 + Math.random() * 90;
            this.particles.push({
                x: this.player.x + (Math.random() - 0.5) * 20,
                y: (Math.random() - 0.5) * 20,
                vx: Math.cos(angle) * spd,
                vy: Math.sin(angle) * spd,
                size: 4 + Math.random() * 4,
                color: Math.random() < 0.5 ? '#f1c40f' : '#3498db',
                life: 0.4 + Math.random() * 0.4,
                maxLife: 0.8,
                isSpark: true
            });
        }
    }

    spawnWaterSplash(x, y, count = 16) {
        if (window.soundManager) window.soundManager.playSplash();
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const spd = 50 + Math.random() * 80;
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * spd,
                vy: Math.sin(angle) * spd - 30,
                size: 3 + Math.random() * 5,
                color: 'rgba(230, 245, 255, 0.85)',
                life: 0.4 + Math.random() * 0.3,
                maxLife: 0.7,
                isBubble: true
            });
        }
    }

    gameLoop(time) {
        const dt = Math.min((time - this.lastTime) / 1000, 0.1);
        this.lastTime = time;

        if (this.state === 'racing') {
            this.update(dt);
        }

        this.render();

        requestAnimationFrame((t) => this.gameLoop(t));
    }

    update(dt) {
        // Cooldowns update
        for (const key in this.powers) {
            const p = this.powers[key];
            if (!p.ready) {
                p.cd -= dt;
                if (p.cd <= 0) {
                    p.cd = 0;
                    p.ready = true;
                    p.active = false;
                }
            }
        }
        this.updatePowerUI();

        // Player Jump Physics (Lápiz bridge or waterfall ramp)
        if (this.player.isJumping) {
            this.player.jumpZ += this.player.jumpVz * dt * 60;
            this.player.jumpVz -= 28 * dt; // gravity
            if (this.player.jumpZ <= 0) {
                this.player.jumpZ = 0;
                this.player.isJumping = false;
                this.player.jumpVz = 0;
                this.spawnWaterSplash(this.player.x, 30);
            }
        }

        // Bridge animation progress
        if (this.player.bridgeAnimation) {
            this.player.bridgeAnimation.progress += dt * 1.8;
            if (this.player.bridgeAnimation.progress >= 1) {
                this.player.bridgeAnimation = null;
            }
        }

        // Boost & Shield timers
        if (this.player.boostTime > 0) {
            this.player.boostTime -= dt;
            this.player.speed = this.player.maxSpeed;
            // Spawn continuous bubble wake during boost
            if (Math.random() < 0.6) {
                this.particles.push({
                    x: this.player.x + (Math.random() - 0.5) * 25,
                    y: 40,
                    vx: (Math.random() - 0.5) * 30,
                    vy: -120,
                    size: 4 + Math.random() * 6,
                    color: 'rgba(255, 255, 255, 0.75)',
                    life: 0.5,
                    maxLife: 0.5,
                    isBubble: true
                });
            }
        } else {
            // Gentle acceleration / deceleration towards baseSpeed
            const targetSpeed = this.inputs.accelerate ? this.player.baseSpeed * 1.35 : this.player.baseSpeed;
            if (this.player.speed < targetSpeed) {
                this.player.speed += 80 * dt;
            } else if (this.player.speed > targetSpeed) {
                this.player.speed -= 100 * dt;
            }
        }

        if (this.player.shieldTime > 0) {
            this.player.shieldTime -= dt;
        }

        if (this.player.invulnerableTime > 0) {
            this.player.invulnerableTime -= dt;
        }

        // Steer Physics (J1 - Hijo)
        const steerSpeed = 480;
        if (this.inputs.steerLeft) {
            this.player.vx -= steerSpeed * dt * 3.5;
            this.player.tilt = Math.max(this.player.tilt - dt * 4, -0.25);
        } else if (this.inputs.steerRight) {
            this.player.vx += steerSpeed * dt * 3.5;
            this.player.tilt = Math.min(this.player.tilt + dt * 4, 0.25);
        } else {
            this.player.vx *= 0.85;
            this.player.tilt *= 0.88;
        }

        this.player.x += this.player.vx * dt;

        // River Banks collision
        const maxRiverX = this.riverWidth * 0.44 - this.player.width * 0.35;
        if (this.player.x < -maxRiverX) {
            this.player.x = -maxRiverX;
            this.player.vx = Math.abs(this.player.vx) * 0.4;
        } else if (this.player.x > maxRiverX) {
            this.player.x = maxRiverX;
            this.player.vx = -Math.abs(this.player.vx) * 0.4;
        }

        // Advance Race Distance
        this.distance += this.player.speed * dt;

        // Check Waterfalls / Ramps
        this.waterfalls.forEach((wf) => {
            if (Math.abs(this.distance - wf.dist) < 25 && !this.player.isJumping) {
                this.player.isJumping = true;
                this.player.jumpVz = 14;
                if (window.soundManager) window.soundManager.playJump();
                this.showSpeechBubble("¡Pequeño salto de agua! ¡Volando!");
            }
        });

        // Check Obstacle Collisions
        this.obstacles.forEach((obs) => {
            if (!obs.active) return;
            const distDiff = obs.dist - this.distance;
            // Visible collision zone
            if (distDiff > -30 && distDiff < 40) {
                const xDiff = Math.abs(obs.x - this.player.x);
                if (xDiff < (this.player.width * 0.35 + obs.size * 0.5)) {
                    if (this.player.isJumping) {
                        // Successfully leaped over obstacle!
                        return;
                    }

                    if (this.player.boostTime > 0) {
                        // Wind power blows obstacle away
                        obs.active = false;
                        this.spawnWaterSplash(obs.x, 0, 10);
                        return;
                    }

                    if (this.player.shieldTime > 0) {
                        // Tornituerqui shield instant repair
                        obs.active = false;
                        if (window.soundManager) window.soundManager.playRepair();
                        this.spawnRepairSparks();
                        this.showSpeechBubble("¡Tornituerqui bloqueó el golpe!");
                        return;
                    }

                    if (this.player.invulnerableTime <= 0) {
                        // Normal obstacle hit
                        obs.active = false;
                        this.player.speed = Math.max(80, this.player.speed * 0.45);
                        this.player.invulnerableTime = 1.2;
                        if (window.soundManager) window.soundManager.playObstacleHit();
                        this.showSpeechBubble("¡Cuidado con la ramita! ¡Tornituerqui puede repararlo!");

                        // Suggest Tornituerqui power if ready
                        const repairBtn = document.getElementById('btn-power-repair');
                        if (repairBtn && this.powers.repair.ready) {
                            repairBtn.classList.add('pulse-help');
                            setTimeout(() => repairBtn.classList.remove('pulse-help'), 2000);
                        }
                    }
                }
            }
        });

        // Check Collectibles
        this.collectibles.forEach((item) => {
            if (item.collected) return;
            const distDiff = item.dist - this.distance;
            if (distDiff > -30 && distDiff < 40) {
                const xDiff = Math.abs(item.x - this.player.x);
                if (xDiff < (this.player.width * 0.42 + 25)) {
                    item.collected = true;
                    if (item.type === 'star') {
                        this.happyPoints += 10;
                        this.starsCollected++;
                        if (window.soundManager) window.soundManager.playStar();
                    } else if (item.type === 'gear') {
                        this.happyPoints += 15;
                        this.gearsCollected++;
                        if (window.soundManager) window.soundManager.playGear();
                    } else {
                        this.happyPoints += 25;
                        if (window.soundManager) window.soundManager.playStar();
                    }
                    this.saveProgress();
                    this.updateHUD();
                }
            }
        });

        // Update Competitor AI
        this.competitors.forEach((c) => {
            // Friendly rubber-banding: keep competitors near player
            const targetDist = this.distance + (c.id === 'leck' ? -30 : 25) + Math.sin(this.distance * 0.005 + c.speed) * 40;
            c.dist += (targetDist - c.dist) * 0.03 + (c.speed - this.player.baseSpeed) * dt * 0.2;
            c.x += Math.sin(this.distance * 0.008 + (c.id === 'leck' ? 0 : 2)) * dt * 30;
            c.tilt = Math.sin(this.distance * 0.02) * 0.08;
        });

        // Laps & Victory
        const lapProgress = this.distance / this.trackLength;
        const currentLapCalc = Math.min(this.totalLaps, Math.floor(lapProgress) + 1);
        if (currentLapCalc !== this.currentLap) {
            this.currentLap = currentLapCalc;
            this.showSpeechBubble("¡Última vuelta! ¡A darlo todo!");
        }

        if (this.distance >= this.trackLength * this.totalLaps && !this.raceFinished) {
            this.finishRace();
        }

        // Particle updates
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            p.life -= dt;
            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }

        this.updateHUD();
    }

    finishRace() {
        this.raceFinished = true;
        this.state = 'celebration';
        if (window.soundManager) window.soundManager.playWinFanfare();

        // Calculate Position
        let position = 1;
        this.competitors.forEach((c) => {
            if (c.dist > this.distance) position++;
        });

        const victoryScreen = document.getElementById('victory-screen');
        const posText = document.getElementById('victory-position');
        const pointsText = document.getElementById('victory-points');

        if (posText) {
            posText.textContent = position === 1 ? '¡1° Lugar! ¡Campeones del Riachuelo!' : `¡${position}° Lugar! ¡Gran carrera en equipo!`;
        }
        if (pointsText) {
            pointsText.textContent = `Ganaron +${this.starsCollected * 10 + this.gearsCollected * 15} Puntos Felices`;
        }

        document.getElementById('game-hud').classList.add('hidden');
        victoryScreen.classList.remove('hidden');
    }

    showSpeechBubble(text) {
        const bubble = document.getElementById('speech-bubble');
        if (!bubble) return;
        bubble.textContent = text;
        bubble.classList.remove('hidden');
        bubble.classList.add('visible');

        clearTimeout(this.speechTimeout);
        this.speechTimeout = setTimeout(() => {
            bubble.classList.remove('visible');
            bubble.classList.add('hidden');
        }, 3200);
    }

    updatePowerUI() {
        const setBtn = (id, p) => {
            const el = document.getElementById(id);
            if (!el) return;
            const cdOverlay = el.querySelector('.cd-overlay');
            if (p.ready) {
                el.classList.remove('disabled');
                if (cdOverlay) cdOverlay.style.height = '0%';
            } else {
                el.classList.add('disabled');
                if (cdOverlay) {
                    const pct = Math.floor((p.cd / p.maxCd) * 100);
                    cdOverlay.style.height = `${pct}%`;
                }
            }
        };

        setBtn('btn-power-wind', this.powers.wind);
        setBtn('btn-power-pencil', this.powers.pencil);
        setBtn('btn-power-repair', this.powers.repair);
    }

    updateHUD() {
        // Speedometer ratio
        const speedRatio = Math.min(1, Math.max(0, (this.player.speed - 80) / (this.player.maxSpeed - 80)));
        const speedFill = document.getElementById('speed-bar-fill');
        if (speedFill) {
            speedFill.style.width = `${Math.floor(speedRatio * 100)}%`;
        }

        // Lap Display
        const lapText = document.getElementById('lap-counter');
        if (lapText) {
            lapText.textContent = `¡Vuelta ${this.currentLap} de ${this.totalLaps}!`;
        }

        // Happy Points
        const pointsEl = document.getElementById('hud-happy-points');
        if (pointsEl) {
            pointsEl.textContent = this.happyPoints;
        }

        // Mini track position tracker
        const totalDist = this.trackLength * this.totalLaps;
        const playerProg = Math.min(1, this.distance / totalDist);
        const iconPlayer = document.getElementById('track-icon-player');
        if (iconPlayer) {
            iconPlayer.style.left = `${playerProg * 85 + 5}%`;
        }

        this.competitors.forEach((c) => {
            const icon = document.getElementById(`track-icon-${c.id}`);
            if (icon) {
                const prog = Math.min(1, Math.max(0, c.dist / totalDist));
                icon.style.left = `${prog * 85 + 5}%`;
            }
        });
    }

    saveProgress() {
        localStorage.setItem('vania_happy_points', this.happyPoints.toString());
        localStorage.setItem('vania_skin', this.selectedSkin);
        localStorage.setItem('vania_hat', this.selectedHat);
        localStorage.setItem('vania_unlocked_skins', JSON.stringify(this.unlockedSkins));
        localStorage.setItem('vania_unlocked_hats', JSON.stringify(this.unlockedHats));
    }

    render() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.clearRect(0, 0, 0, 0);

        // 1. Sky and Distant Scenery
        this.renderBackground(ctx, w, h);

        // 2. 3D Flowing River, Curbs & Sidewalks (Using full screen width)
        this.renderRiver(ctx, w, h);

        // 3. Build Depth-Sorted Entity Queue (Back-to-Front)
        const renderQueue = [];

        // Waterfalls / Sidewalk Drop Ramps
        this.waterfalls.forEach((wf) => {
            const proj = this.project(0, wf.dist, 0);
            if (proj && proj.screenY > -50 && proj.screenY < h + 100) {
                renderQueue.push({
                    dist: wf.dist,
                    type: 'waterfall',
                    proj: proj,
                    wf: wf
                });
            }
        });

        // Collectibles
        this.collectibles.forEach((item) => {
            if (item.collected) return;
            const proj = this.project(item.x, item.dist, 8);
            if (proj && proj.screenY > -50 && proj.screenY < h + 100) {
                renderQueue.push({
                    dist: item.dist,
                    type: 'collectible',
                    proj: proj,
                    item: item
                });
            }
        });

        // Obstacles
        this.obstacles.forEach((obs) => {
            if (!obs.active) return;
            const proj = this.project(obs.x, obs.dist, 0);
            if (proj && proj.screenY > -50 && proj.screenY < h + 100) {
                renderQueue.push({
                    dist: obs.dist,
                    type: 'obstacle',
                    proj: proj,
                    obs: obs
                });
            }
        });

        // Competitors
        this.competitors.forEach((c) => {
            const proj = this.project(c.x, c.dist, 0);
            if (proj && proj.screenY > -80 && proj.screenY < h + 120) {
                renderQueue.push({
                    dist: c.dist,
                    type: 'competitor',
                    proj: proj,
                    comp: c
                });
            }
        });

        // Player Boat
        const playerProj = this.project(this.player.x, this.distance, this.player.jumpZ);
        if (playerProj) {
            renderQueue.push({
                dist: this.distance,
                type: 'player',
                proj: playerProj
            });
        }

        // Rainbow Bridge Power Animation
        if (this.player.bridgeAnimation) {
            const b = this.player.bridgeAnimation;
            const startProj = this.project(b.startX, this.distance - 20, 0);
            const endProj = this.project(b.startX, this.distance + 240, 20);
            if (startProj && endProj) {
                Sprites.drawRainbowBridge(ctx, startProj.screenX, startProj.screenY, endProj.screenX, endProj.screenY, b.progress);
            }
        }

        // Sort entities from furthest (largest dist) to closest (smallest dist)
        renderQueue.sort((a, b) => b.dist - a.dist);

        // Render each entity in 3D perspective
        renderQueue.forEach((entity) => {
            const { type, proj } = entity;
            const s = proj.scale;

            switch (type) {
                case 'waterfall':
                    this.renderWaterfallStep(ctx, proj.screenX, proj.screenY, proj.riverSpan, s);
                    break;

                case 'collectible': {
                    const item = entity.item;
                    const rot = item.rot + this.distance * 0.02;
                    const itemSize = 22 * s;
                    if (item.type === 'star') {
                        Sprites.drawStar(ctx, proj.screenX, proj.screenY, itemSize, rot);
                    } else if (item.type === 'gear') {
                        Sprites.drawGear(ctx, proj.screenX, proj.screenY, itemSize * 0.9, item.color, rot);
                    } else {
                        Sprites.drawLollipop(ctx, proj.screenX, proj.screenY, itemSize * 0.85, rot);
                    }
                    break;
                }

                case 'obstacle': {
                    const obs = entity.obs;
                    const obsSize = obs.size * s * 1.25;
                    if (obs.type === 'leaf_brown') {
                        Sprites.drawLeaf(ctx, proj.screenX, proj.screenY, obsSize, false, obs.rot);
                    } else if (obs.type === 'leaf_green') {
                        Sprites.drawLeaf(ctx, proj.screenX, proj.screenY, obsSize, true, obs.rot);
                    } else if (obs.type === 'twig') {
                        Sprites.drawTwig(ctx, proj.screenX, proj.screenY, obsSize * 1.2, obs.rot);
                    } else if (obs.type === 'bottle_cap') {
                        Sprites.drawBottleCap(ctx, proj.screenX, proj.screenY, 18 * s);
                    }
                    break;
                }

                case 'competitor': {
                    const c = entity.comp;
                    const compW = c.width * s * 1.15;
                    const compH = c.height * s * 1.15;
                    if (c.type === 'carton') {
                        Sprites.drawMilkCartonBoat(ctx, proj.screenX, proj.screenY, compW, compH, c.tilt);
                    } else {
                        Sprites.drawSodaCanBoat(ctx, proj.screenX, proj.screenY, compW, compH, c.tilt);
                    }
                    break;
                }

                case 'player': {
                    const pW = this.player.width * s * 1.35;
                    const pH = this.player.height * s * 1.35;

                    // 3D Water shadow beneath boat
                    ctx.save();
                    ctx.beginPath();
                    ctx.ellipse(proj.screenX, proj.screenY + pH * 0.35, pW * 0.46, pH * 0.18, 0, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(10, 35, 65, 0.38)';
                    ctx.filter = 'blur(4px)';
                    ctx.fill();
                    ctx.restore();

                    // Render Boat with active accessories
                    Sprites.drawBoat(ctx, proj.screenX, proj.screenY, pW, pH, {
                        tilt: this.player.tilt,
                        palette: this.selectedSkin,
                        hat: this.selectedHat,
                        jumping: this.player.isJumping,
                        scaleY: 1 + this.player.jumpZ * 0.004,
                        isBoosted: this.player.boostTime > 0,
                        isShielded: this.player.shieldTime > 0,
                        invulnerable: this.player.invulnerableTime > 0
                    });

                    // 3D Water V-shaped wake ripples
                    if (!this.player.isJumping) {
                        ctx.save();
                        ctx.beginPath();
                        ctx.ellipse(proj.screenX, proj.screenY + pH * 0.32, pW * 0.52 + Math.sin(Date.now() * 0.01) * 4, 10 * s, 0, 0, Math.PI * 2);
                        ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
                        ctx.lineWidth = 3 * s;
                        ctx.stroke();

                        // Stern wake foam lines
                        ctx.beginPath();
                        ctx.moveTo(proj.screenX - pW * 0.25, proj.screenY + pH * 0.3);
                        ctx.lineTo(proj.screenX - pW * 0.65, proj.screenY + pH * 0.45);
                        ctx.moveTo(proj.screenX + pW * 0.25, proj.screenY + pH * 0.3);
                        ctx.lineTo(proj.screenX + pW * 0.65, proj.screenY + pH * 0.45);
                        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                        ctx.lineWidth = 2.5 * s;
                        ctx.stroke();
                        ctx.restore();
                    }
                    break;
                }
            }
        });

        // 4. Particles (Bubbles, Sparks, Foams)
        this.particles.forEach((p) => {
            const proj = this.project(p.x, this.distance + p.y, 0);
            if (proj) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(proj.screenX, proj.screenY, p.size * (p.life / p.maxLife) * proj.scale * 1.2, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
                ctx.restore();
            }
        });

        // 5. Rain & Weather Overlays
        this.renderRain(ctx, w, h);
    }

    renderBackground(ctx, w, h) {
        const horizonY = h * 0.26;

        // Sky with rainy atmospheric gradient
        const skyGrad = ctx.createLinearGradient(0, 0, 0, horizonY);
        skyGrad.addColorStop(0, '#5dade2');
        skyGrad.addColorStop(0.5, '#aed6f1');
        skyGrad.addColorStop(1, '#ebf5fb');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, w, horizonY + 2);

        // Distant Rainbow Arc
        ctx.save();
        ctx.beginPath();
        ctx.arc(w * 0.52, horizonY * 1.5, w * 0.46, Math.PI * 1.15, Math.PI * 1.85);
        const rainbowColors = [
            'rgba(231, 76, 60, 0.28)',
            'rgba(243, 156, 18, 0.28)',
            'rgba(241, 196, 15, 0.28)',
            'rgba(46, 204, 113, 0.28)',
            'rgba(52, 152, 219, 0.28)',
            'rgba(155, 89, 182, 0.28)'
        ];
        rainbowColors.forEach((col, idx) => {
            ctx.strokeStyle = col;
            ctx.lineWidth = 7;
            ctx.stroke();
        });
        ctx.restore();

        // Distant Cozy Storybook Houses on Horizon
        ctx.save();
        const houseColors = ['#f39c12', '#e74c3c', '#3498db', '#9b59b6', '#2ecc71'];
        for (let i = 0; i < 9; i++) {
            const hx = (i * (w / 8.5)) - 10;
            const hw = w * 0.07;
            const hh = 30 + (i % 3) * 12;
            const hy = horizonY - hh + 6;

            // House walls
            ctx.fillStyle = houseColors[i % houseColors.length];
            ctx.fillRect(hx, hy + 12, hw, hh - 12);

            // Roof
            ctx.beginPath();
            ctx.moveTo(hx - 4, hy + 12);
            ctx.lineTo(hx + hw * 0.5, hy);
            ctx.lineTo(hx + hw + 4, hy + 12);
            ctx.closePath();
            ctx.fillStyle = '#8e44ad';
            ctx.fill();

            // Window
            ctx.fillStyle = '#fef9e7';
            ctx.fillRect(hx + hw * 0.35, hy + 18, hw * 0.3, 8);
        }
        ctx.restore();
    }

    renderRiver(ctx, w, h) {
        const horizonY = h * 0.26;
        const slices = 44;
        const sliceH = (h - horizonY) / slices;

        // Render each 3D slice from horizon to bottom of screen
        for (let i = 0; i < slices; i++) {
            const y0 = horizonY + i * sliceH;
            const y1 = y0 + sliceH + 0.8;

            // Perspective factor (0 at horizon, 1 at screen bottom)
            const p0 = (y0 - horizonY) / (h - horizonY);
            const p1 = (y1 - horizonY) / (h - horizonY);

            // Distance along track for these scanlines
            const invP0 = Math.max(0.01, Math.pow(p0, 1.14));
            const invP1 = Math.max(0.01, Math.pow(p1, 1.14));

            const worldDist0 = this.distance + (1 - invP0) * 1100;
            const worldDist1 = this.distance + (1 - invP1) * 1100;

            const curve0 = Math.sin(worldDist0 * 0.0016) * (65 * invP0);
            const curve1 = Math.sin(worldDist1 * 0.0016) * (65 * invP1);

            const centerX0 = (w * 0.5) + curve0;
            const centerX1 = (w * 0.5) + curve1;

            // River width utilizing the full screen width at foreground
            const rw0 = (w * (0.22 + 0.70 * p0)) * 0.5;
            const rw1 = (w * (0.22 + 0.70 * p1)) * 0.5;

            const curbWidth0 = 26 * (0.3 + 0.7 * p0);
            const curbWidth1 = 26 * (0.3 + 0.7 * p1);

            // Left River Bank: Sidewalk / Grass Lawn
            ctx.fillStyle = (i % 2 === 0) ? '#48c774' : '#3ec46d';
            ctx.beginPath();
            ctx.moveTo(0, y0);
            ctx.lineTo(centerX0 - rw0 - curbWidth0, y0);
            ctx.lineTo(centerX1 - rw1 - curbWidth1, y1);
            ctx.lineTo(0, y1);
            ctx.closePath();
            ctx.fill();

            // Right River Bank: Wet Asphalt Road
            ctx.fillStyle = (i % 2 === 0) ? '#4a5568' : '#455060';
            ctx.beginPath();
            ctx.moveTo(centerX0 + rw0 + curbWidth0, y0);
            ctx.lineTo(w, y0);
            ctx.lineTo(w, y1);
            ctx.lineTo(centerX1 + rw1 + curbWidth1, y1);
            ctx.closePath();
            ctx.fill();

            // Road rain gloss sheen
            ctx.fillStyle = 'rgba(174, 214, 241, 0.12)';
            ctx.fillRect(centerX0 + rw0 + curbWidth0, y0, w, sliceH);

            // 3D Left Concrete Curb Top
            ctx.fillStyle = '#a0aec0';
            ctx.beginPath();
            ctx.moveTo(centerX0 - rw0 - curbWidth0, y0);
            ctx.lineTo(centerX0 - rw0, y0);
            ctx.lineTo(centerX1 - rw1, y1);
            ctx.lineTo(centerX1 - rw1 - curbWidth1, y1);
            ctx.closePath();
            ctx.fill();

            // 3D Left Curb Vertical Drop Face (Drop into river)
            ctx.fillStyle = '#4a5568';
            ctx.beginPath();
            ctx.moveTo(centerX0 - rw0, y0);
            ctx.lineTo(centerX0 - rw0 + 4, y0);
            ctx.lineTo(centerX1 - rw1 + 4, y1);
            ctx.lineTo(centerX1 - rw1, y1);
            ctx.closePath();
            ctx.fill();

            // 3D Right Concrete Curb Top
            ctx.fillStyle = '#a0aec0';
            ctx.beginPath();
            ctx.moveTo(centerX0 + rw0, y0);
            ctx.lineTo(centerX0 + rw0 + curbWidth0, y0);
            ctx.lineTo(centerX1 + rw1 + curbWidth1, y1);
            ctx.lineTo(centerX1 + rw1, y1);
            ctx.closePath();
            ctx.fill();

            // 3D Right Curb Vertical Drop Face
            ctx.fillStyle = '#4a5568';
            ctx.beginPath();
            ctx.moveTo(centerX0 + rw0 - 4, y0);
            ctx.lineTo(centerX0 + rw0, y0);
            ctx.lineTo(centerX1 + rw1, y1);
            ctx.lineTo(centerX1 + rw1 - 4, y1);
            ctx.closePath();
            ctx.fill();

            // Flowing Water Surface Polygon
            const waterHue = 200 + Math.floor(p0 * 10);
            const waterLightness = 32 + Math.floor(p0 * 20);
            ctx.fillStyle = `hsl(${waterHue}, 75%, ${waterLightness}%)`;

            ctx.beginPath();
            ctx.moveTo(centerX0 - rw0, y0);
            ctx.lineTo(centerX0 + rw0, y0);
            ctx.lineTo(centerX1 + rw1, y1);
            ctx.lineTo(centerX1 - rw1, y1);
            ctx.closePath();
            ctx.fill();

            // Perspective Water Ripples and Wave Crests
            const waveOffset = ((worldDist0 * 0.9) % 90);
            if (waveOffset < 14) {
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.15 + 0.35 * p0})`;
                ctx.lineWidth = 1.5 + 2 * p0;
                ctx.beginPath();
                ctx.moveTo(centerX0 - rw0 * 0.85, y0);
                ctx.quadraticCurveTo(centerX0, y0 - 3 * p0, centerX0 + rw0 * 0.85, y0);
                ctx.stroke();
            }
        }
    }

    renderWaterfallStep(ctx, centerX, screenY, rw, scale) {
        const left = centerX - rw * 0.48;
        const w = rw * 0.96;
        const h = 16 * scale;

        // Concrete step drop
        ctx.fillStyle = '#2d3748';
        ctx.fillRect(left, screenY - 4 * scale, w, h * 0.7);

        // Foaming rapid splash line
        ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
        ctx.fillRect(left, screenY + 2 * scale, w, h);

        // Froth bubbles
        for (let i = 0; i < 22; i++) {
            ctx.beginPath();
            const fx = left + (i * w) / 22;
            const fy = screenY + 6 * scale + Math.sin(i * 1.5 + Date.now() * 0.01) * (3 * scale);
            ctx.arc(fx, fy, 4 * scale, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    renderRain(ctx, w, h) {
        ctx.save();
        ctx.strokeStyle = 'rgba(214, 234, 248, 0.4)';
        ctx.lineWidth = 1.5;
        const time = Date.now() * 0.0035;
        for (let i = 0; i < 60; i++) {
            const rx = (i * 41 + time * 160) % w;
            const ry = (i * 67 + time * 720) % h;
            ctx.beginPath();
            ctx.moveTo(rx, ry);
            ctx.lineTo(rx - 5, ry + 22);
            ctx.stroke();
        }
        ctx.restore();
    }

    renderRain(ctx, w, h) {
        ctx.save();
        ctx.strokeStyle = 'rgba(200, 230, 255, 0.35)';
        ctx.lineWidth = 1.2;
        const time = Date.now() * 0.003;
        for (let i = 0; i < 50; i++) {
            const rx = (i * 37 + time * 140) % w;
            const ry = (i * 59 + time * 650) % h;
            ctx.beginPath();
            ctx.moveTo(rx, ry);
            ctx.lineTo(rx - 4, ry + 16);
            ctx.stroke();
        }
        ctx.restore();
    }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
    window.game = new VaniaBoatGame();
});
