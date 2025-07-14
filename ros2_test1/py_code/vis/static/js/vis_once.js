const data_times = 20000-1;

let socket = io();
socket.emit("oram_join");
socket.on("oram_data", function (data) {
    console.log(`Connected to server: ${JSON.stringify(data)}`);
    let leftNodesRaw = data.left_nodes;
    let rightNodesRaw = data.right_nodes;
    process_nodes(leftNodesRaw, rightNodesRaw);
    update_vis(nodes, null);
    socket.emit("oram_update_edges", {time:0,edge:null});
});

let time = 0
let edge_tmp = null;
function add_update_edge(num,edge=edge_tmp) {
    edge_tmp = edge;
    time += num;
    if (time < 0) {
        time = 0;
        return;
    }

    if (time > data_times) {
        time = data_times;
        return;
    }
    edge_time = document.getElementById('time');
    edge_time.innerText = `${time}/${data_times}`;
    datas = {time:time,edge:edge};
    socket.emit("oram_update_edges", datas);

}

function goto_round(){
    // get the value from the input field
    let roundId = document.getElementById('round_id').value;
    console.log(`goto round: ${roundId}`);

    roundId = parseInt(roundId);
    if (isNaN(roundId) || roundId < 0 || roundId > data_times) {
        console.log("Invalid round ID.");
        return;
    }

    add_update_edge(roundId-time, edge_tmp);

}

socket.on("oram_update_edges", function (data) {
    console.log(`edge update: ${JSON.stringify(data)}`);
    update_vis(nodes,data);
});

socket.on("oram_add_edge", function (data) {
    console.log(`edge added: ${JSON.stringify(data)}`);
    edgesRaw.push(data);
    update_vis(nodes, edgesRaw);
});

function update_vis(update_nodes, update_edges) {

    console.log(`update_vis: ${JSON.stringify(update_nodes)}`);
    console.log(`update_edges: ${JSON.stringify(update_edges)}`);
    update_nodes = new vis.DataSet(update_nodes);
    update_edges = new vis.DataSet(update_edges);

    let data = {
        nodes: update_nodes,
        edges: update_edges
    };
    //update global nodes
    network.setData(data);
}

let nodes = null;

function process_nodes(leftNodesRaw, rightNodesRaw) {
    let processedNodes = []
    // 處理左側節點
    leftNodesRaw.forEach((node, index) => {
        processedNodes.push({
            ...node,
            x: xCoords.left,
            y: index * ySpacing,
            fixed: true, // 鎖定位置，使用者不可拖動
            color: '#66a3ff' // 給個顏色區分
        });
    });

// 處理右側節點
    rightNodesRaw.forEach((node, index) => {
        processedNodes.push({
            ...node,
            x: xCoords.right,
            y: index * ySpacing,
            fixed: true, // 鎖定位置
            color: '#ff9966' // 給個顏色區分
        });
    });
    nodes = processedNodes;
}


// 準備邊 (edges) 的資料
let edgesRaw = [];

// set node x and y coordinates
const xCoords = {
    left: -250, // 左側欄的 X 座標
    right: 250   // 右側欄的 X 座標
};
const ySpacing = 60; // 節點之間的垂直間距


// 找到 HTML 容器
const container = document.getElementById('vis_once');


const data = {
    nodes: null,
    edges: null
};

// 設定選項
const options = {
    // **關閉物理引擎**
    physics: {
        enabled: false
    },
    // 你也可以在這裡設定邊的樣式等等
    edges: {
        smooth: {
            type: 'cubicBezier', // 可以讓線條更平滑
            forceDirection: 'horizontal',
            roundness: 0.4,

        },
        arrows: {to: true},
    },
    interaction: {
        dragNodes: true, // 即使 fixed:true，這裡設 true 還是能觸發點擊事件
        dragView: true,
        zoomView: true
    }
};

// 6. 初始化網路圖
const network = new vis.Network(container, data, options);