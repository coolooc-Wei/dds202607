var socket = io();
socket.emit("oram_join");
socket.on("oram_data", function (data) {
    var messages = document.getElementById("test");
    messages.innerHTML += `<p>${data}</p>`;
});

