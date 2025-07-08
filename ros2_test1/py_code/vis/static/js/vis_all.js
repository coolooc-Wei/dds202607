const container_all = document.getElementById('vis_all');

var data_ = {
    nodes: null,
    edges: null,
};
const network_all = new vis.Network(container_all, data_, options);


socket.on("oram_all_edges", function (data) {
    console.log(`Connected to server: ${JSON.stringify(data)}`);
    create_all(data);
});

function create_all(data) {
    let all_nodes = [];
    for (let time = 0; time <= data.time; time++) {
        for (let node = 0; node < data.node; node++) {
            all_nodes.push({
                id: `${time}_${node}`,
                label: `node_${node}`,
                x: xCoords.right*time,
                y: node * ySpacing,
                fixed: true,
                color: (time % 2 === 0) ? '#66a3ff' : '#ff9966',
            });
        }
    }

    all_edges = new vis.DataSet(data.edges);




    all_nodes = new vis.DataSet(all_nodes);

    let datas = {
        nodes: all_nodes,
        edges: all_edges
    }

    network_all.setData(datas);

}
