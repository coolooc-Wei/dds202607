const container_all = document.getElementById('vis_all');

var data_ = {
    nodes: null,
    edges: null,
};
const network_all = new vis.Network(container_all, data_, options);

let all_nodes = [];
let all_edges = [];
let round_start = 0;
let round_end = 20000-1;
socket.on("oram_all_edges", function (data) {
    console.log(`get all: ${JSON.stringify(data)}`);
    all_nodes = [];
    for (let time = 0; time <= data.time; time++) {
        for (let node = 0; node < data.node; node++) {
            all_nodes.push({
                id: `${time}_${node}`,
                label: `node_${node}`,
                x: xCoords.right * time,
                y: node * ySpacing,
                fixed: true,
                color: (time % 2 === 0) ? '#66a3ff' : '#ff9966',
            });
        }
        all_nodes.push({
            id: `${time}_label`,
            label: `${time}`,
            x: xCoords.right * time,
            y: data.node * ySpacing,
            fixed: true,
            color: '#808080',
        });
    }


    all_edges = data.edges;
    update_all();
});

function update_all(edge_label = null) {

    let tmp_nodes = all_nodes.filter(node => {
        let time = parseInt(node.id.split('_')[0]);
        return time >= round_start && time <= round_end;
    });
    let tmp_edges = all_edges.filter(edge => {
        let time = parseInt(edge.from.split('_')[0]);
        return time >= round_start && time <= round_end && (!edge_label || edge_label === convert_edge_color_to_label(edge.color));
    });


    let datas = {
        nodes: new vis.DataSet(tmp_nodes),
        edges: new vis.DataSet(tmp_edges)
    }

    network_all.setData(datas);
}

function convert_edge_color_to_label(color) {
    switch (color) {
        case 'red':
            return 'fake';
        case 'green':
            return 'real';
    }

}



function all_round_set_range() {
    round_start = parseInt(document.getElementById('all_round_start').value);
    round_end = parseInt(document.getElementById('all_round_end').value);

    if (isNaN(round_start) || isNaN(round_end) || round_start < 0 || round_end < 0 || round_start > round_end) {
        console.log("Invalid round range.");
        return;
    }
    update_all();
}
