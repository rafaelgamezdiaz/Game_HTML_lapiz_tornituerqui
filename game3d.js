// 3D WebGL Engine for "La Gran Carrera de Kairos, Lápiz y Tornituerqui"
// Flooded Streets Racing with Branching Paths and High-Detail Blender 5.0 Models

class BoatGame3D {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.clock = new THREE.Clock();

        // Game Configuration
        this.numPlayers = 2; // 1 or 2
        this.currentCupIndex = 0;
        this.totalLaps = 3;
        this.gameState = 'menu'; // 'menu', 'select', 'racing', 'race_over', 'tournament_over'

        // Cups definition (Long tracks with curves)
        this.cups = [
            {
                name: 'Copa Pueblo Costero',
                subtitle: 'Calles inundadas, canales navegables y callejones con atajos',
                length: 16000,
                trackCurvePoints: [
                    new THREE.Vector3(0, 0, 0),
                    new THREE.Vector3(120, 0, 300),
                    new THREE.Vector3(260, 0, 700),
                    new THREE.Vector3(180, 0, 1200),
                    new THREE.Vector3(-80, 0, 1600),
                    new THREE.Vector3(-240, 0, 2100),
                    new THREE.Vector3(-150, 0, 2600),
                    new THREE.Vector3(60, 0, 3100),
                    new THREE.Vector3(200, 0, 3600),
                    new THREE.Vector3(100, 0, 4200),
                    new THREE.Vector3(-100, 0, 4800),
                    new THREE.Vector3(0, 0, 5200)
                ]
            },
            {
                name: 'Copa Colinas Curvas',
                subtitle: 'Eses enlazadas, desniveles y chicanes desafiantes',
                length: 20000,
                trackCurvePoints: [
                    new THREE.Vector3(0, 0, 0),
                    new THREE.Vector3(220, 15, 350),
                    new THREE.Vector3(380, 25, 800),
                    new THREE.Vector3(150, 10, 1300),
                    new THREE.Vector3(-180, -10, 1800),
                    new THREE.Vector3(-360, 5, 2400),
                    new THREE.Vector3(-120, 20, 3000),
                    new THREE.Vector3(250, 30, 3700),
                    new THREE.Vector3(340, 15, 4400),
                    new THREE.Vector3(50, -5, 5100),
                    new THREE.Vector3(-250, 10, 5800),
                    new THREE.Vector3(0, 0, 6500)
                ]
            },
            {
                name: 'Copa Casco Antiguo',
                subtitle: 'Curvas cerradas de 90 grados y máxima densidad de obstáculos',
                length: 24000,
                trackCurvePoints: [
                    new THREE.Vector3(0, 0, 0),
                    new THREE.Vector3(320, 0, 400),
                    new THREE.Vector3(500, 0, 950),
                    new THREE.Vector3(280, 0, 1500),
                    new THREE.Vector3(-200, 0, 2100),
                    new THREE.Vector3(-450, 0, 2750),
                    new THREE.Vector3(-320, 0, 3400),
                    new THREE.Vector3(120, 0, 4100),
                    new THREE.Vector3(420, 0, 4800),
                    new THREE.Vector3(200, 0, 5600),
                    new THREE.Vector3(-300, 0, 6400),
                    new THREE.Vector3(0, 0, 7200)
                ]
            }
        ];

        // Players selection
        this.p1Model = 'kairos'; // 'kairos', 'lapiz', 'tornituerqui'
        this.p2Model = 'lapiz';

        // Tournament Standings
        this.tournamentScores = {
            'P1': 0, 'P2': 0, 'IA_1': 0, 'IA_2': 0, 'IA_3': 0, 'IA_4': 0
        };

        // Input System
        this.keys = {};
        window.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            this.keys[e.key] = true;
        });
        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
            this.keys[e.key] = false;
        });

        // Touch / Virtual button states
        this.virtualInputs = {
            p1Left: false, p1Right: false, p1Accel: false, p1Boost: false, p1Shield: false, p1Jump: false,
            p2Left: false, p2Right: false, p2Accel: false, p2Boost: false, p2Shield: false, p2Jump: false
        };

        this.vehicles = [];
        this.obstacles = [];

        this.initThree();
        this.initClouds();
        this.initParticles();
        this.buildTrack();

        this.loadAssets(() => {
            console.log('3D Assets loaded successfully');
            this.buildTrack();
        });

        window.addEventListener('resize', () => this.onWindowResize());
    }

    initThree() {
        const w = window.innerWidth;
        const h = window.innerHeight;

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(w, h);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.1;

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x7eccff);
        this.scene.fog = new THREE.FogExp2(0xb5e2ff, 0.0014);

        // Lighting: Warm golden sunlight, hemisphere ground bounce and ambient fill for cartoon diorama richness
        const hemiLight = new THREE.HemisphereLight(0xfff5e6, 0x4a6b4a, 0.75);
        this.scene.add(hemiLight);

        const ambLight = new THREE.AmbientLight(0xffedd8, 0.55);
        this.scene.add(ambLight);

        this.sunLight = new THREE.DirectionalLight(0xfffaea, 1.45);
        this.sunLight.position.set(130, 240, 110);
        this.sunLight.castShadow = true;
        this.sunLight.shadow.mapSize.width = 2048;
        this.sunLight.shadow.mapSize.height = 2048;
        this.sunLight.shadow.bias = -0.0004;
        this.sunLight.shadow.camera.near = 10;
        this.sunLight.shadow.camera.far = 550;
        this.sunLight.shadow.camera.left = -160;
        this.sunLight.shadow.camera.right = 160;
        this.sunLight.shadow.camera.top = 160;
        this.sunLight.shadow.camera.bottom = -160;
        this.scene.add(this.sunLight);

        // Cameras for P1 and P2
        this.cameraP1 = new THREE.PerspectiveCamera(65, (w / (this.numPlayers === 2 ? 2 : 1)) / h, 0.5, 1400);
        this.cameraP2 = new THREE.PerspectiveCamera(65, (w / 2) / h, 0.5, 1400);

        // Asset Models dictionary
        this.models = {};
        this.loader = new THREE.GLTFLoader();

        // Start render loop
        requestAnimationFrame((t) => this.renderLoop(t));
    }

    createWaterTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Deep vibrant tropical canal water
        const grad = ctx.createLinearGradient(0, 0, 512, 512);
        grad.addColorStop(0, '#00b4d8');
        grad.addColorStop(0.5, '#0096c7');
        grad.addColorStop(1, '#0077b6');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 512);

        // Water caustics & ripple rings
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.42)';
        ctx.lineWidth = 2.5;
        for (let i = 0; i < 48; i++) {
            ctx.beginPath();
            const cx = Math.random() * 512;
            const cy = Math.random() * 512;
            const r = 24 + Math.random() * 55;
            ctx.ellipse(cx, cy, r, r * 0.55, Math.random() * Math.PI, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Sun glints on water
        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        for (let i = 0; i < 75; i++) {
            ctx.beginPath();
            ctx.arc(Math.random() * 512, Math.random() * 512, 1 + Math.random() * 2.2, 0, Math.PI * 2);
            ctx.fill();
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(3, 24);
        return texture;
    }

    createCobbleTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = '#636e72';
        ctx.fillRect(0, 0, 256, 256);

        // Cobblestone grid pavers
        ctx.strokeStyle = '#2d3436';
        ctx.lineWidth = 3;
        for (let y = 0; y < 256; y += 32) {
            const shift = (y % 64 === 0) ? 0 : 16;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(256, y);
            ctx.stroke();

            for (let x = shift; x < 256; x += 32) {
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x, y + 32);
                ctx.stroke();

                // Paver shading
                const shade = 100 + Math.floor(Math.random() * 35);
                ctx.fillStyle = `rgb(${shade}, ${shade + 4}, ${shade + 8})`;
                ctx.fillRect(x + 2, y + 2, 28, 28);
            }
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(4, 30);
        return texture;
    }

    initClouds() {
        this.clouds = [];
        const cloudGeom = new THREE.DodecahedronGeometry(22, 1);
        const cloudMat = new THREE.MeshBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.92
        });

        // Cumulus cloud banks circling outer horizon
        for (let i = 0; i < 28; i++) {
            const group = new THREE.Group();
            const numPuffs = 6 + Math.floor(Math.random() * 5);
            for (let j = 0; j < numPuffs; j++) {
                const puff = new THREE.Mesh(cloudGeom, cloudMat);
                puff.position.set(
                    (Math.random() - 0.5) * 65,
                    (Math.random() - 0.5) * 16,
                    (Math.random() - 0.5) * 45
                );
                const s = 0.8 + Math.random() * 0.9;
                puff.scale.set(s, s * 0.65, s);
                group.add(puff);
            }
            const angle = (i / 28) * Math.PI * 2;
            const dist = 1400 + Math.random() * 600;
            group.position.set(
                Math.cos(angle) * dist,
                110 + Math.random() * 60,
                Math.sin(angle) * dist
            );
            this.scene.add(group);
            this.clouds.push(group);
        }
    }

    initParticles() {
        this.activeParticles = [];
        this.particleMax = 200;
        const geom = new THREE.SphereGeometry(0.24, 6, 6);
        const mat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
        this.particleMesh = new THREE.InstancedMesh(geom, mat, this.particleMax);
        this.particleMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

        // Instance colors
        const colors = new Float32Array(this.particleMax * 3);
        for (let i = 0; i < this.particleMax * 3; i++) colors[i] = 1.0;
        this.particleMesh.instanceColor = new THREE.InstancedBufferAttribute(colors, 3);
        this.particleMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);

        this.scene.add(this.particleMesh);

        this.dummyObj = new THREE.Object3D();
        this.tempColor = new THREE.Color();
        for (let i = 0; i < this.particleMax; i++) {
            this.dummyObj.position.set(0, -999, 0);
            this.dummyObj.scale.set(0, 0, 0);
            this.dummyObj.updateMatrix();
            this.particleMesh.setMatrixAt(i, this.dummyObj.matrix);
        }
        this.particleMesh.instanceMatrix.needsUpdate = true;
    }

    spawnParticle(pos, vel, colorHex = 0xffffff, life = 0.55, isSmoke = false) {
        if (this.activeParticles.length >= this.particleMax) return;
        this.activeParticles.push({
            pos: pos.clone(),
            vel: vel.clone(),
            life: life,
            maxLife: life,
            color: colorHex,
            isSmoke: isSmoke
        });
    }

    updateParticles(dt) {
        for (let i = this.activeParticles.length - 1; i >= 0; i--) {
            const p = this.activeParticles[i];
            p.life -= dt;
            if (p.life <= 0) {
                this.activeParticles.splice(i, 1);
            } else {
                p.pos.addScaledVector(p.vel, dt);
                if (p.isSmoke) {
                    p.vel.y += 1.6 * dt; // Smoke rises upward
                    p.vel.x += (Math.random() - 0.5) * 0.4 * dt;
                } else {
                    p.vel.y -= 12.0 * dt; // Gravity on water drops
                }
            }
        }

        for (let i = 0; i < this.particleMax; i++) {
            if (i < this.activeParticles.length) {
                const p = this.activeParticles[i];
                const progress = 1.0 - (p.life / p.maxLife);
                // Smoke puffs expand as they billow up
                const s = p.isSmoke ? (0.6 + progress * 2.2) : ((p.life / p.maxLife) * 1.3);
                this.dummyObj.position.copy(p.pos);
                this.dummyObj.scale.set(s, s, s);
                this.dummyObj.updateMatrix();
                this.particleMesh.setMatrixAt(i, this.dummyObj.matrix);

                this.tempColor.setHex(p.color);
                this.particleMesh.setColorAt(i, this.tempColor);
            } else {
                this.dummyObj.position.set(0, -999, 0);
                this.dummyObj.scale.set(0, 0, 0);
                this.dummyObj.updateMatrix();
                this.particleMesh.setMatrixAt(i, this.dummyObj.matrix);
            }
        }
        this.particleMesh.instanceMatrix.needsUpdate = true;
        if (this.particleMesh.instanceColor) this.particleMesh.instanceColor.needsUpdate = true;
    }

    loadAssets(onComplete) {
        const list = [
            { id: 'kairos', path: 'assets/models/boat_kairos.glb', isBoat: true },
            { id: 'lapiz', path: 'assets/models/boat_lapiz.glb', isBoat: true },
            { id: 'tornituerqui', path: 'assets/models/boat_tornituerqui.glb', isBoat: true },
            { id: 'house', path: 'assets/models/house_village.glb' },
            { id: 'house_slate', path: 'assets/models/house_slate.glb' },
            { id: 'house_tudor', path: 'assets/models/house_tudor.glb' },
            { id: 'bridge', path: 'assets/models/bridge_arch.glb' },
            { id: 'bench', path: 'assets/models/prop_bench.glb' },
            { id: 'fence', path: 'assets/models/prop_fence.glb' },
            { id: 'tree', path: 'assets/models/tree_lowpoly.glb' },
            { id: 'rock', path: 'assets/models/obstacle_rock.glb' },
            { id: 'manhole', path: 'assets/models/obstacle_manhole.glb' },
            { id: 'lamp', path: 'assets/models/prop_lamp.glb' }
        ];

        let loadedCount = 0;
        const total = list.length;

        list.forEach(item => {
            this.loader.load(
                item.path,
                (gltf) => {
                    const obj = gltf.scene;
                    obj.traverse((node) => {
                        if (node.isMesh) {
                            node.castShadow = true;
                            node.receiveShadow = true;
                            if (node.material) {
                                node.material.side = THREE.DoubleSide;
                            }
                        }
                    });
                    this.models[item.id] = obj;
                    loadedCount++;
                    if (loadedCount >= total && onComplete) onComplete();
                },
                undefined,
                (err) => {
                    console.warn(`Fallback for model: ${item.id}`, err);
                    this.models[item.id] = this.createFallbackModel(item.id);
                    loadedCount++;
                    if (loadedCount >= total && onComplete) onComplete();
                }
            );
        });
    }

    createFallbackModel(type) {
        const group = new THREE.Group();
        let geom, mat;
        if (type.includes('boat')) {
            geom = new THREE.BoxGeometry(1.2, 0.8, 2.2);
            mat = new THREE.MeshStandardMaterial({ color: 0x3498db });
        } else if (type === 'house') {
            geom = new THREE.BoxGeometry(2.5, 2.5, 2.5);
            mat = new THREE.MeshStandardMaterial({ color: 0xe67e22 });
        } else if (type === 'tree') {
            geom = new THREE.ConeGeometry(1.2, 3, 6);
            mat = new THREE.MeshStandardMaterial({ color: 0x27ae60 });
        } else if (type === 'rock') {
            geom = new THREE.DodecahedronGeometry(0.8);
            mat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d });
        } else {
            geom = new THREE.CylinderGeometry(0.7, 0.7, 0.1, 12);
            mat = new THREE.MeshStandardMaterial({ color: 0x333333 });
        }
        const mesh = new THREE.Mesh(geom, mat);
        group.add(mesh);
        return group;
    }

    buildTrack() {
        if (this.trackContainer) {
            this.scene.remove(this.trackContainer);
        }
        this.trackContainer = new THREE.Group();
        this.scene.add(this.trackContainer);

        const cup = this.cups[this.currentCupIndex];
        const points = cup.trackCurvePoints;
        this.curve = new THREE.CatmullRomCurve3(points, true, 'centripetal');

        const divisions = 350;
        this.trackPoints = this.curve.getSpacedPoints(divisions);
        const roadWidth = 14;
        const curbWidth = 0.55;
        const sidewalkWidth = 4.8;
        const up = new THREE.Vector3(0, 1, 0);

        // Geometries
        const waterGeom = new THREE.BufferGeometry();
        const bedGeom = new THREE.BufferGeometry();
        const curbLeftGeom = new THREE.BufferGeometry();
        const curbRightGeom = new THREE.BufferGeometry();
        const sidewalkGeom = new THREE.BufferGeometry();
        const foamGeom = new THREE.BufferGeometry();

        // Branching Shortcut Alley (Calle Alterna between t = 0.24 and t = 0.60)
        const scWaterGeom = new THREE.BufferGeometry();
        const scBedGeom = new THREE.BufferGeometry();
        const scFoamGeom = new THREE.BufferGeometry();

        const waterVerts = [];
        const waterUVs = [];
        const waterIndices = [];

        const bedVerts = [];
        const bedUVs = [];
        const bedIndices = [];

        const curbLVerts = [];
        const curbLColors = [];
        const curbLIndices = [];

        const curbRVerts = [];
        const curbRColors = [];
        const curbRIndices = [];

        const swVerts = [];
        const swUVs = [];
        const swIndices = [];

        const foamVerts = [];
        const foamIndices = [];

        const scWaterVerts = [];
        const scWaterUVs = [];
        const scWaterIndices = [];

        const scBedVerts = [];
        const scBedUVs = [];
        const scBedIndices = [];

        let scQuadCount = 0;

        for (let i = 0; i <= divisions; i++) {
            const t = i / divisions;
            const pt = this.curve.getPointAt(t);
            const tangent = this.curve.getTangentAt(t).normalize();
            const normal = new THREE.Vector3().crossVectors(tangent, up).normalize();

            // Main Canal Edges
            const pLeft = pt.clone().addScaledVector(normal, -roadWidth / 2);
            const pRight = pt.clone().addScaledVector(normal, roadWidth / 2);

            // 1. Water surface (At Y = 0.05 with animated ripple texture)
            waterVerts.push(pLeft.x, pLeft.y + 0.05, pLeft.z);
            waterVerts.push(pRight.x, pRight.y + 0.05, pRight.z);
            waterUVs.push(0, t * 75);
            waterUVs.push(1, t * 75);

            // 2. Submerged Canal Bed (At Y = -0.42, revealing submerged cobblestone street after rain)
            bedVerts.push(pLeft.x, pLeft.y - 0.42, pLeft.z);
            bedVerts.push(pRight.x, pRight.y - 0.42, pRight.z);
            bedUVs.push(0, t * 80);
            bedUVs.push(1, t * 80);

            // 3. Stone Curbs with racing kerbs on turns
            const isCurve = Math.abs(normal.x) > 0.35 || (i % 16 < 8);
            const isRed = Math.floor(i / 2) % 2 === 0;
            const cr = isCurve ? (isRed ? 0.92 : 0.98) : 0.68;
            const cg = isCurve ? (isRed ? 0.20 : 0.98) : 0.70;
            const cb = isCurve ? (isRed ? 0.20 : 0.98) : 0.72;

            const cLOuter = pt.clone().addScaledVector(normal, -roadWidth / 2 - curbWidth);
            curbLVerts.push(cLOuter.x, cLOuter.y + 0.18, cLOuter.z);
            curbLVerts.push(pLeft.x, pLeft.y + 0.18, pLeft.z);
            curbLColors.push(cr, cg, cb, cr, cg, cb);

            const cROuter = pt.clone().addScaledVector(normal, roadWidth / 2 + curbWidth);
            curbRVerts.push(pRight.x, pRight.y + 0.18, pRight.z);
            curbRVerts.push(cROuter.x, cROuter.y + 0.18, cROuter.z);
            curbRColors.push(cr, cg, cb, cr, cg, cb);

            // 4. Cobblestone Sidewalks on Left and Right
            const swLOuter = pt.clone().addScaledVector(normal, -roadWidth / 2 - curbWidth - sidewalkWidth);
            const swROuter = pt.clone().addScaledVector(normal, roadWidth / 2 + curbWidth + sidewalkWidth);

            swVerts.push(swLOuter.x, swLOuter.y + 0.15, swLOuter.z);
            swVerts.push(cLOuter.x, cLOuter.y + 0.15, cLOuter.z);
            swVerts.push(cROuter.x, cROuter.y + 0.15, cROuter.z);
            swVerts.push(swROuter.x, swROuter.y + 0.15, swROuter.z);

            swUVs.push(0, t * 60, 0.5, t * 60, 0.5, t * 60, 1.0, t * 60);

            // 5. White Foam Water Ribbons lapping against curbs
            const fLOuter = pt.clone().addScaledVector(normal, -roadWidth / 2 + 0.55);
            const fROuter = pt.clone().addScaledVector(normal, roadWidth / 2 - 0.55);
            foamVerts.push(pLeft.x, pLeft.y + 0.06, pLeft.z);
            foamVerts.push(fLOuter.x, fLOuter.y + 0.06, fLOuter.z);
            foamVerts.push(fROuter.x, fROuter.y + 0.06, fROuter.z);
            foamVerts.push(pRight.x, pRight.y + 0.06, pRight.z);

            // 6. Branching Canal Street (Callejón Inundado / Atajo between t = 0.24 and 0.60)
            if (t >= 0.24 && t <= 0.60) {
                const scWidth = 7.0;
                const scOffset = -roadWidth / 2 - curbWidth - 5.5;
                const scL = pt.clone().addScaledVector(normal, scOffset - scWidth / 2);
                const scR = pt.clone().addScaledVector(normal, scOffset + scWidth / 2);

                scWaterVerts.push(scL.x, scL.y + 0.05, scL.z);
                scWaterVerts.push(scR.x, scR.y + 0.05, scR.z);
                scWaterUVs.push(0, t * 75);
                scWaterUVs.push(1, t * 75);

                scBedVerts.push(scL.x, scL.y - 0.42, scL.z);
                scBedVerts.push(scR.x, scR.y - 0.42, scR.z);
                scBedUVs.push(0, t * 80);
                scBedUVs.push(1, t * 80);

                if (scQuadCount > 0) {
                    const b = (scQuadCount - 1) * 2;
                    scWaterIndices.push(b, b + 1, b + 2);
                    scWaterIndices.push(b + 1, b + 3, b + 2);

                    scBedIndices.push(b, b + 1, b + 2);
                    scBedIndices.push(b + 1, b + 3, b + 2);
                }
                scQuadCount++;
            }

            if (i < divisions) {
                const base = i * 2;
                waterIndices.push(base, base + 1, base + 2);
                waterIndices.push(base + 1, base + 3, base + 2);

                bedIndices.push(base, base + 1, base + 2);
                bedIndices.push(base + 1, base + 3, base + 2);

                curbLIndices.push(base, base + 1, base + 2);
                curbLIndices.push(base + 1, base + 3, base + 2);

                curbRIndices.push(base, base + 1, base + 2);
                curbRIndices.push(base + 1, base + 3, base + 2);

                const swBase = i * 4;
                swIndices.push(swBase, swBase + 1, swBase + 4);
                swIndices.push(swBase + 1, swBase + 5, swBase + 4);
                swIndices.push(swBase + 2, swBase + 3, swBase + 6);
                swIndices.push(swBase + 3, swBase + 7, swBase + 6);

                const fBase = i * 4;
                foamIndices.push(fBase, fBase + 1, fBase + 4);
                foamIndices.push(fBase + 1, fBase + 5, fBase + 4);
                foamIndices.push(fBase + 2, fBase + 3, fBase + 6);
                foamIndices.push(fBase + 3, fBase + 7, fBase + 6);
            }
        }

        // Set attributes
        waterGeom.setAttribute('position', new THREE.Float32BufferAttribute(waterVerts, 3));
        waterGeom.setAttribute('uv', new THREE.Float32BufferAttribute(waterUVs, 2));
        waterGeom.setIndex(waterIndices);
        waterGeom.computeVertexNormals();

        this.waterBaseY = [];
        for (let i = 1; i < waterVerts.length; i += 3) {
            this.waterBaseY.push(waterVerts[i]);
        }

        bedGeom.setAttribute('position', new THREE.Float32BufferAttribute(bedVerts, 3));
        bedGeom.setAttribute('uv', new THREE.Float32BufferAttribute(bedUVs, 2));
        bedGeom.setIndex(bedIndices);
        bedGeom.computeVertexNormals();

        curbLeftGeom.setAttribute('position', new THREE.Float32BufferAttribute(curbLVerts, 3));
        curbLeftGeom.setAttribute('color', new THREE.Float32BufferAttribute(curbLColors, 3));
        curbLeftGeom.setIndex(curbLIndices);
        curbLeftGeom.computeVertexNormals();

        curbRightGeom.setAttribute('position', new THREE.Float32BufferAttribute(curbRVerts, 3));
        curbRightGeom.setAttribute('color', new THREE.Float32BufferAttribute(curbRColors, 3));
        curbRightGeom.setIndex(curbRIndices);
        curbRightGeom.computeVertexNormals();

        sidewalkGeom.setAttribute('position', new THREE.Float32BufferAttribute(swVerts, 3));
        sidewalkGeom.setAttribute('uv', new THREE.Float32BufferAttribute(swUVs, 2));
        sidewalkGeom.setIndex(swIndices);
        sidewalkGeom.computeVertexNormals();

        foamGeom.setAttribute('position', new THREE.Float32BufferAttribute(foamVerts, 3));
        foamGeom.setIndex(foamIndices);
        foamGeom.computeVertexNormals();

        // 1. Flooded Canal Water Material (Vibrant aquamarine with caustics, wave ripples and specular shine)
        this.waterTexture = this.createWaterTexture();
        const waterMat = new THREE.MeshStandardMaterial({
            map: this.waterTexture,
            color: 0x00c8f8,
            roughness: 0.08,
            metalness: 0.18,
            transparent: true,
            opacity: 0.82
        });
        this.waterMesh = new THREE.Mesh(waterGeom, waterMat);
        this.waterMesh.receiveShadow = true;
        this.trackContainer.add(this.waterMesh);

        // 2. Submerged Cobblestone Street Bed beneath the water
        this.cobbleTexture = this.createCobbleTexture();
        const bedMat = new THREE.MeshStandardMaterial({
            map: this.cobbleTexture,
            color: 0x576574,
            roughness: 0.85
        });
        const bedMesh = new THREE.Mesh(bedGeom, bedMat);
        bedMesh.receiveShadow = true;
        this.trackContainer.add(bedMesh);

        // 3. Water Foam Edge Ribbons
        const foamMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.82 });
        const foamMesh = new THREE.Mesh(foamGeom, foamMat);
        this.trackContainer.add(foamMesh);

        // 4. Branching Shortcut Canal Alley Meshes
        if (scWaterVerts.length > 0) {
            scWaterGeom.setAttribute('position', new THREE.Float32BufferAttribute(scWaterVerts, 3));
            scWaterGeom.setAttribute('uv', new THREE.Float32BufferAttribute(scWaterUVs, 2));
            scWaterGeom.setIndex(scWaterIndices);
            scWaterGeom.computeVertexNormals();

            this.scWaterBaseY = [];
            for (let i = 1; i < scWaterVerts.length; i += 3) {
                this.scWaterBaseY.push(scWaterVerts[i]);
            }

            this.scWaterMesh = new THREE.Mesh(scWaterGeom, waterMat);
            this.scWaterMesh.receiveShadow = true;
            this.trackContainer.add(this.scWaterMesh);

            scBedGeom.setAttribute('position', new THREE.Float32BufferAttribute(scBedVerts, 3));
            scBedGeom.setAttribute('uv', new THREE.Float32BufferAttribute(scBedUVs, 2));
            scBedGeom.setIndex(scBedIndices);
            scBedGeom.computeVertexNormals();
            const scBedMesh = new THREE.Mesh(scBedGeom, bedMat);
            scBedMesh.receiveShadow = true;
            this.trackContainer.add(scBedMesh);
        }

        // 5. Curbs (Stone grey with red/white rumble on curves)
        const curbMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.6 });
        const curbLMesh = new THREE.Mesh(curbLeftGeom, curbMat);
        const curbRMesh = new THREE.Mesh(curbRightGeom, curbMat);
        curbLMesh.receiveShadow = true;
        curbRMesh.receiveShadow = true;
        this.trackContainer.add(curbLMesh);
        this.trackContainer.add(curbRMesh);

        // 6. Cobblestone Sidewalks
        const sidewalkMat = new THREE.MeshStandardMaterial({
            map: this.cobbleTexture,
            color: 0xdcdde1,
            roughness: 0.82
        });
        const sidewalkMesh = new THREE.Mesh(sidewalkGeom, sidewalkMat);
        sidewalkMesh.receiveShadow = true;
        this.trackContainer.add(sidewalkMesh);

        // 7. Ground terrain plane (Grassy European landscape)
        const terrainGeom = new THREE.PlaneGeometry(12000, 12000, 32, 32);
        const terrainMat = new THREE.MeshStandardMaterial({ color: 0x82c96c, roughness: 0.95 });
        const terrain = new THREE.Mesh(terrainGeom, terrainMat);
        terrain.rotation.x = -Math.PI / 2;
        terrain.position.y = -0.38;
        terrain.receiveShadow = true;
        this.trackContainer.add(terrain);

        // 8. Overhead Branching Sign Archway at t = 0.24
        this.buildBranchingArch(roadWidth, curbWidth);

        // 9. Finish Line Archway
        this.buildFinishArch(roadWidth, curbWidth);

        // 10. Scenery & Obstacles (Dense Village Population)
        this.obstacles = [];
        this.spawnTrackScenery(divisions, roadWidth, curbWidth, sidewalkWidth);

        // Setup Competitors
        this.setupVehicles();
    }

    buildBranchingArch(roadWidth, curbWidth) {
        const pt = this.curve.getPointAt(0.24);
        const tangent = this.curve.getTangentAt(0.24).normalize();
        const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

        const woodMat = new THREE.MeshStandardMaterial({ color: 0x5d4037, roughness: 0.7 });
        const signMatLeft = new THREE.MeshStandardMaterial({ color: 0xe67e22, roughness: 0.4 });
        const signMatRight = new THREE.MeshStandardMaterial({ color: 0x2980b9, roughness: 0.4 });

        // Left post (at edge of branching alley)
        const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 8.5, 10), woodMat);
        p1.position.copy(pt.clone().addScaledVector(normal, -roadWidth / 2 - 9.5));
        p1.position.y += 4.25;
        this.trackContainer.add(p1);

        // Center post (between alley and main canal)
        const p2 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 8.5, 10), woodMat);
        p2.position.copy(pt.clone().addScaledVector(normal, -roadWidth / 2 - curbWidth));
        p2.position.y += 4.25;
        this.trackContainer.add(p2);

        // Right post
        const p3 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 8.5, 10), woodMat);
        p3.position.copy(pt.clone().addScaledVector(normal, roadWidth / 2 + curbWidth));
        p3.position.y += 4.25;
        this.trackContainer.add(p3);

        // Overhead sign left: ATAJO CALLEJÓN
        const signLeft = new THREE.Mesh(new THREE.BoxGeometry(8.5, 1.4, 0.35), signMatLeft);
        signLeft.position.copy(pt.clone().addScaledVector(normal, -roadWidth / 2 - 5.0));
        signLeft.position.y += 7.2;
        signLeft.rotation.y = Math.atan2(tangent.x, tangent.z);
        this.trackContainer.add(signLeft);

        // Overhead sign right: CALLE PRINCIPAL
        const signRight = new THREE.Mesh(new THREE.BoxGeometry(roadWidth, 1.4, 0.35), signMatRight);
        signRight.position.copy(pt.clone());
        signRight.position.y += 7.2;
        signRight.rotation.y = Math.atan2(tangent.x, tangent.z);
        this.trackContainer.add(signRight);
    }

    buildFinishArch(roadWidth, curbWidth) {
        const pt = this.curve.getPointAt(0.001);
        const tangent = this.curve.getTangentAt(0.001).normalize();
        const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

        const postMat = new THREE.MeshStandardMaterial({ color: 0xd63031, metalness: 0.4 });
        const bannerMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });

        // Left and Right Posts
        [-1, 1].forEach((side) => {
            const pGeom = new THREE.CylinderGeometry(0.35, 0.35, 7.5, 12);
            const post = new THREE.Mesh(pGeom, postMat);
            post.position.copy(pt.clone().addScaledVector(normal, side * (roadWidth / 2 + curbWidth / 2)));
            post.position.y += 3.75;
            this.trackContainer.add(post);
        });

        // Top Banner Crossbar
        const crossGeom = new THREE.BoxGeometry(roadWidth + curbWidth + 1.2, 1.5, 0.45);
        const banner = new THREE.Mesh(crossGeom, bannerMat);
        banner.position.copy(pt.clone());
        banner.position.y += 7.2;
        banner.rotation.y = Math.atan2(tangent.x, tangent.z);
        this.trackContainer.add(banner);
    }

    spawnTrackScenery(divisions, roadWidth, curbWidth, sidewalkWidth) {
        const houseModel = this.models['house'];
        const houseSlateModel = this.models['house_slate'];
        const houseTudorModel = this.models['house_tudor'];
        const bridgeModel = this.models['bridge'];
        const benchModel = this.models['bench'];
        const fenceModel = this.models['fence'];
        const treeModel = this.models['tree'];
        const lampModel = this.models['lamp'];
        const rockModel = this.models['rock'];
        const manholeModel = this.models['manhole'];

        const houseVariants = [houseModel, houseSlateModel, houseTudorModel].filter(Boolean);

        for (let i = 0; i < divisions; i++) {
            const t = i / divisions;
            const pt = this.curve.getPointAt(t);
            const tangent = this.curve.getTangentAt(t).normalize();
            const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

            // Stone Arch Bridges spanning across the flooded canal
            if ((i === Math.floor(divisions * 0.38) || i === Math.floor(divisions * 0.72)) && bridgeModel) {
                const bridge = bridgeModel.clone();
                bridge.position.copy(pt.clone());
                bridge.position.y += 0.05;
                bridge.rotation.y = Math.atan2(tangent.x, tangent.z);
                this.trackContainer.add(bridge);
            }

            [-1, 1].forEach((side) => {
                const distSidewalk = (roadWidth / 2) + curbWidth;
                const distHouse = distSidewalk + sidewalkWidth + 2.8;

                // Dense village houses lining both canal banks
                const isHouseSlot = (side === -1) ? (i % 2 === 0) : ((i + 1) % 2 === 0);
                if (isHouseSlot && houseVariants.length > 0) {
                    const houseIndex = (i + (side > 0 ? 1 : 0)) % houseVariants.length;
                    const house = houseVariants[houseIndex].clone();
                    const posHouse = pt.clone().addScaledVector(normal, side * distHouse);
                    house.position.copy(posHouse);
                    // Slight organic rotation facing canal or angled
                    const angleOffset = ((i % 5) - 2) * 0.08;
                    house.rotation.y = Math.atan2(-normal.x * side, -normal.z * side) + angleOffset;
                    const s = 1.3 + ((i * 7) % 3) * 0.12;
                    house.scale.set(s, s, s);
                    this.trackContainer.add(house);
                } else if (fenceModel && (i % 2 === 1)) {
                    // Picket fences enclosing gardens between houses
                    const fencePos = pt.clone().addScaledVector(normal, side * (distSidewalk + sidewalkWidth + 0.15));
                    const fence = fenceModel.clone();
                    fence.position.copy(fencePos);
                    fence.position.y += 0.15;
                    fence.rotation.y = Math.atan2(tangent.x, tangent.z);
                    fence.scale.set(1.2, 1.2, 1.2);
                    this.trackContainer.add(fence);
                }

                // Park Benches facing canal
                if (i % 4 === 2 && benchModel) {
                    const benchPos = pt.clone().addScaledVector(normal, side * (distSidewalk + 1.8));
                    const bench = benchModel.clone();
                    bench.position.copy(benchPos);
                    bench.position.y += 0.15;
                    bench.rotation.y = Math.atan2(-normal.x * side, -normal.z * side) + mathPiHalf(side);
                    bench.scale.set(1.2, 1.2, 1.2);
                    this.trackContainer.add(bench);
                }

                // Low-poly Deciduous Trees with lush foliage
                if (i % 3 === 1 && treeModel) {
                    const treePos = pt.clone().addScaledVector(normal, side * (distSidewalk + sidewalkWidth + 1.6)).addScaledVector(tangent, 1.4);
                    const tree = treeModel.clone();
                    tree.position.copy(treePos);
                    const s = 1.3 + ((i * 5) % 4) * 0.18;
                    tree.scale.set(s, s, s);
                    this.trackContainer.add(tree);
                }

                // Victorian Street Lamps along sidewalks
                if (i % 3 === 0 && lampModel) {
                    const lampPos = pt.clone().addScaledVector(normal, side * (distSidewalk + 0.65));
                    const lamp = lampModel.clone();
                    lamp.position.copy(lampPos);
                    lamp.position.y += 0.15;
                    lamp.scale.set(1.15, 1.15, 1.15);
                    this.trackContainer.add(lamp);
                }
            });

            // Obstacles in the flooded water (Mossy rocks & storm drains)
            if (i > 8 && i % 6 === 0 && (rockModel || manholeModel)) {
                const laneOffset = ((i % 5) - 2) * 2.1;
                const obsPos = pt.clone().addScaledVector(normal, laneOffset);
                const isRock = (i % 2 === 0);

                if (isRock && rockModel) {
                    const rock = rockModel.clone();
                    rock.position.copy(obsPos);
                    rock.position.y += 0.15;
                    rock.scale.set(1.3, 1.3, 1.3);
                    this.trackContainer.add(rock);
                    this.obstacles.push({ type: 'rock', pos: obsPos, radius: 1.5, mesh: rock });
                } else if (manholeModel) {
                    const manhole = manholeModel.clone();
                    manhole.position.copy(obsPos);
                    manhole.position.y += 0.05;
                    manhole.scale.set(1.5, 1.5, 1.5);
                    this.trackContainer.add(manhole);
                    this.obstacles.push({ type: 'manhole', pos: obsPos, radius: 1.6, mesh: manhole });
                }
            }
        }

        function mathPiHalf(side) {
            return side > 0 ? -Math.PI / 2 : Math.PI / 2;
        }
    }

    setupVehicles() {
        if (this.vehicles) {
            this.vehicles.forEach(v => {
                if (v.mesh && v.mesh.parent) {
                    v.mesh.parent.remove(v.mesh);
                }
            });
        }
        this.vehicles = [];

        const configs = [
            { id: 'P1', name: 'Jugador 1', modelKey: this.p1Model, isAI: false, lane: -2.5 },
            { id: 'P2', name: 'Jugador 2', modelKey: this.p2Model, isAI: this.numPlayers === 1, lane: 2.5 },
            { id: 'IA_1', name: 'Vaporcito', modelKey: 'tornituerqui', isAI: true, lane: -5.0 },
            { id: 'IA_2', name: 'Grafito Veloz', modelKey: 'lapiz', isAI: true, lane: 5.0 },
            { id: 'IA_3', name: 'Brisamar', modelKey: 'kairos', isAI: true, lane: -1.0 },
            { id: 'IA_4', name: 'Tuerca Brava', modelKey: 'tornituerqui', isAI: true, lane: 1.0 }
        ];

        configs.forEach((cfg) => {
            const rawModel = this.models[cfg.modelKey] || this.createFallbackModel('boat');
            const mesh = rawModel.clone();
            mesh.scale.set(1.18, 1.18, 1.18);
            const rotOffsets = { 'kairos': Math.PI, 'tornituerqui': Math.PI, 'lapiz': Math.PI };
            mesh.rotation.y = rotOffsets[cfg.modelKey] || Math.PI;

            // Glowing shield bubble
            const shieldGeom = new THREE.SphereGeometry(2.35, 14, 10);
            const shieldMat = new THREE.MeshBasicMaterial({
                color: 0x00e5ff,
                transparent: true,
                opacity: 0.35,
                wireframe: true
            });
            const shieldMesh = new THREE.Mesh(shieldGeom, shieldMat);
            shieldMesh.visible = false;
            mesh.add(shieldMesh);

            this.scene.add(mesh);

            const vehicle = {
                id: cfg.id,
                name: cfg.name,
                modelKey: cfg.modelKey,
                isAI: cfg.isAI,
                mesh: mesh,
                shieldMesh: shieldMesh,
                progress: 0.002, // 0 to 1 along spline
                lap: 1,
                laneOffset: cfg.lane,
                targetLane: cfg.lane,
                steerAngle: 0,
                targetSteerAngle: 0,
                rollAngle: 0,
                targetRollAngle: 0,
                speed: 0,
                maxSpeed: 88 + (cfg.isAI ? Math.random() * 8 : 10),
                accel: 55,
                handling: 4.8,
                spinTimer: 0,
                boostTimer: 0,
                shieldTimer: 0,
                jumpY: 0,
                jumpVy: 0,
                isJumping: false,
                finished: false,
                finishRank: 0,
                inShortcut: false
            };

            this.vehicles.push(vehicle);
        });

        this.finishedVehicles = [];
    }

    startRace() {
        this.gameState = 'racing';
        this.finishedVehicles = [];
        const cup = this.cups[this.currentCupIndex];

        // Reset positions
        this.vehicles.forEach((v, idx) => {
            v.progress = 0.001 + (idx * 0.003);
            v.lap = 1;
            v.speed = 0;
            v.finished = false;
            v.spinTimer = 0;
            v.boostTimer = 0;
            v.shieldTimer = 0;
            v.jumpY = 0;
            v.jumpVy = 0;
            v.isJumping = false;
            v.inShortcut = false;
            v.targetLane = v.laneOffset;
            if (v.shieldMesh) v.shieldMesh.visible = false;
        });

        // Hide title, show HUD
        const titleScreen = document.getElementById('title-screen');
        const victoryScreen = document.getElementById('victory-screen');
        const gameHud = document.getElementById('game-hud');

        if (titleScreen) titleScreen.classList.add('hidden');
        if (victoryScreen) victoryScreen.classList.add('hidden');
        if (gameHud) gameHud.classList.remove('hidden');

        const cupBadge = document.getElementById('hud-cup-title');
        if (cupBadge) cupBadge.textContent = cup.name;

        if (window.soundManager) {
            if (typeof window.soundManager.init === 'function') window.soundManager.init();
            if (typeof window.soundManager.playButton === 'function') window.soundManager.playButton();
        }
    }

    update(dt) {
        if (this.gameState !== 'racing' || !this.curve || !this.vehicles || !this.vehicles.length) return;

        // Process Player 1 Inputs
        const p1 = this.vehicles.find(v => v.id === 'P1');
        if (p1 && !p1.finished) {
            const steerLeft = this.keys['KeyA'] || this.virtualInputs.p1Left;
            const steerRight = this.keys['KeyD'] || this.virtualInputs.p1Right;
            const accel = this.keys['KeyW'] || this.virtualInputs.p1Accel;
            const brake = this.keys['KeyS'];
            const boost = this.keys['Space'] || this.keys['Digit1'] || this.virtualInputs.p1Boost;
            const shield = this.keys['KeyQ'] || this.keys['Digit2'] || this.virtualInputs.p1Shield;
            const jump = this.keys['KeyE'] || this.keys['Digit3'] || this.virtualInputs.p1Jump;

            if (boost && p1.boostTimer <= 0) {
                p1.boostTimer = 2.0;
                if (window.soundManager) window.soundManager.playWindBoost();
            }
            if (shield && p1.shieldTimer <= 0) {
                p1.shieldTimer = 4.5;
                if (window.soundManager) window.soundManager.playRepair();
            }
            if (jump && !p1.isJumping) {
                p1.isJumping = true;
                p1.jumpVy = 16;
                if (window.soundManager) window.soundManager.playJump();
            }

            // Dynamic car-like steering: turning authority requires forward momentum
            let p1SteerInput = 0;
            if (steerLeft) p1SteerInput -= 1.0;
            if (steerRight) p1SteerInput += 1.0;

            const p1SpeedFactor = Math.min(1.0, Math.max(0.18, p1.speed / 28.0));
            const minLane = (p1.progress >= 0.26 && p1.progress <= 0.60) ? -9.5 : -6.0;

            if (p1SteerInput !== 0) {
                // Nose points into the turn (yaw), hull banks (roll)
                p1.targetSteerAngle = p1SteerInput * 0.38;
                p1.targetRollAngle = p1SteerInput * 0.16;
                // Lateral shift is proportional to forward movement
                const turnRate = p1.handling * dt * 3.8 * p1SpeedFactor;
                p1.laneOffset = Math.max(minLane, Math.min(6.0, p1.laneOffset + p1SteerInput * turnRate));
            } else {
                p1.targetSteerAngle = 0;
                p1.targetRollAngle = 0;
            }

            p1.steerAngle = THREE.MathUtils.lerp(p1.steerAngle || 0, p1.targetSteerAngle, dt * 10.0);
            p1.rollAngle = THREE.MathUtils.lerp(p1.rollAngle || 0, p1.targetRollAngle, dt * 8.0);

            const topSpeed = p1.boostTimer > 0 ? p1.maxSpeed * 1.45 : p1.maxSpeed;
            if (accel) p1.speed = Math.min(p1.speed + p1.accel * dt, topSpeed);
            else if (brake) p1.speed = Math.max(p1.speed - p1.accel * dt * 2, 0);
            else p1.speed = Math.max(p1.speed - 15 * dt, 0);
        }

        // Process Player 2 Inputs
        const p2 = this.vehicles.find(v => v.id === 'P2');
        if (p2 && !p2.finished) {
            if (this.numPlayers === 2) {
                const steerLeft = this.keys['ArrowLeft'] || this.keys['Numpad4'] || this.keys['4'] || this.virtualInputs.p2Left;
                const steerRight = this.keys['ArrowRight'] || this.keys['Numpad6'] || this.keys['6'] || this.virtualInputs.p2Right;
                const accel = this.keys['ArrowUp'] || this.keys['Numpad8'] || this.keys['8'] || this.virtualInputs.p2Accel;
                const brake = this.keys['ArrowDown'] || this.keys['Numpad5'] || this.keys['5'] || this.keys['Numpad2'] || this.keys['2'];
                const boost = this.keys['Enter'] || this.keys['NumpadEnter'] || this.keys['Numpad0'] || this.keys['0'] || this.keys['Numpad1'] || this.keys['1'] || this.virtualInputs.p2Boost;
                const shield = this.keys['ShiftRight'] || this.keys['NumpadDecimal'] || this.keys['NumpadPeriod'] || this.keys['.'] || this.keys['NumpadAdd'] || this.keys['+'] || this.keys['Numpad7'] || this.keys['7'] || this.virtualInputs.p2Shield;
                const jump = this.keys['ControlRight'] || this.keys['Numpad3'] || this.keys['3'] || this.keys['Numpad9'] || this.keys['9'] || this.virtualInputs.p2Jump;

                if (boost && p2.boostTimer <= 0) {
                    p2.boostTimer = 2.0;
                    if (window.soundManager) window.soundManager.playWindBoost();
                }
                if (shield && p2.shieldTimer <= 0) {
                    p2.shieldTimer = 4.5;
                    if (window.soundManager) window.soundManager.playRepair();
                }
                if (jump && !p2.isJumping) {
                    p2.isJumping = true;
                    p2.jumpVy = 16;
                    if (window.soundManager) window.soundManager.playJump();
                }

                let p2SteerInput = 0;
                if (steerLeft) p2SteerInput -= 1.0;
                if (steerRight) p2SteerInput += 1.0;

                const p2SpeedFactor = Math.min(1.0, Math.max(0.18, p2.speed / 28.0));
                const minLane = (p2.progress >= 0.26 && p2.progress <= 0.60) ? -9.5 : -6.0;

                if (p2SteerInput !== 0) {
                    p2.targetSteerAngle = p2SteerInput * 0.38;
                    p2.targetRollAngle = p2SteerInput * 0.16;
                    const turnRate = p2.handling * dt * 3.8 * p2SpeedFactor;
                    p2.laneOffset = Math.max(minLane, Math.min(6.0, p2.laneOffset + p2SteerInput * turnRate));
                } else {
                    p2.targetSteerAngle = 0;
                    p2.targetRollAngle = 0;
                }

                p2.steerAngle = THREE.MathUtils.lerp(p2.steerAngle || 0, p2.targetSteerAngle, dt * 10.0);
                p2.rollAngle = THREE.MathUtils.lerp(p2.rollAngle || 0, p2.targetRollAngle, dt * 8.0);

                const topSpeed = p2.boostTimer > 0 ? p2.maxSpeed * 1.45 : p2.maxSpeed;
                if (accel) p2.speed = Math.min(p2.speed + p2.accel * dt, topSpeed);
                else if (brake) p2.speed = Math.max(p2.speed - p2.accel * dt * 2, 0);
                else p2.speed = Math.max(p2.speed - 15 * dt, 0);
            } else {
                this.updateAIVehicle(p2, dt);
            }
        }

        // Process AI Vehicles
        this.vehicles.filter(v => v.isAI && v.id !== 'P2').forEach(ai => {
            this.updateAIVehicle(ai, dt);
        });

        // Update physics, positions and collisions for all vehicles
        const cup = this.cups[this.currentCupIndex];
        const trackLengthUnits = cup.length;

        this.vehicles.forEach(v => {
            if (v.finished) return;

            if (v.spinTimer > 0) {
                v.spinTimer -= dt;
                v.speed = Math.max(v.speed - 40 * dt, 15);
                v.mesh.rotation.y += dt * 14;
            } else {
                if (v.boostTimer > 0) v.boostTimer -= dt;
            }

            if (v.shieldTimer > 0) {
                v.shieldTimer -= dt;
                if (v.shieldMesh) {
                    v.shieldMesh.visible = true;
                    v.shieldMesh.rotation.y += dt * 3.5;
                }
            } else if (v.shieldMesh) {
                v.shieldMesh.visible = false;
            }

            // Jump Physics
            if (v.isJumping) {
                v.jumpY += v.jumpVy * dt;
                v.jumpVy -= 42 * dt;
                if (v.jumpY <= 0) {
                    v.jumpY = 0;
                    v.isJumping = false;
                    v.jumpVy = 0;
                }
            }

            // Shortcut check: if in the branching alley region and laneOffset < -5.5
            const inShortcutZone = (v.progress >= 0.28 && v.progress <= 0.58);
            v.inShortcut = inShortcutZone && (v.laneOffset < -5.0);
            const shortcutBonus = v.inShortcut ? 1.30 : 1.0; // 30% faster progression in shortcut alley!

            const step = ((v.speed * shortcutBonus) / trackLengthUnits) * dt;
            v.progress += step;

            if (v.progress >= 1.0) {
                v.progress -= 1.0;
                v.lap++;
                if (v.lap > this.totalLaps) {
                    v.finished = true;
                    this.finishedVehicles.push(v);
                    v.finishRank = this.finishedVehicles.length;

                    const humans = this.vehicles.filter(vh => !vh.isAI);
                    const humansDone = humans.every(vh => vh.finished);
                    if (humansDone) {
                        this.handleRaceOver();
                    }
                }
            }

            // Calculate 3D position and orientation from Spline
            const normProgress = Math.max(0, Math.min(0.9999, ((v.progress % 1.0) + 1.0) % 1.0));
            const pt = this.curve.getPointAt(normProgress);
            const tangent = this.curve.getTangentAt(normProgress).normalize();
            const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

            const boatPos = pt.clone().addScaledVector(normal, v.laneOffset);
            boatPos.y += v.jumpY;
            v.mesh.position.copy(boatPos);

            if (v.spinTimer <= 0) {
                const rotOffset = Math.PI; // All boats face forward away from camera
                const trackHeading = Math.atan2(tangent.x, tangent.z);
                v.mesh.rotation.y = trackHeading + rotOffset + (v.steerAngle || 0);
                v.mesh.rotation.z = (v.rollAngle || 0);
                v.mesh.rotation.x = Math.sin(this.clock.getElapsedTime() * 4.0 + v.progress * 25.0) * 0.035;
            }

            // Water spray wake particles
            if (v.speed > 10 && Math.random() < 0.55) {
                const wakePos = boatPos.clone().addScaledVector(tangent, -1.8);
                const wakeVel = new THREE.Vector3((Math.random() - 0.5) * 4, 1.2 + Math.random() * 2.5, (Math.random() - 0.5) * 4);
                this.spawnParticle(wakePos, wakeVel, v.boostTimer > 0 ? 0xffa502 : 0xffffff, 0.45);
            }

            // Smoke puffs from Tornituerqui's chimney
            if (v.modelKey === 'tornituerqui' && Math.random() < 0.45) {
                const smokePos = boatPos.clone().add(new THREE.Vector3(0, 2.7, 0)).addScaledVector(tangent, -1.6);
                const smokeVel = new THREE.Vector3((Math.random() - 0.5) * 0.8, 2.2 + Math.random() * 1.4, (Math.random() - 0.5) * 0.8);
                this.spawnParticle(smokePos, smokeVel, 0x444444, 0.75, true);
            }

            // Check collision with obstacles
            if (!v.isJumping || v.jumpY < 0.8) {
                this.obstacles.forEach(obs => {
                    const dist = obs.pos.distanceTo(boatPos);
                    if (dist < obs.radius) {
                        if (v.shieldTimer > 0) {
                            if (window.soundManager) window.soundManager.playRepair();
                        } else if (obs.type === 'manhole' && v.spinTimer <= 0) {
                            v.spinTimer = 1.2;
                            if (window.soundManager) window.soundManager.playObstacleHit();
                            for (let k = 0; k < 8; k++) {
                                this.spawnParticle(boatPos, new THREE.Vector3((Math.random() - 0.5) * 7, 3 + Math.random() * 4, (Math.random() - 0.5) * 7), 0x333333, 0.6);
                            }
                        } else if (obs.type === 'rock' && v.spinTimer <= 0) {
                            v.speed = 10;
                            v.spinTimer = 0.6;
                            v.laneOffset += (v.laneOffset > 0 ? -1.5 : 1.5);
                            if (window.soundManager) window.soundManager.playObstacleHit();
                            for (let k = 0; k < 10; k++) {
                                this.spawnParticle(boatPos, new THREE.Vector3((Math.random() - 0.5) * 9, 4 + Math.random() * 5, (Math.random() - 0.5) * 9), 0x7f8c8d, 0.7);
                            }
                        }
                    }
                });
            }
        });

        this.updateHUD();
    }

    updateAIVehicle(ai, dt) {
        if (ai.finished) return;

        const p1 = this.vehicles.find(v => v.id === 'P1');
        let speedBoost = 0;
        if (p1) {
            const diff = p1.progress - ai.progress;
            if (diff > 0.05) speedBoost = 12;
            else if (diff < -0.05) speedBoost = -8;
        }

        const targetSpeed = ai.maxSpeed + speedBoost;
        if (ai.speed < targetSpeed) ai.speed += ai.accel * dt * 0.9;
        else ai.speed -= 20 * dt;

        // AI alternate path logic: some AIs decide to take the shortcut alley
        if (ai.progress >= 0.25 && ai.progress <= 0.28 && (ai.id === 'IA_1' || ai.id === 'IA_2')) {
            ai.targetLane = -7.2; // Take the shortcut alley!
        } else if (ai.progress > 0.58 && ai.targetLane < -4.5) {
            ai.targetLane = -2.0; // Rejoin main canal!
        }

        // Obstacle avoidance
        const lookAheadProgress = (ai.progress + 0.02) % 1.0;
        const futurePt = this.curve.getPointAt(lookAheadProgress);
        const tangent = this.curve.getTangentAt(lookAheadProgress).normalize();
        const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();
        const futureBoatPos = futurePt.clone().addScaledVector(normal, ai.laneOffset);

        let avoidOffset = 0;
        for (let i = 0; i < this.obstacles.length; i++) {
            const obs = this.obstacles[i];
            if (obs.pos.distanceTo(futureBoatPos) < 3.2) {
                avoidOffset = (ai.laneOffset > 0) ? -2.5 : 2.5;
                break;
            }
        }

        ai.targetLane = Math.max(-8.5, Math.min(5.5, ai.targetLane + avoidOffset));
        const laneDiff = ai.targetLane - ai.laneOffset;
        ai.laneOffset += laneDiff * dt * 2.5;

        // Smooth AI steering yaw and roll bank
        ai.targetSteerAngle = Math.max(-0.30, Math.min(0.30, laneDiff * 0.25));
        ai.targetRollAngle = ai.targetSteerAngle * 0.45;
        ai.steerAngle = THREE.MathUtils.lerp(ai.steerAngle || 0, ai.targetSteerAngle, dt * 6.0);
        ai.rollAngle = THREE.MathUtils.lerp(ai.rollAngle || 0, ai.targetRollAngle, dt * 6.0);
    }

    updateCameras() {
        if (!this.curve || !this.vehicles || !this.vehicles.length) return;
        const p1 = this.vehicles.find(v => v.id === 'P1');
        const p2 = this.vehicles.find(v => v.id === 'P2');

        if (p1) {
            const pt = p1.mesh.position;
            const u1 = Math.max(0, Math.min(0.9999, ((p1.progress % 1.0) + 1.0) % 1.0));
            const tangent = this.curve.getTangentAt(u1).normalize();
            const camPos = pt.clone().addScaledVector(tangent, -9.5).add(new THREE.Vector3(0, 4.2, 0));
            this.cameraP1.position.lerp(camPos, 0.16);
            this.cameraP1.lookAt(pt.clone().add(new THREE.Vector3(0, 1.2, 0)));
        }

        if (p2) {
            const pt = p2.mesh.position;
            const u2 = Math.max(0, Math.min(0.9999, ((p2.progress % 1.0) + 1.0) % 1.0));
            const tangent = this.curve.getTangentAt(u2).normalize();
            const camPos = pt.clone().addScaledVector(tangent, -9.5).add(new THREE.Vector3(0, 4.2, 0));
            this.cameraP2.position.lerp(camPos, 0.16);
            this.cameraP2.lookAt(pt.clone().add(new THREE.Vector3(0, 1.2, 0)));
        }
    }

    updateHUD() {
        const p1 = this.vehicles.find(v => v.id === 'P1');
        const p2 = this.vehicles.find(v => v.id === 'P2');

        const sorted = [...this.vehicles].sort((a, b) => {
            const scoreA = a.lap * 1000 + a.progress * 100;
            const scoreB = b.lap * 1000 + b.progress * 100;
            return scoreB - scoreA;
        });

        const rankP1 = sorted.findIndex(v => v.id === 'P1') + 1;
        const rankP2 = sorted.findIndex(v => v.id === 'P2') + 1;

        const rankP1El = document.getElementById('hud-p1-rank');
        if (rankP1El) rankP1El.textContent = `${rankP1}°`;

        const rankP2El = document.getElementById('hud-p2-rank');
        if (rankP2El) rankP2El.textContent = `${rankP2}°`;

        const lapP1El = document.getElementById('hud-p1-lap');
        if (lapP1El && p1) {
            lapP1El.textContent = p1.inShortcut ? '⚡ ¡Atajo Callejón!' : `Vuelta ${Math.min(p1.lap, this.totalLaps)}/${this.totalLaps}`;
            lapP1El.style.color = p1.inShortcut ? '#e67e22' : '#2c3e50';
        }

        const lapP2El = document.getElementById('hud-p2-lap');
        if (lapP2El && p2) {
            lapP2El.textContent = p2.inShortcut ? '⚡ ¡Atajo Callejón!' : `Vuelta ${Math.min(p2.lap, this.totalLaps)}/${this.totalLaps}`;
            lapP2El.style.color = p2.inShortcut ? '#e67e22' : '#2c3e50';
        }

        const speedP1 = document.getElementById('speed-bar-p1');
        if (speedP1 && p1) {
            const pct = Math.min(100, Math.floor((p1.speed / p1.maxSpeed) * 100));
            speedP1.style.width = `${pct}%`;
        }

        const speedP2 = document.getElementById('speed-bar-p2');
        if (speedP2 && p2) {
            const pct = Math.min(100, Math.floor((p2.speed / p2.maxSpeed) * 100));
            speedP2.style.width = `${pct}%`;
        }
    }

    handleRaceOver() {
        this.gameState = 'race_over';

        const pointsTable = [15, 12, 10, 8, 6, 4];
        this.vehicles.forEach((v, idx) => {
            const pts = pointsTable[idx] || 2;
            this.tournamentScores[v.id] = (this.tournamentScores[v.id] || 0) + pts;
        });

        const victoryScreen = document.getElementById('victory-screen');
        const posText = document.getElementById('victory-position');
        const pointsText = document.getElementById('victory-points');
        const descText = document.getElementById('victory-desc');
        const btnNext = document.getElementById('btn-play-again');

        const p1 = this.vehicles.find(v => v.id === 'P1');
        const isCupEnd = this.currentCupIndex >= this.cups.length - 1;

        if (posText) {
            posText.textContent = `¡Carrera Terminada! P1 terminó en ${p1.finishRank || 1}° Lugar`;
        }
        if (pointsText) {
            pointsText.textContent = `Puntuaciones Gran Prix: P1: ${this.tournamentScores['P1']} pts | P2: ${this.tournamentScores['P2']} pts`;
        }
        if (descText) {
            descText.textContent = isCupEnd
                ? '🏆 ¡GRAN CAMPEONATO FINALIZADO! ¡Felicitaciones a Kairos, Lápiz y Tornituerqui!'
                : `Siguiente circuito: ${this.cups[this.currentCupIndex + 1].name}`;
        }
        if (btnNext) {
            btnNext.textContent = isCupEnd ? '🏆 Reiniciar Torneo' : '🚀 Siguiente Circuito';
        }

        document.getElementById('game-hud').classList.add('hidden');
        if (victoryScreen) victoryScreen.classList.remove('hidden');

        if (window.soundManager) window.soundManager.playWin();
    }

    advanceTournament() {
        if (this.currentCupIndex >= this.cups.length - 1) {
            this.currentCupIndex = 0;
            for (const key in this.tournamentScores) this.tournamentScores[key] = 0;
        } else {
            this.currentCupIndex++;
        }
        this.buildTrack();
        this.startRace();
    }

    renderLoop() {
        const dt = Math.min(this.clock.getDelta(), 0.1);

        this.update(dt);
        this.updateCameras();
        this.updateParticles(dt);

        // Animated Water Waves Displacement (Main Canal)
        const time = this.clock.getElapsedTime();
        if (this.waterMesh && this.waterBaseY) {
            const posAttr = this.waterMesh.geometry.attributes.position;
            for (let i = 0; i < posAttr.count; i++) {
                const u = i / posAttr.count;
                const wave = Math.sin(u * 55.0 + time * 3.8) * Math.cos(i * 0.5 + time * 2.8) * 0.12;
                posAttr.setY(i, this.waterBaseY[i] + wave);
            }
            posAttr.needsUpdate = true;
            this.waterMesh.geometry.computeVertexNormals();
        }

        // Animated Waves for the Branching Shortcut Alley Canal
        if (this.scWaterMesh && this.scWaterBaseY) {
            const scPos = this.scWaterMesh.geometry.attributes.position;
            for (let i = 0; i < scPos.count; i++) {
                const u = i / scPos.count;
                const wave = Math.sin(u * 45.0 + time * 4.2) * Math.cos(i * 0.6 + time * 3.0) * 0.11;
                scPos.setY(i, this.scWaterBaseY[i] + wave);
            }
            scPos.needsUpdate = true;
            this.scWaterMesh.geometry.computeVertexNormals();
        }

        // Flowing Water Texture Animation (Caustics and glints drifting along the canal)
        if (this.waterTexture) {
            this.waterTexture.offset.y += dt * 0.20;
            this.waterTexture.offset.x = Math.sin(time * 0.7) * 0.035;
        }

        if (this.clouds) {
            this.clouds.forEach(c => {
                c.position.x += dt * 3.2;
                if (c.position.x > 950) c.position.x = -950;
            });
        }

        const w = window.innerWidth;
        const h = window.innerHeight;

        if (this.numPlayers === 2 && this.gameState === 'racing') {
            this.renderer.setScissorTest(true);

            // Left Viewport (Player 1)
            this.renderer.setViewport(0, 0, w / 2, h);
            this.renderer.setScissor(0, 0, w / 2, h);
            this.cameraP1.aspect = (w / 2) / h;
            this.cameraP1.updateProjectionMatrix();
            this.renderer.render(this.scene, this.cameraP1);

            // Right Viewport (Player 2)
            this.renderer.setViewport(w / 2, 0, w / 2, h);
            this.renderer.setScissor(w / 2, 0, w / 2, h);
            this.cameraP2.aspect = (w / 2) / h;
            this.cameraP2.updateProjectionMatrix();
            this.renderer.render(this.scene, this.cameraP2);

            this.renderer.setScissorTest(false);
        } else {
            this.renderer.setViewport(0, 0, w, h);
            this.cameraP1.aspect = w / h;
            this.cameraP1.updateProjectionMatrix();
            this.renderer.render(this.scene, this.cameraP1);
        }

        requestAnimationFrame(() => this.renderLoop());
    }

    onWindowResize() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.renderer.setSize(w, h);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.game3d = new BoatGame3D();
});
