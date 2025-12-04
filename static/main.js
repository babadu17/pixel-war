const socket = io();

let grid = null;
let width = 0, height = 0;

const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const colorInput = document.getElementById("color");
const pixelSizeSelect = document.getElementById("pixelSize");
let pixelSize = parseInt(pixelSizeSelect.value);

pixelSizeSelect.addEventListener("change", () => {
  pixelSize = parseInt(pixelSizeSelect.value);
  renderGrid();
});

// CONNECTION
socket.on("connect", () => {
  document.getElementById("status").textContent = "connecté";
});
socket.on("disconnect", () => {
  document.getElementById("status").textContent = "déconnecté";
});

// FULL GRID RECEIVED
socket.on("full_grid", (data) => {
  width = data.width;
  height = data.height;
  grid = data.grid;
  resizeCanvas();
  renderGrid();
});

// UPDATE
socket.on("pixel_update", (d) => {
  grid[d.y][d.x] = d.color;
  drawPixel(d.x, d.y, d.color);
});

socket.on("cooldown", (d) => {
  document.getElementById("status").textContent =
    "cooldown " + d.remaining.toFixed(2) + "s";
  setTimeout(() => document.getElementById("status").textContent = "connecté", 800);
});

function resizeCanvas() {
  canvas.width = width * pixelSize;
  canvas.height = height * pixelSize;
}

function renderGrid() {
  if (!grid) return;
  resizeCanvas();
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++)
      drawPixel(x, y, grid[y][x]);
}

function drawPixel(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x * pixelSize, y * pixelSize, pixelSize, pixelSize);
}

// CLICK → PLACE PIXEL
canvas.addEventListener("click", (ev) => {
  const rect = canvas.getBoundingClientRect();
  const gx = Math.floor((ev.clientX - rect.left) / pixelSize);
  const gy = Math.floor((ev.clientY - rect.top) / pixelSize);
  socket.emit("place_pixel", { x: gx, y: gy, color: colorInput.value });
});

// DRAG
let mouseDown = false;
canvas.addEventListener("mousedown", () => mouseDown = true);
canvas.addEventListener("mouseup", () => mouseDown = false);
canvas.addEventListener("mousemove", (ev) => {
  if (!mouseDown) return;
  const rect = canvas.getBoundingClientRect();
  const gx = Math.floor((ev.clientX - rect.left) / pixelSize);
  const gy = Math.floor((ev.clientY - rect.top) / pixelSize);
  socket.emit("place_pixel", { x: gx, y: gy, color: colorInput.value });
});
