/**
 * RoboForge Arena — High Precision Stick Figure Canvas Renderer
 * Renders fighting stick figures, limbs, head circles, joint pivot dots, and weapons.
 */

class CanvasRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.scale = 50.0; // 50 pixels per meter
    }

    worldToScreen(x, y) {
        const sx = this.canvas.width / 2.0 + x * this.scale;
        const sy = (this.canvas.height - 80.0) - y * this.scale;
        return { x: sx, y: sy };
    }

    clear() {
        this.ctx.fillStyle = '#121319';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw Arena Floor Ground at y = 0.5m
        const groundPos = this.worldToScreen(0, 0.5);
        this.ctx.beginPath();
        this.ctx.moveTo(0, groundPos.y);
        this.ctx.lineTo(this.canvas.width, groundPos.y);
        this.ctx.strokeStyle = '#3f3f46';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }

    drawBody(body, index) {
        const p = this.worldToScreen(body.pos[0], body.pos[1]);

        this.ctx.save();
        this.ctx.translate(p.x, p.y);
        this.ctx.rotate(-body.angle);

        // Ground / Static environment bodies
        if (body.is_static) {
            this.ctx.fillStyle = '#27272a';
            this.ctx.strokeStyle = '#3f3f46';
            this.ctx.lineWidth = 1;
            if (body.shape_type === 'polygon' && body.vertices) {
                this.ctx.beginPath();
                body.vertices.forEach((v, i) => {
                    const vx = v[0] * this.scale;
                    const vy = -v[1] * this.scale;
                    if (i === 0) this.ctx.moveTo(vx, vy);
                    else this.ctx.lineTo(vx, vy);
                });
                this.ctx.closePath();
                this.ctx.fill();
                this.ctx.stroke();
            }
            this.ctx.restore();
            return;
        }

        // Dynamic Robot Fighter Bodies: Robot A (Red) vs Robot B (Blue)
        const isRed = (body.pos[0] < 0 || index <= 6);
        const fillStyle = isRed ? '#ef4444' : '#3b82f6';
        const strokeStyle = isRed ? '#dc2626' : '#2563eb';

        this.ctx.fillStyle = fillStyle;
        this.ctx.strokeStyle = strokeStyle;
        this.ctx.lineWidth = 2.5;

        if (body.shape_type === 'circle') {
            const radiusPx = body.radius * this.scale;
            this.ctx.beginPath();
            this.ctx.arc(0, 0, radiusPx, 0, Math.PI * 2);
            this.ctx.fill();
        } else if (body.shape_type === 'polygon' && body.vertices) {
            // Draw sleek limb / torso stick segment
            this.ctx.beginPath();
            body.vertices.forEach((v, i) => {
                const vx = v[0] * this.scale;
                const vy = -v[1] * this.scale;
                if (i === 0) this.ctx.moveTo(vx, vy);
                else this.ctx.lineTo(vx, vy);
            });
            this.ctx.closePath();
            this.ctx.fill();
            this.ctx.stroke();

            // Draw boxing glove fist / weapon tip at extremity
            const maxV = body.vertices.reduce((max, v) => (Math.abs(v[0]) > Math.abs(max[0]) ? v : max), body.vertices[0]);
            const tipX = maxV[0] * this.scale;
            const tipY = -maxV[1] * this.scale;

            if (Math.abs(maxV[0]) > 0.2) {
                this.ctx.beginPath();
                this.ctx.arc(tipX, tipY, 7, 0, Math.PI * 2);
                this.ctx.fillStyle = isRed ? '#fca5a5' : '#93c5fd';
                this.ctx.fill();
            }
        }

        this.ctx.restore();
    }

    drawJoints(joints) {
        if (!joints) return;

        joints.forEach(j => {
            const p1 = this.worldToScreen(j.anchor_a[0], j.anchor_a[1]);
            const p2 = this.worldToScreen(j.anchor_b[0], j.anchor_b[1]);

            // Draw joint connection link line
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Draw joint pivot dot
            [p1, p2].forEach(p => {
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                this.ctx.fillStyle = '#fca5a5';
                this.ctx.fill();
            });
        });
    }

    render(state) {
        this.clear();

        if (state.bodies) {
            state.bodies.forEach((b, idx) => this.drawBody(b, idx));
        }

        if (state.joints) {
            this.drawJoints(state.joints);
        }
    }
}
