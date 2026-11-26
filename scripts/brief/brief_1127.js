// 一周简报（4 页）。数据截至 11-27 00:17（评测机快照）。每个数字的出处见 Status 11-27 的核对记录。
const pptxgen = require('/opt/npm-tools/node_modules/pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/9701b851-5d17-4514-adcc-8bed2fe5a792_f563679b-85d8-4e38-bf0a-ca2eb5fae4cd/pptx/scripts/apply_theme.js');

const OUT = process.argv[2] || 'brief.pptx';
const CUTOFF = process.argv[3] || '11-27 00:17';
const FONT = 'Microsoft YaHei';

const THEME = {
  name: 'MemBrief',
  headFontFace: FONT,
  bodyFontFace: FONT,
  colors: {
    dk1: '1B2A34', lt1: 'FFFFFF', dk2: '2F4858', lt2: 'EEF2F4',
    accent1: '1F7A8C', accent2: 'E07A1F', accent3: '2E7D4F', accent4: '6B7785',
    accent5: 'B23A2E', accent6: '7B5EA7', hlink: '1F7A8C', folHlink: '6B4E71',
  },
};
// hex copies for hex-only options
const H = THEME.colors;
const MUTED = '5B6B77';
const GRID = 'D5DCE1';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
pres.title = '一周简报：打榜进度';
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: H.lt1 },
  margin: [0.4, 0.5, 0.4, 0.5],
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.32, w: 12.33, h: 0.78,
        fontFace: FONT, fontSize: 30, bold: true, color: C.text1, align: 'left', valign: 'middle', margin: 0 },
      text: '' } },
  ],
});

// ---------- helpers ----------
const T = (text, o = {}) => ({ text, options: { fontFace: FONT, ...o } });

function keyPoints(slide, x, y, w, items, opt = {}) {
  // numbered circles + sentences, stacked vertically
  const size = opt.fontSize || 14;
  const gap = opt.gap || 0.18;
  const heights = opt.heights; // per item heights (inches)
  let cy = y;
  const start = opt.start || 1;
  items.forEach((txt, j) => {
    const i = j + start - 1;
    const h = heights[j];
    slide.addShape(pres.shapes.OVAL, { x, y: cy + 0.04, w: 0.32, h: 0.32, fill: { color: C.accent1 }, line: { color: C.accent1 },
      objectName: `kp-dot-${i + 1}` });
    slide.addText(String(i + 1), { x, y: cy + 0.04, w: 0.32, h: 0.32, fontFace: FONT, fontSize: 12, bold: true,
      color: C.background1, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: `kp-num-${i + 1}` });
    slide.addText(txt, { x: x + 0.45, y: cy, w: w - 0.45, h, fontFace: FONT, fontSize: size, color: C.text1,
      align: 'left', valign: 'top', margin: 0, lineSpacingMultiple: 1.15, isTextBox: true, objectName: `kp-text-${i + 1}` });
    cy += h + gap;
  });
  return cy;
}

function panel(slide, x, y, w, h, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 },
    line: { color: C.background2 }, objectName: name });
}

// table cell builders
const hdr = (text, o = {}) => ({ text, options: { bold: true, color: C.background1, fill: { color: C.text2 }, fontFace: FONT,
  fontSize: 11, valign: 'middle', align: 'center', ...o } });
const cell = (text, o = {}) => ({ text, options: { fontFace: FONT, fontSize: 12, color: C.text1, valign: 'middle', ...o } });

// ====================== 第 1 页 ======================
{
  const s = pres.addSlide({ masterName: 'CONTENT' });
  s.addText('打榜现状：1 个超过、3 个持平、5 个没到', { placeholder: 'title' });

  const tag = (label) => {
    const map = {
      '超过': { fill: H.accent3, color: 'FFFFFF' },
      '持平': { fill: H.accent1, color: 'FFFFFF' },
      '没到，接近': { fill: 'F3D9B1', color: H.dk1 },
      '没到': { fill: 'F2D4D0', color: H.dk1 },
    }[label];
    return { text: label, options: { fontFace: FONT, fontSize: 12, bold: true, align: 'center', valign: 'middle',
      color: map.color, fill: { color: map.fill } } };
  };
  const group = (text) => [{ text, options: { colspan: 6, fontFace: FONT, fontSize: 12, bold: true, color: C.accent1,
    fill: { color: C.background2 }, valign: 'middle', margin: [0, 0, 0, 0.08] } }];
  const row = (task, sota, ours, ver, diff, cls) => [
    cell(task, { bold: true }), cell(sota, { align: 'center' }), cell(ours, { align: 'center', bold: true }),
    cell(ver, { fontSize: 11 }), cell(diff, { align: 'center' }), tag(cls)];

  const rows = [
    [hdr('任务'), hdr('纯 WAM 最高\n（各家论文自报）'), hdr('我们最好\n（官方 100 个场景，评一遍）'), hdr('用的版本'),
     hdr('差'), hdr('归类\n（差 3 分以内算持平）')],
    group('记“自己做过的事”'),
    row('放回', '100', '100', '三帧、身体记录都是 100', '0', '持平'),
    row('交换', '100', '100', '身体记录（三帧 56）', '0', '持平'),
    row('盖方块', '98', '99', '身体记录（三帧 72）', '+1', '持平'),
    row('试电池', '48', '91', '三帧（身体记录同为 91，无历史 54）', '+43', '超过'),
    row('重排', '100', '93', '身体记录 + 及时写入 + 按下前加权（训了一次）', '-7', '没到，接近'),
    row('排序', '100', '77', '三帧（身体记录 65）', '-23', '没到'),
    group('记“只见过一次的画面细节”'),
    row('T 块', '94–97', '51', '三帧（时钟 51，身体记录 49）', '-43 至 -46', '没到'),
    row('找同款', '27–28', '16', '身体记录（三帧 13，无历史 15；五选一盲抓 20）', '-11 至 -12', '没到'),
    group('两样都要'),
    row('按按钮', '87', '26', '身体记录（快写入版）', '-61', '没到'),
  ];
  const colW = [0.85, 1.2, 1.45, 3.0, 1.25, 1.2]; // 8.95
  const rowH = [0.62, 0.3, 0.38, 0.38, 0.38, 0.38, 0.45, 0.38, 0.3, 0.38, 0.45, 0.3, 0.38];
  s.addTable(rows, { x: 0.5, y: 1.3, w: colW.reduce((a, b) => a + b, 0), colW, rowH,
    border: { type: 'solid', pt: 0.75, color: GRID }, fontFace: FONT, objectName: 'leaderboard-table' });

  // right panel: key points
  const px = 9.75, pw = 3.08, py = 1.3, ph = 5.45;
  panel(s, px, py, pw, ph, 'kp-panel');
  s.addText('要点', { x: px + 0.25, y: py + 0.18, w: 2, h: 0.35, fontFace: FONT, fontSize: 15, bold: true, color: C.accent1,
    margin: 0, isTextBox: true, objectName: 'kp-head' });
  keyPoints(s, px + 0.25, py + 0.68, pw - 0.45, [
    '记“自己做过的事”的六个任务，四个已到同类最好；重排本周 62 → 93，差 7 分；排序差 23 分。',
    '记“只见过一次的画面细节”的任务都没到；找同款上同类模型自己也只有 27–28，五选一盲抓是 20。',
    '试电池超过 43 分，靠的是三帧短记忆，不是身体记录。',
  ], { fontSize: 14, heights: [1.35, 1.35, 0.72], gap: 0.22 });
  s.addText(`数据截至 ${CUTOFF}`, { x: px + 0.25, y: py + ph - 0.5, w: pw - 0.45, h: 0.3, fontFace: FONT, fontSize: 11,
    color: MUTED, margin: 0, isTextBox: true, objectName: 'cutoff' });
}

// ====================== 第 2 页 ======================
{
  const s = pres.addSlide({ masterName: 'CONTENT' });
  s.addText('缺陷和观察：模型只读最便宜的那条线索', { placeholder: 'title' });

  const labels = ['0', '64', '256', '1024'];
  const common = {
    x: 0.5, y: 1.3, w: 5.3, h: 3.75,
    showTitle: true, title: '交换任务：中途停顿后的成功数（满分 50）', titleFontFace: FONT, titleFontSize: 13, titleColor: H.dk1,
    showLegend: true, legendPos: 'b', legendFontFace: FONT, legendFontSize: 11, legendColor: H.dk1,
    catAxisTitle: '中途停顿的帧数', showCatAxisTitle: true, catAxisTitleFontFace: FONT, catAxisTitleFontSize: 11,
    catAxisTitleColor: MUTED, catAxisLabelFontFace: FONT, catAxisLabelFontSize: 11, catAxisLabelColor: MUTED,
    valAxisMinVal: -10, valAxisMaxVal: 60, valAxisMajorUnit: 10, valAxisHidden: true,
    valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
    showValue: true, dataLabelFontFace: FONT, dataLabelFontSize: 12, dataLabelColor: H.dk1, dataLabelFormatCode: '0',
    displayBlanksAs: 'gap', objectName: 'pause-chart',
  };
  s.addChart([
    { type: pres.charts.LINE, data: [{ name: '按时间记', labels, values: [50, 50, 7, 7] }],
      options: { chartColors: [H.accent2], lineSize: 3, lineDataSymbol: 'circle', lineDataSymbolSize: 9, dataLabelPosition: 'b' } },
    { type: pres.charts.LINE, data: [{ name: '按身体事件记（256 帧未测）', labels, values: [50, 50, null, 50] }],
      options: { chartColors: [H.accent1], lineSize: 3, lineDataSymbol: 'diamond', lineDataSymbolSize: 10, dataLabelPosition: 't' } },
  ], common);

  const rows = [
    [hdr('模型（任务）'), hdr('测试时改了什么'), hdr('结果'), hdr('说明')],
    [cell('按时间记（交换）', { bold: true }), cell('时间戳拨快 1.5 倍、拨慢一半、抹成同一个值；或整段关掉'),
     cell('都是 0/50', { align: 'center' }), cell('在读时间戳，离了它不行')],
    [cell('按时间记（交换）', { bold: true }), cell('历史里的身体读数换成当前的，时间戳不动'),
     cell('50/50', { align: 'center' }), cell('不读内容')],
    [cell('身体记录（交换）', { bold: true }), cell('关掉记录；只留最近 8 条'),
     cell('0/50；0/50', { align: 'center' }), cell('在读记录')],
    [cell('三帧（试电池）', { bold: true }), cell('遮首帧；遮两张近帧（不遮时 45/50）'),
     cell('45/50；14/50', { align: 'center' }), cell('读的是近帧')],
    [cell('三帧（找同款）', { bold: true }), cell('把首帧换成别的场景的'),
     cell('动作变化 < 2%', { align: 'center' }), cell('不看参照物，在背场景')],
  ];
  const colW = [1.75, 2.3, 1.43, 1.3]; // 6.78
  s.addText('测试时改掉一条线索，看行为变不变（交换不改时 50/50）', { x: 6.05, y: 1.3, w: 6.78, h: 0.35, fontFace: FONT,
    fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: 'intervention-head' });
  s.addTable(rows, { x: 6.05, y: 1.68, w: 6.78, colW, rowH: [0.4, 0.75, 0.62, 0.45, 0.62, 0.5],
    border: { type: 'solid', pt: 0.75, color: GRID }, fontFace: FONT, objectName: 'intervention-table' });

  panel(s, 0.5, 5.45, 12.33, 1.4, 'kp-panel');
  const kx = [0.75, 6.85];
  const kp = [
    '给钟读钟，给记录读记录，找同款上背训练场景：模型只读训练里最便宜的那条线索，并且完全依赖它。',
    '按时间记的，停顿 256 帧后只剩 7/50；按身体事件记的不受影响，而且学得快：都只训 10 轮，78 对 43（满分 100）。',
  ];
  kp.forEach((t, i) => keyPoints(s, kx[i], 5.68, 5.75, [t], { fontSize: 14, heights: [1.15], start: i + 1 }));
}

// ====================== 第 3 页 ======================
{
  const s = pres.addSlide({ masterName: 'CONTENT' });
  s.addText('设计和结果：对上病灶，分数才动（重排 29 → 93）', { placeholder: 'title' });

  const labels = ['三帧', '加身体记录', '再把记录写早', '再加按下前加权'];
  s.addChart(pres.charts.BAR, [
    { name: '成功', labels, values: [29, 62, 47, 93] },
    { name: '重复按', labels, values: [34, 18, 27, 0] },
    { name: '漏按', labels, values: [33, 17, 15, 4] },
    { name: '其他（挪错块、按早了）', labels, values: [4, 3, 11, 3] },
  ], {
    x: 0.5, y: 1.3, w: 6.6, h: 5.6, barDir: 'bar', barGrouping: 'stacked', barGapWidthPct: 55,
    catAxisOrientation: 'maxMin',
    chartColors: [H.accent3, H.accent5, H.accent6, H.accent4],
    showTitle: true, title: '重排：100 个回合的结局', titleFontFace: FONT, titleFontSize: 13, titleColor: H.dk1,
    showLegend: true, legendPos: 'b', legendFontFace: FONT, legendFontSize: 11, legendColor: H.dk1,
    catAxisLabelFontFace: FONT, catAxisLabelFontSize: 12, catAxisLabelColor: H.dk1,
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 100, valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
    showValue: true, dataLabelPosition: 'ctr', dataLabelFontFace: FONT, dataLabelFontSize: 12, dataLabelFontBold: true,
    dataLabelColor: 'FFFFFF', dataLabelFormatCode: '0;;;', objectName: 'rearrange-chart',
  });

  s.addText('其余记“自己做过的事”的任务（成功数，满分 100）', { x: 7.45, y: 1.3, w: 5.4, h: 0.35, fontFace: FONT,
    fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: 'others-head' });
  const rows = [
    [hdr('任务'), hdr('无历史'), hdr('三帧'), hdr('身体记录'), hdr('纯 WAM 最高\n（自报）')],
    [cell('交换', { bold: true }), cell('23', { align: 'center' }), cell('56', { align: 'center' }), cell('100', { align: 'center', bold: true }), cell('100', { align: 'center' })],
    [cell('放回', { bold: true }), cell('0', { align: 'center' }), cell('100', { align: 'center' }), cell('100', { align: 'center', bold: true }), cell('100', { align: 'center' })],
    [cell('盖方块', { bold: true }), cell('还没评', { align: 'center', color: MUTED }), cell('72', { align: 'center' }), cell('99', { align: 'center', bold: true }), cell('98', { align: 'center' })],
    [cell('试电池', { bold: true }), cell('54', { align: 'center' }), cell('91', { align: 'center' }), cell('91', { align: 'center', bold: true }), cell('48', { align: 'center' })],
  ];
  s.addTable(rows, { x: 7.45, y: 1.72, w: 5.38, colW: [1.1, 0.95, 0.95, 1.08, 1.3], rowH: [0.58, 0.38, 0.38, 0.38, 0.38],
    border: { type: 'solid', pt: 0.75, color: GRID }, fontFace: FONT, objectName: 'others-table' });

  panel(s, 7.45, 4.1, 5.38, 2.85, 'kp-panel');
  keyPoints(s, 7.65, 4.25, 5.05, [
    '身体记录把“按没按过、搬到第几步”的错减半：重排 29 → 62，交换 56 → 100，盖方块 72 → 99。',
    '只把记录写早没有用（33，另训一次 47）；再把“按下去之前那一小段”的训练加权，漏按 15 → 4，重复按 27 → 0，成功 93。',
    '93 只训了一次、评了一遍；其中多少来自记忆、多少来自“按”练得更足，两格对照 11-28 出数。',
  ], { fontSize: 13, heights: [0.62, 0.85, 0.62], gap: 0.12 });
}

// ====================== 第 4 页 ======================
{
  const s = pres.addSlide({ masterName: 'CONTENT' });
  s.addText('没到的五个任务：试过什么、卡在哪、下一步', { placeholder: 'title' });

  const c = (t, o = {}) => cell(t, { fontSize: 12, valign: 'middle', ...o });
  const rows = [
    [hdr('任务（差）'), hdr('已失败（原因）'), hdr('有希望 / 快成了'), hdr('还没评'), hdr('下一步')],
    [c('重排（-7）', { bold: true }), c('只把记录写早：33 对 62'), c('快成了：加按下前加权，93', { color: H.accent3, bold: true }),
     c('第二个种子；记忆占多少的两格对照'), c('两样今天开训，11-28 看对照')],
    [c('排序（-23）', { bold: true }), c('身体记录 65，低于三帧 77，差距的区间含 0'),
     c('有希望：两版错在不同场景，至少一版做对 96 个', { color: H.accent1, bold: true }),
     c('及时写入版（今天判）、无历史版'), c('先拆每个回合的按键顺序，再定训练')],
    [c('T 块（-43）', { bold: true }), c('换历史形式 49–51；训练加倍 36 对 39、38 对 49'), c('暂无', { color: MUTED }),
     c('和放回、交换合训（11-28 出数）'), c('先查放的位置读的是哪条线索')],
    [c('找同款（-12）', { bold: true }), c('放大参照物 11、预测抓取姿态 11、递上“哪个最像”12：模型背场景，不看首帧；200 个场景仍 15 对 13'),
     c('暂无', { color: MUTED }), c('800 个场景（今天训完后评）'), c('同一张桌面换参照物的新数据：生成前的检查没通过，先查原因，不进训练')],
    [c('按按钮（-61）', { bold: true }), c('五种记录写法 8–26；次数写进指令 22 对 17'), c('暂无', { color: MUTED }),
     c('第二个基准的计数任务'), c('12-14 前到不了 87 就如实报告')],
  ];
  s.addTable(rows, { x: 0.5, y: 1.3, w: 12.33, colW: [1.55, 3.75, 2.55, 2.2, 2.28],
    rowH: [0.42, 0.62, 0.72, 0.62, 0.72, 0.62], border: { type: 'solid', pt: 0.75, color: GRID }, fontFace: FONT,
    objectName: 'gap-table' });

  panel(s, 0.5, 5.35, 12.33, 1.45, 'kp-panel');
  keyPoints(s, 0.75, 5.58, 6.2, [
    '失败的方向有一个共同点：在同样的示范上多给输入、多加监督（放大图、抓取姿态预测、“哪个最像”、把次数写进指令），成绩都没动；查过的“哪个最像”，模型根本没读。',
  ], { fontSize: 14, heights: [1.15] });
  keyPoints(s, 7.1, 5.58, 5.5, [
    '下周的规矩：先查清每个任务上模型读的是哪条线索，再开训练。',
  ], { fontSize: 14, heights: [1.15], start: 2 });
}

pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT, THEME);
  console.log('written', OUT);
});
