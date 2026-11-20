const { createCanvas } = require('@napi-rs/canvas');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const ink = '#1b312b';
const pine = '#163b31';
const mint = '#b9ef8b';
const paper = '#f9f8f0';

function stroke(ctx, points, color, weight) {
  ctx.strokeStyle = color;
  ctx.lineWidth = weight;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  points.forEach(([x, y], index) => index ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.stroke();
}

function arrow(ctx, points, color, weight, tip) {
  stroke(ctx, points, color, weight);
  const [endX, endY] = points[points.length - 1];
  const [prevX, prevY] = points[points.length - 2];
  const dx = Math.sign(endX - prevX);
  const dy = Math.sign(endY - prevY);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(endX + dx * tip * .88, endY + dy * tip * .88);
  ctx.lineTo(endX - dx * tip * .36 - dy * tip * .66, endY - dy * tip * .36 + dx * tip * .66);
  ctx.lineTo(endX - dx * tip * .36 + dy * tip * .66, endY - dy * tip * .36 - dx * tip * .66);
  ctx.closePath();
  ctx.fill();
}

function circle(ctx, x, y, radius, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function fillRoundRect(ctx, x, y, width, height, radius, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, radius);
  ctx.fill();
}

function write(canvas, name) {
  fs.writeFileSync(path.join(root, name), canvas.toBuffer('image/png'));
}

function drawMark(ctx, size) {
  ctx.save();
  ctx.scale(size / 100, size / 100);
  fillRoundRect(ctx, 0, 0, 100, 100, 22, pine);
  for (let y = 16; y < 90; y += 10) {
    for (let x = 16; x < 90; x += 10) circle(ctx, x, y, .65, '#386252');
  }
  arrow(ctx, [[24, 74], [24, 48], [49, 48], [49, 26], [71, 26]], mint, 8, 11);
  arrow(ctx, [[76, 49], [76, 74], [53, 74]], '#f8f5df', 6, 9);
  ctx.restore();
}

const icon = createCanvas(512, 512);
const iconContext = icon.getContext('2d');
iconContext.fillStyle = pine;
iconContext.fillRect(0, 0, 512, 512);
drawMark(iconContext, 512);
write(icon, 'publish/icon.png');

const mark = createCanvas(96, 96);
drawMark(mark.getContext('2d'), 96);
write(mark, 'dist/icons/mark.png');

const symbols = {
  hint(ctx) {
    const gold = '#8e5a09';
    ctx.strokeStyle = gold;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(9, 17);
    ctx.bezierCurveTo(9, 14, 6, 14, 6, 10);
    ctx.bezierCurveTo(6, 2, 18, 2, 18, 10);
    ctx.bezierCurveTo(18, 14, 15, 14, 15, 17);
    ctx.closePath();
    ctx.fillStyle = '#ffda77';
    ctx.fill();
    ctx.stroke();
    stroke(ctx, [[10, 20], [14, 20]], gold, 2);
    stroke(ctx, [[12, 1], [12, 2]], gold, 1.5);
    stroke(ctx, [[2.5, 5], [3.7, 6]], gold, 1.5);
    stroke(ctx, [[21.5, 5], [20.3, 6]], gold, 1.5);
  },
  magnet(ctx) {
    ctx.strokeStyle = '#54458e';
    ctx.lineWidth = 5;
    ctx.lineCap = 'butt';
    ctx.beginPath();
    ctx.moveTo(5, 4);
    ctx.lineTo(5, 12);
    ctx.arc(12, 12, 7, Math.PI, 0, true);
    ctx.lineTo(19, 4);
    ctx.stroke();
    stroke(ctx, [[5, 4], [5, 7]], '#a594eb', 5);
    stroke(ctx, [[19, 4], [19, 7]], '#a594eb', 5);
  },
  erase(ctx) {
    ctx.save();
    ctx.translate(12, 11);
    ctx.rotate(-Math.PI / 4);
    fillRoundRect(ctx, -9, -5.5, 18, 11, 2.3, '#b25145');
    fillRoundRect(ctx, -7, -3.5, 15, 7, 1.2, '#f6ab98');
    ctx.fillStyle = '#f9dfd1';
    ctx.fillRect(-7, -3.5, 5.5, 7);
    ctx.restore();
    stroke(ctx, [[10.5, 20], [21, 20]], '#b25145', 1.8);
  },
  settings(ctx) {
    for (let i = 0; i < 3; i++) {
      const y = 5 + i * 7;
      stroke(ctx, [[3, y], [21, y]], ink, 1.7);
      circle(ctx, i === 1 ? 15 : 8, y, 3, paper);
      ctx.lineWidth = 1.6;
      ctx.strokeStyle = ink;
      ctx.stroke();
    }
  },
  restart(ctx) {
    ctx.lineWidth = 2.2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = ink;
    ctx.beginPath();
    ctx.arc(12, 12, 7, -2.4, 2.54);
    ctx.stroke();
    stroke(ctx, [[4.7, 4.8], [4.7, 9], [9, 9]], ink, 2);
  },
  reset(ctx) {
    stroke(ctx, [[9, 4], [4, 4], [4, 9]], ink, 1.8);
    stroke(ctx, [[15, 4], [20, 4], [20, 9]], ink, 1.8);
    stroke(ctx, [[4, 15], [4, 20], [9, 20]], ink, 1.8);
    stroke(ctx, [[20, 15], [20, 20], [15, 20]], ink, 1.8);
  },
  heart(ctx) {
    ctx.fillStyle = '#c75d52';
    ctx.beginPath();
    ctx.moveTo(12, 21);
    ctx.bezierCurveTo(8, 17, 2.5, 13.6, 2.5, 8.3);
    ctx.bezierCurveTo(2.5, 3, 9, 1.6, 12, 6);
    ctx.bezierCurveTo(15, 1.6, 21.5, 3, 21.5, 8.3);
    ctx.bezierCurveTo(21.5, 13.6, 16, 17, 12, 21);
    ctx.fill();
  }
};

for (const [name, draw] of Object.entries(symbols)) {
  const canvas = createCanvas(72, 72);
  const ctx = canvas.getContext('2d');
  ctx.scale(3, 3);
  draw(ctx);
  write(canvas, 'dist/icons/' + name + '.png');
}

const cover = createCanvas(768, 1024);
const ctx = cover.getContext('2d');
ctx.fillStyle = '#f1f2e6';
ctx.fillRect(0, 0, 768, 1024);
for (let y = 26; y < 1024; y += 29) {
  for (let x = 22; x < 768; x += 29) circle(ctx, x, y, 1.6, '#d5ddcd');
}
ctx.textAlign = 'center';
ctx.fillStyle = ink;
ctx.font = '700 83px "PingFang SC", sans-serif';
ctx.fillText('箭头画谜', 384, 177);
ctx.save();
ctx.translate(146, 246);
drawMark(ctx, 476);
ctx.restore();
ctx.font = '600 35px "PingFang SC", sans-serif';
ctx.fillText('按顺序解开箭头', 384, 843);
ctx.fillStyle = '#53685f';
ctx.font = '500 24px "PingFang SC", sans-serif';
ctx.fillText('120 道解堵谜题', 384, 909);
write(cover, 'publish/cover.png');
