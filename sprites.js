// High-detail procedural sprite renderer for "La Gran Carrera del Barquito de Vania"
const Sprites = {
    // Color palettes for boat customizations
    boatPalettes: {
        rainbow: ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6'],
        sunset: ['#d35400', '#e67e22', '#f39c12', '#f1c40f', '#e74c3c'],
        ocean: ['#1b4f72', '#2874a6', '#3498db', '#5dade2', '#aed6f1'],
        emerald: ['#145a32', '#1e8449', '#27ae60', '#52be80', '#a9dfbf'],
        pirate: ['#3e2723', '#4e342e', '#5d4037', '#6d4c41', '#8d6e63']
    },

    drawBoat(ctx, x, y, width, height, options = {}) {
        const {
            tilt = 0,
            palette = 'rainbow',
            hat = 'none',
            jumping = false,
            scaleY = 1,
            isBoosted = false,
            isShielded = false,
            invulnerable = false
        } = options;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(tilt);

        if (jumping) {
            ctx.scale(1.15, 1.15 * scaleY);
        }

        // Shield glow if active
        if (isShielded) {
            ctx.save();
            ctx.beginPath();
            ctx.ellipse(0, 0, width * 0.75, height * 0.65, 0, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(52, 152, 219, 0.25)';
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 4;
            ctx.setLineDash([8, 6]);
            ctx.stroke();
            ctx.fill();
            ctx.restore();
        }

        // Flashing if invulnerable after hit
        if (invulnerable && Math.floor(Date.now() / 100) % 2 === 0) {
            ctx.globalAlpha = 0.5;
        }

        const colors = this.boatPalettes[palette] || this.boatPalettes.rainbow;

        // Shadow under boat in water
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(2, height * 0.38, width * 0.52, height * 0.28, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(10, 45, 75, 0.35)';
        ctx.filter = 'blur(4px)';
        ctx.fill();
        ctx.restore();

        // Boat Hull (Layered rainbow wood planks)
        const stripeCount = colors.length;
        const stripeH = (height * 0.45) / stripeCount;
        const hullTop = height * 0.05;

        // Base wooden outer hull
        ctx.beginPath();
        ctx.ellipse(0, hullTop + height * 0.2, width * 0.48, height * 0.25, 0, 0, Math.PI);
        ctx.fillStyle = '#8b5a2b';
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#5a3818';
        ctx.stroke();

        // Hull colored stripes
        for (let i = 0; i < stripeCount; i++) {
            ctx.beginPath();
            const yOffset = hullTop + i * stripeH;
            const progress = (i + 1) / stripeCount;
            const rx = width * 0.47 * (1 - progress * 0.18);
            const ry = height * 0.24 * (1 - progress * 0.12);

            ctx.ellipse(0, yOffset, rx, ry, 0, 0, Math.PI);
            ctx.fillStyle = colors[i];
            ctx.fill();
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = 'rgba(0,0,0,0.15)';
            ctx.stroke();
        }

        // Boat deck (inside rim)
        ctx.beginPath();
        ctx.ellipse(0, hullTop, width * 0.44, height * 0.15, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#e5b887';
        ctx.fill();
        ctx.strokeStyle = '#a67244';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Inner shadow of deck
        ctx.beginPath();
        ctx.ellipse(0, hullTop + 2, width * 0.4, height * 0.12, 0, 0, Math.PI);
        ctx.fillStyle = 'rgba(80, 50, 20, 0.22)';
        ctx.fill();

        // Mast & Sail
        const mastX = -width * 0.05;
        const mastTop = -height * 0.6;
        ctx.beginPath();
        ctx.moveTo(mastX, hullTop + 5);
        ctx.lineTo(mastX, mastTop);
        ctx.strokeStyle = '#c68a4c';
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.stroke();

        // White/Cream Triangular Sail
        ctx.beginPath();
        ctx.moveTo(mastX + 2, mastTop + 10);
        ctx.quadraticCurveTo(mastX + width * 0.35, mastTop + height * 0.32, mastX + 2, hullTop - 8);
        ctx.closePath();
        ctx.fillStyle = '#fdfbf7';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#3498db';
        ctx.stroke();

        // Sail shadow / accent stripe
        ctx.beginPath();
        ctx.moveTo(mastX + 2, mastTop + 12);
        ctx.lineTo(mastX + width * 0.12, mastTop + height * 0.25);
        ctx.lineTo(mastX + 2, hullTop - 12);
        ctx.fillStyle = 'rgba(52, 152, 219, 0.18)';
        ctx.fill();

        // Red pennant flag on mast top
        ctx.beginPath();
        ctx.moveTo(mastX, mastTop);
        ctx.lineTo(mastX + width * 0.25, mastTop + 8);
        ctx.lineTo(mastX, mastTop + 16);
        ctx.closePath();
        ctx.fillStyle = '#e74c3c';
        ctx.fill();
        ctx.strokeStyle = '#c0392b';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Steering Wheel
        const charScale = width / 76;
        const wheelX = width * 0.16;
        const wheelY = hullTop - 2;
        ctx.save();
        ctx.translate(wheelX, wheelY);
        ctx.rotate(tilt * 3);
        ctx.beginPath();
        ctx.arc(0, 0, 11 * charScale, 0, Math.PI * 2);
        ctx.strokeStyle = '#8b5a2b';
        ctx.lineWidth = 3 * charScale;
        ctx.stroke();
        // Spokes
        for (let a = 0; a < 6; a++) {
            const rad = (a * Math.PI) / 3;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.cos(rad) * 14 * charScale, Math.sin(rad) * 14 * charScale);
            ctx.strokeStyle = '#8b5a2b';
            ctx.lineWidth = 2 * charScale;
            ctx.stroke();
        }
        ctx.beginPath();
        ctx.arc(0, 0, 4 * charScale, 0, Math.PI * 2);
        ctx.fillStyle = '#f39c12';
        ctx.fill();
        ctx.restore();

        // CHARACTERS:
        // 1. Vania (Boy at the wheel)
        this.drawVania(ctx, width * 0.18, hullTop - 22 * charScale, 0.85 * charScale);

        // 2. Lápiz (Pencil friend leaning on front bow)
        this.drawLapiz(ctx, -width * 0.24, hullTop - 14 * charScale, 0.8 * charScale);

        // 3. Tornituerqui (Robot friend holding wrench)
        this.drawTornituerqui(ctx, width * 0.28, hullTop - 8 * charScale, 0.75 * charScale);

        // Hat on Vania if selected
        if (hat && hat !== 'none') {
            this.drawHat(ctx, width * 0.18, hullTop - 44 * charScale, hat, charScale);
        }

        ctx.restore();
    },

    drawVania(ctx, x, y, scale = 1) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);

        // Brown Hair back
        ctx.beginPath();
        ctx.ellipse(0, -6, 16, 17, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#6e3c15';
        ctx.fill();

        // Face
        ctx.beginPath();
        ctx.arc(0, 0, 14, 0, Math.PI * 2);
        ctx.fillStyle = '#ffdfba';
        ctx.fill();

        // Hair front tuft / fringe
        ctx.beginPath();
        ctx.moveTo(-14, -6);
        ctx.quadraticCurveTo(-4, -18, 12, -10);
        ctx.quadraticCurveTo(8, -4, 14, -2);
        ctx.quadraticCurveTo(0, -10, -14, -6);
        ctx.fillStyle = '#552c0e';
        ctx.fill();

        // Cheerful Eyes
        ctx.beginPath();
        ctx.arc(-4, -1, 2.5, 0, Math.PI * 2);
        ctx.arc(6, -1, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = '#2c1810';
        ctx.fill();
        // Eye twinkle
        ctx.beginPath();
        ctx.arc(-5, -2, 1, 0, Math.PI * 2);
        ctx.arc(5, -2, 1, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

        // Rosy Cheeks
        ctx.beginPath();
        ctx.arc(-7, 4, 3, 0, Math.PI * 2);
        ctx.arc(9, 4, 3, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(231, 76, 60, 0.4)';
        ctx.fill();

        // Big Happy Smile
        ctx.beginPath();
        ctx.arc(1, 3, 6, 0.15 * Math.PI, 0.85 * Math.PI);
        ctx.strokeStyle = '#c0392b';
        ctx.lineWidth = 1.8;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Striped shirt & Overalls
        ctx.beginPath();
        ctx.rect(-10, 14, 20, 14);
        ctx.fillStyle = '#3498db'; // blue denim overalls
        ctx.fill();

        // Yellow striped shirt sleeves
        ctx.beginPath();
        ctx.arc(-11, 17, 4, 0, Math.PI * 2);
        ctx.arc(11, 17, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#f1c40f';
        ctx.fill();

        ctx.restore();
    },

    drawLapiz(ctx, x, y, scale = 1) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);
        ctx.rotate(-0.15);

        // Pencil Body (Hexagonal yellow wood)
        ctx.beginPath();
        ctx.rect(-6, -15, 12, 28);
        ctx.fillStyle = '#f1c40f';
        ctx.fill();
        ctx.strokeStyle = '#d4ac0d';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Darker stripe for 3D bevel
        ctx.fillStyle = '#d4ac0d';
        ctx.fillRect(-2, -15, 4, 28);

        // Sharpened cone top
        ctx.beginPath();
        ctx.moveTo(-6, -15);
        ctx.lineTo(0, -32);
        ctx.lineTo(6, -15);
        ctx.closePath();
        ctx.fillStyle = '#fce5cd';
        ctx.fill();
        ctx.strokeStyle = '#d5a6bd';
        ctx.stroke();

        // Graphite lead tip
        ctx.beginPath();
        ctx.moveTo(-2.5, -26);
        ctx.lineTo(0, -32);
        ctx.lineTo(2.5, -26);
        ctx.closePath();
        ctx.fillStyle = '#2c3e50';
        ctx.fill();

        // Pencil cartoon eyes
        ctx.beginPath();
        ctx.arc(-2, -4, 2, 0, Math.PI * 2);
        ctx.arc(3, -4, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#2c3e50';
        ctx.fill();

        // Pencil smile
        ctx.beginPath();
        ctx.arc(0, 1, 3, 0.1 * Math.PI, 0.9 * Math.PI);
        ctx.strokeStyle = '#7f8c8d';
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // Pencil stick arm pointing forward
        ctx.beginPath();
        ctx.moveTo(-6, 2);
        ctx.lineTo(-15, -4);
        ctx.lineTo(-20, -10);
        ctx.strokeStyle = '#b7950b';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.restore();
    },

    drawTornituerqui(ctx, x, y, scale = 1) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);
        ctx.rotate(0.12);

        // Robot Head (Silver metallic dome)
        ctx.beginPath();
        ctx.arc(0, -8, 11, 0, Math.PI * 2);
        const grad = ctx.createLinearGradient(-10, -18, 10, 0);
        grad.addColorStop(0, '#ecf0f1');
        grad.addColorStop(0.5, '#bdc3c7');
        grad.addColorStop(1, '#7f8c8d');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = '#566573';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Nut / Screw ears
        ctx.fillStyle = '#95a5a6';
        ctx.fillRect(-14, -11, 3, 6);
        ctx.fillRect(11, -11, 3, 6);

        // Antenna with glowing blue bulb
        ctx.beginPath();
        ctx.moveTo(0, -19);
        ctx.lineTo(0, -26);
        ctx.strokeStyle = '#7f8c8d';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(0, -28, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#00e5ff';
        ctx.fill();

        // Robot friendly eyes
        ctx.beginPath();
        ctx.arc(-4, -8, 2.8, 0, Math.PI * 2);
        ctx.arc(4, -8, 2.8, 0, Math.PI * 2);
        ctx.fillStyle = '#34495e';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(-3.5, -8.5, 1, 0, Math.PI * 2);
        ctx.arc(4.5, -8.5, 1, 0, Math.PI * 2);
        ctx.fillStyle = '#00f0ff';
        ctx.fill();

        // Robot grill smile
        ctx.beginPath();
        ctx.roundRect(-5, -2, 10, 3, 1.5);
        ctx.fillStyle = '#2c3e50';
        ctx.fill();

        // Robot body
        ctx.beginPath();
        ctx.rect(-8, 3, 16, 12);
        ctx.fillStyle = '#95a5a6';
        ctx.fill();
        ctx.strokeStyle = '#566573';
        ctx.stroke();

        // Hand holding little wrench
        ctx.save();
        ctx.translate(11, 6);
        ctx.rotate(-0.5);
        ctx.fillStyle = '#34495e';
        ctx.fillRect(-2, -8, 4, 16);
        // Wrench head
        ctx.beginPath();
        ctx.arc(0, -8, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#2c3e50';
        ctx.fill();
        ctx.restore();

        ctx.restore();
    },

    drawHat(ctx, x, y, type, scale = 1) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);

        switch (type) {
            case 'captain':
                // Navy blue captain cap with gold anchor/trim
                ctx.beginPath();
                ctx.ellipse(0, 4, 15, 6, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#1c2833';
                ctx.fill();
                // Crown
                ctx.beginPath();
                ctx.rect(-10, -6, 20, 10);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                ctx.strokeStyle = '#1c2833';
                ctx.lineWidth = 1;
                ctx.stroke();
                // Gold band
                ctx.fillStyle = '#f1c40f';
                ctx.fillRect(-10, 1, 20, 3);
                // Visor
                ctx.beginPath();
                ctx.ellipse(0, 6, 12, 3, 0, 0, Math.PI);
                ctx.fillStyle = '#0e171d';
                ctx.fill();
                break;

            case 'party':
                // Colorful party cone
                ctx.beginPath();
                ctx.moveTo(-9, 4);
                ctx.lineTo(0, -22);
                ctx.lineTo(9, 4);
                ctx.closePath();
                ctx.fillStyle = '#e91e63';
                ctx.fill();
                // Polka dots
                ctx.fillStyle = '#f1c40f';
                ctx.beginPath();
                ctx.arc(-2, -6, 2, 0, Math.PI * 2);
                ctx.arc(3, -12, 1.8, 0, Math.PI * 2);
                ctx.fill();
                // Pom-pom on top
                ctx.beginPath();
                ctx.arc(0, -23, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = '#00e5ff';
                ctx.fill();
                break;

            case 'crown':
                // Royal gold crown
                ctx.beginPath();
                ctx.moveTo(-11, 4);
                ctx.lineTo(-11, -8);
                ctx.lineTo(-6, -2);
                ctx.lineTo(0, -11);
                ctx.lineTo(6, -2);
                ctx.lineTo(11, -8);
                ctx.lineTo(11, 4);
                ctx.closePath();
                ctx.fillStyle = '#f39c12';
                ctx.fill();
                ctx.strokeStyle = '#d68910';
                ctx.lineWidth = 1.5;
                ctx.stroke();
                // Jewels
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(-1, 0, 3, 3);
                ctx.fillStyle = '#3498db';
                ctx.fillRect(-8, 0, 3, 3);
                ctx.fillRect(6, 0, 3, 3);
                break;

            case 'propeller':
                // Colorful propeller beanie
                ctx.beginPath();
                ctx.arc(0, 2, 11, Math.PI, 0);
                ctx.fillStyle = '#3498db';
                ctx.fill();
                // Propeller shaft
                ctx.beginPath();
                ctx.moveTo(0, -9);
                ctx.lineTo(0, -17);
                ctx.strokeStyle = '#e74c3c';
                ctx.lineWidth = 2;
                ctx.stroke();
                // Spinning blades
                const spin = Date.now() * 0.01;
                ctx.save();
                ctx.translate(0, -17);
                ctx.rotate(spin);
                ctx.beginPath();
                ctx.ellipse(0, 0, 10, 2.5, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#f1c40f';
                ctx.fill();
                ctx.restore();
                break;

            case 'straw':
                // Summer straw sunhat
                ctx.beginPath();
                ctx.ellipse(0, 4, 18, 7, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#eedc82';
                ctx.fill();
                ctx.strokeStyle = '#c5a059';
                ctx.lineWidth = 1.5;
                ctx.stroke();
                // Cap dome
                ctx.beginPath();
                ctx.ellipse(0, 0, 10, 7, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#eedc82';
                ctx.fill();
                // Red ribbon band
                ctx.fillStyle = '#e74c3c';
                ctx.fillRect(-10, 1, 20, 2.5);
                break;
        }

        ctx.restore();
    },

    drawMilkCartonBoat(ctx, x, y, width, height, tilt = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(tilt);

        // Wooden raft base
        ctx.fillStyle = '#8b5a2b';
        ctx.fillRect(-width * 0.45, height * 0.15, width * 0.9, height * 0.18);
        ctx.strokeStyle = '#5c3a1e';
        ctx.strokeRect(-width * 0.45, height * 0.15, width * 0.9, height * 0.18);

        // Milk carton body
        const cartonScale = width / 60;
        ctx.save();
        ctx.translate(-width * 0.15, -height * 0.15);
        ctx.scale(cartonScale, cartonScale);
        ctx.beginPath();
        ctx.rect(-18, -25, 36, 42);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#bdc3c7';
        ctx.stroke();

        // Blue lower half of carton
        ctx.fillStyle = '#2980b9';
        ctx.fillRect(-18, -4, 36, 21);

        // "LECK" label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 9px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('LECK', 0, 10);

        // Gable top
        ctx.beginPath();
        ctx.moveTo(-18, -25);
        ctx.lineTo(0, -36);
        ctx.lineTo(18, -25);
        ctx.closePath();
        ctx.fillStyle = '#ecf0f1';
        ctx.fill();
        ctx.stroke();

        // Spout ridge
        ctx.fillStyle = '#3498db';
        ctx.fillRect(-3, -39, 6, 5);
        ctx.restore();

        // Little toothpick flag
        ctx.beginPath();
        ctx.moveTo(width * 0.25, height * 0.15);
        ctx.lineTo(width * 0.25, -height * 0.4);
        ctx.strokeStyle = '#d4ac0d';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(width * 0.25, -height * 0.4);
        ctx.lineTo(width * 0.45, -height * 0.32);
        ctx.lineTo(width * 0.25, -height * 0.24);
        ctx.closePath();
        ctx.fillStyle = '#27ae60';
        ctx.fill();

        ctx.restore();
    },

    drawSodaCanBoat(ctx, x, y, width, height, tilt = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(tilt);

        // Wooden pontoons
        ctx.fillStyle = '#a0522d';
        ctx.fillRect(-width * 0.48, height * 0.18, width * 0.96, height * 0.15);

        // Cylinder Soda Can lying horizontally
        ctx.save();
        ctx.translate(0, -height * 0.05);

        // Can cylinder body with rainbow stripes
        const canW = width * 0.72;
        const canH = height * 0.38;
        const rainbow = ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6'];
        const sliceW = canW / rainbow.length;

        for (let i = 0; i < rainbow.length; i++) {
            ctx.fillStyle = rainbow[i];
            ctx.fillRect(-canW / 2 + i * sliceW, -canH / 2, sliceW, canH);
        }

        // Metallic sheen overlay
        const canGrad = ctx.createLinearGradient(0, -canH / 2, 0, canH / 2);
        canGrad.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
        canGrad.addColorStop(0.3, 'rgba(255, 255, 255, 0.0)');
        canGrad.addColorStop(0.8, 'rgba(0, 0, 0, 0.2)');
        ctx.fillStyle = canGrad;
        ctx.fillRect(-canW / 2, -canH / 2, canW, canH);

        // Rim / Can top (silver ellipse on right)
        ctx.beginPath();
        ctx.ellipse(canW / 2, 0, 7, canH / 2, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#bdc3c7';
        ctx.fill();
        ctx.strokeStyle = '#7f8c8d';
        ctx.stroke();

        // Pull tab
        ctx.beginPath();
        ctx.arc(canW / 2, 0, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#2c3e50';
        ctx.fill();

        ctx.restore();
        ctx.restore();
    },

    drawLeaf(ctx, x, y, size = 26, isGreen = false, rotation = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        ctx.beginPath();
        // Maple-ish or Elm leaf curved shape
        ctx.moveTo(0, -size * 0.6);
        ctx.bezierCurveTo(size * 0.5, -size * 0.4, size * 0.6, size * 0.3, 0, size * 0.6);
        ctx.bezierCurveTo(-size * 0.6, size * 0.3, -size * 0.5, -size * 0.4, 0, -size * 0.6);
        ctx.closePath();

        const grad = ctx.createLinearGradient(-size * 0.5, -size * 0.5, size * 0.5, size * 0.5);
        if (isGreen) {
            grad.addColorStop(0, '#2ecc71');
            grad.addColorStop(1, '#27ae60');
        } else {
            grad.addColorStop(0, '#e67e22');
            grad.addColorStop(0.5, '#d35400');
            grad.addColorStop(1, '#962d00');
        }
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = isGreen ? '#1e8449' : '#78281f';
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // Leaf veins
        ctx.beginPath();
        ctx.moveTo(0, -size * 0.55);
        ctx.lineTo(0, size * 0.55);
        ctx.stroke();

        ctx.restore();
    },

    drawTwig(ctx, x, y, length = 40, rotation = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        ctx.beginPath();
        ctx.moveTo(-length * 0.5, 0);
        ctx.quadraticCurveTo(-length * 0.1, -4, length * 0.5, 2);
        ctx.strokeStyle = '#6e2c00';
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Little sub-branch
        ctx.beginPath();
        ctx.moveTo(-length * 0.1, -2);
        ctx.lineTo(0, -10);
        ctx.lineWidth = 2.5;
        ctx.stroke();

        ctx.restore();
    },

    drawBottleCap(ctx, x, y, radius = 14, color = '#2980b9') {
        ctx.save();
        ctx.translate(x, y);

        // Outer ribbed rim
        ctx.beginPath();
        for (let i = 0; i < 16; i++) {
            const angle = (i * Math.PI * 2) / 16;
            const r = i % 2 === 0 ? radius : radius - 1.5;
            const px = Math.cos(angle) * r;
            const py = Math.sin(angle) * r;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#1b4f72';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Inner cap seal circle
        ctx.beginPath();
        ctx.arc(0, 0, radius * 0.65, 0, Math.PI * 2);
        ctx.fillStyle = '#3498db';
        ctx.fill();

        ctx.restore();
    },

    drawStar(ctx, x, y, size = 18, rotation = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        // Wooden golden star
        const spikes = 5;
        const outerRadius = size;
        const innerRadius = size * 0.45;

        ctx.beginPath();
        for (let i = 0; i < spikes * 2; i++) {
            const r = i % 2 === 0 ? outerRadius : innerRadius;
            const a = (i * Math.PI) / spikes - Math.PI / 2;
            const sx = Math.cos(a) * r;
            const sy = Math.sin(a) * r;
            if (i === 0) ctx.moveTo(sx, sy);
            else ctx.lineTo(sx, sy);
        }
        ctx.closePath();

        const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, outerRadius);
        grad.addColorStop(0, '#f9e79f');
        grad.addColorStop(0.6, '#f39c12');
        grad.addColorStop(1, '#b9770e');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = '#7d6608';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Center wood grain ring
        ctx.beginPath();
        ctx.arc(0, 0, innerRadius * 0.6, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(125, 102, 8, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.restore();
    },

    drawGear(ctx, x, y, size = 16, color = '#3498db', rotation = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        const teeth = 8;
        const outerR = size;
        const innerR = size * 0.72;

        ctx.beginPath();
        for (let i = 0; i < teeth * 2; i++) {
            const r = i % 2 === 0 ? outerR : innerR;
            const a = (i * Math.PI) / teeth;
            const gx = Math.cos(a) * r;
            const gy = Math.sin(a) * r;
            if (i === 0) ctx.moveTo(gx, gy);
            else ctx.lineTo(gx, gy);
        }
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#1a5276';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Center hollow shaft
        ctx.beginPath();
        ctx.arc(0, 0, size * 0.35, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#1a5276';
        ctx.stroke();

        ctx.restore();
    },

    drawLollipop(ctx, x, y, size = 16, rotation = 0) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(rotation);

        // Stick
        ctx.beginPath();
        ctx.moveTo(0, size * 0.5);
        ctx.lineTo(0, size * 1.5);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Candy swirl disc
        ctx.beginPath();
        ctx.arc(0, 0, size, 0, Math.PI * 2);
        ctx.fillStyle = '#e91e63';
        ctx.fill();

        // Swirl spiral lines
        ctx.beginPath();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        for (let r = 2; r < size; r += 3) {
            ctx.arc(0, 0, r, r * 0.5, r * 0.5 + Math.PI * 0.6);
        }
        ctx.stroke();

        ctx.restore();
    },

    drawRainbowBridge(ctx, startX, startY, endX, endY, progress = 1) {
        ctx.save();
        const colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6'];
        const stripW = 5;

        colors.forEach((col, idx) => {
            const offset = (idx - colors.length / 2) * stripW;
            ctx.beginPath();
            ctx.moveTo(startX + offset, startY);
            const curEndX = startX + (endX - startX) * progress + offset;
            const curEndY = startY + (endY - startY) * progress;

            // Arced curve upwards
            const midX = (startX + curEndX) / 2;
            const midY = (startY + curEndY) / 2 - 40;

            ctx.quadraticCurveTo(midX + offset, midY, curEndX, curEndY);
            ctx.strokeStyle = col;
            ctx.lineWidth = stripW;
            ctx.lineCap = 'round';
            ctx.stroke();
        });

        ctx.restore();
    }
};

window.Sprites = Sprites;
