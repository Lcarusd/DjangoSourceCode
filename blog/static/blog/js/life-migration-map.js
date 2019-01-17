var dom = document.getElementById("geo");
var myChart = echarts.init(dom);
var app = {};
option = null;
var geoCoordMap = {
    '上海': [121.4648,31.2891],
    '异域': [87.9236,43.5883],
    '传媒': [116.4551,40.2539],
    '熊猫': [103.9526,30.7617],
    '无锡': [120.3442,31.5527],
    '南下': [119.5313,29.8773],
    '根脉': [117.323,34.8926],
    '学思': [114.3896,30.6628],
    '与父': [120.564,29.7565],
    '吴江': [120.6519,31.3989],
    '初见': [109.1162,34.2004],
    '长春': [125.8154,44.2584],
    '长沙': [113.0823,28.2568],
    '青岛': [120.4651,36.3373],
    '佛造像': [94.7869,40.1710],
    '太白山': [107.9015, 34.0933],
    '红河': [103.3756, 23.3642, ]
};

var SZData = [
    [{name:'吴江'},{name:'传媒',value:60}],
    [{name:'吴江'},{name:'学思',value:70}],
    [{name:'吴江'},{name:'根脉',value:80}],
    [{name:'吴江'},{name:'异域',value:20}],
    [{name:'吴江'},{name:'与父',value:40}],
];

var ZZData = [
    [{name:'根脉'},{name:'吴江',value:100}],
];

var WHData = [
    [{name:'学思'},{name:'佛造像',value:70}],
    [{name:'学思'},{name:'初见',value:110}],
];

var XAData = [
    [{name:'初见'},{name:'熊猫',value:70}],
    [{name:'初见'},{name:'红河',value:70}],
];

var planePath = 'path://M1705.06,1318.313v-89.254l-319.9-221.799l0.073-208.063c0.521-84.662-26.629-121.796-63.961-121.491c-37.332-0.305-64.482,36.829-63.961,121.491l0.073,208.063l-319.9,221.799v89.254l330.343-157.288l12.238,241.308l-134.449,92.931l0.531,42.034l175.125-42.917l175.125,42.917l0.531-42.034l-134.449-92.931l12.238-241.308L1705.06,1318.313z';

var convertData = function (data) {
    var res = [];
    for (var i = 0; i < data.length; i++) {
        var dataItem = data[i];
        var fromCoord = geoCoordMap[dataItem[0].name];
        var toCoord = geoCoordMap[dataItem[1].name];
        if (fromCoord && toCoord) {
            res.push({
                fromName: dataItem[0].name,
                toName: dataItem[1].name,
                coords: [fromCoord, toCoord]
            });
        }
    }
    return res;
};

var color = ['#a6c84c', '#ffa022', '#46bee9'];
var series = [];

[['吴江', SZData], ['根脉', ZZData], ['学思', WHData], ['初见', XAData]].forEach(function (item, i) {

    series.push({
        name: item[0],
        type: 'lines',
        zlevel: 5,
        effect: {
            show: true,
            period: 6,
            trailLength: 0.7,
            color: '#fff',
            symbolSize: 4
        },
        lineStyle: {
            normal: {
                color: color[i],
                width: 0,
                curveness: 0.2
            }
        },
        data: convertData(item[1])
    },

    {
        name: item[0],
        type: 'lines',
        zlevel: 2,
        symbol: ['none', 'arrow'],
        symbolSize: 10,
        effect: {
            show: true,
            period: 6,
            trailLength: 0,
            symbol: planePath,
            symbolSize: 15
        },
        lineStyle: {
            normal: {
                color: color[i],
                width: 1,
                opacity: 0.6,
                curveness: 0.2
            }
        },
        data: convertData(item[1])
    },

    {
        name: item[0],
        type: 'effectScatter',
        coordinateSystem: 'geo',
        zlevel: 2,
        rippleEffect: {
            brushType: 'stroke'
        },
        label: {
            normal: {
                show: true,
                position: 'right',
                formatter: '{b}'
            }
        },
        symbolSize: function (val) {
            return val[2] / 8;
        },
        itemStyle: {
            normal: {
                color: color[i]
            }
        },

        data: item[1].map(function (dataItem) {
            return {
                name: dataItem[1].name,
                value: geoCoordMap[dataItem[1].name].concat([dataItem[1].value])
            };
        })

    });
});

option = {
    backgroundColor: '#404a59',
    title : {
        text: '行迹图',
        subtext: '仅统计重要节点与精彩时刻',
        left: 'center',
        textStyle : {
            color: '#fff',
            fontSize:28
        },
        link: 'http://188.131.177.190/',
        padding: [30, 0, 0, 0],
    },
    tooltip : {
        trigger: 'item'
    },
    legend: {
        orient: 'vertical',
        top: 'bottom',
        left: 'right',
        data:['吴江'],
        textStyle: {
            color: '#fff'
        },
        selectedMode: 'single'
    },
    geo: {
        map: 'china',
        label: {
            emphasis: {
                show: false
            }
        },
        roam: true,
        itemStyle: {
            normal: {
                areaColor: '#323c48',
                borderColor: '#404a59'
            },
            emphasis: {
                areaColor: '#2a333d'
            }
        }
    },
    series: series
};
if (option && typeof option === "object") {
    myChart.setOption(option, true);
}