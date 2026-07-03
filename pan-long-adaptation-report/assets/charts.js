// assets/charts.js - ECharts initialization for 《攀龙》adaptation report
(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart: Volume Word Count Distribution ---
  var chartVolumes = echarts.init(document.getElementById('chart-volumes'), null, { renderer: 'svg' });
  chartVolumes.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      formatter: function(params) {
        return params[0].name + '<br/>字数：' + params[0].value + ' 万字';
      }
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['入府为妾', '后院争锋', '风云暗涌', '步步为营', '宫闱惊变', '凤临天下', '番外篇'],
      axisLabel: { color: muted, fontSize: 11, rotate: 20 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '万字',
      nameTextStyle: { color: muted, fontSize: 11 },
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false }
    },
    series: [{
      type: 'bar',
      data: [10, 16, 16, 20, 18, 18, 7],
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: accent },
          { offset: 1, color: accent + '66' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}万',
        color: ink,
        fontSize: 12,
        fontWeight: 'bold'
      }
    }]
  });
  window.addEventListener('resize', function() { chartVolumes.resize(); });

  // --- Chart: Character Frequency TOP15 ---
  var chartChars = echarts.init(document.getElementById('chart-chars'), null, { renderer: 'svg' });
  chartChars.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        return params[0].name + '<br/>出场次数：' + params[0].value.toLocaleString();
      }
    },
    grid: { left: '3%', right: '8%', bottom: '5%', top: '5%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false }
    },
    yAxis: {
      type: 'category',
      data: ['冯牧', '罗达', '仇引', '世子', '丁香', '金粟', '娄凌云', '润儿', '俞氏', '王妃', '定安王', '薛氏', '衡哥儿', '宗凛', '宓之'],
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false },
      inverse: true
    },
    series: [{
      type: 'bar',
      data: [200, 220, 260, 280, 310, 420, 480, 520, 590, 680, 746, 951, 1647, 7838, 8777],
      barWidth: '55%',
      itemStyle: {
        color: function(params) {
          var idx = params.dataIndex;
          if (idx >= 13) return accent;       // 宓之 - protagonist
          if (idx >= 12) return accent2;      // 宗凛 - protagonist
          if (idx >= 11) return accent2 + 'cc'; // 衡哥儿 - main supporting
          if (idx >= 9) return accent + '88';  // 薛氏/定安王/王妃 - main
          return muted + '88';
        },
        borderRadius: [0, 4, 4, 0]
      },
      label: {
        show: true,
        position: 'right',
        formatter: function(p) { return p.value.toLocaleString(); },
        color: ink,
        fontSize: 11
      }
    }]
  });
  window.addEventListener('resize', function() { chartChars.resize(); });

})();
