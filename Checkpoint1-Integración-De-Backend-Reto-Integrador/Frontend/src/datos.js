// Datos compartidos y ejemplos precargados (los mismos de Swagger en el backend).

export const INTEGRANTES = [
  { nombre: "Jonathan Hernández Lazcano", cuenta: "200417" },
  { nombre: "Camila Rodriguez Rosas", cuenta: "194100" },
  { nombre: "Daniel Peña Cruz", cuenta: "200818" },
];

// Grafo de 10 nodos de la Actividad 12, con las coordenadas de su imagen.
export const GRAFO_10 = {
  A: [["B", 15], ["C", 22], ["D", 10]],
  B: [["E", 35], ["F", 18]],
  C: [["E", 20], ["G", 45]],
  D: [["F", 28], ["G", 30]],
  E: [["H", 12], ["I", 25]],
  F: [["H", 40], ["I", 15]],
  G: [["I", 10], ["J", 50]],
  H: [["J", 14]],
  I: [["J", 8]],
  J: [],
};

export const COORDENADAS_10 = {
  A: [1521, 193], B: [1670, 546], C: [566, 311], D: [1814, 363], E: [278, 801],
  F: [1526, 986], G: [1399, 1118], H: [185, 1100], I: [1032, 1225], J: [721, 1295],
};

export const EJEMPLOS_AUTOMATAS = {
  AFD: {
    descripcion: "Acepta las cadenas sobre {a, b} con un número par de a's.",
    simbolos: ["a", "b"],
    estados: ["q0", "q1"],
    tabla: { q0: { a: "q1", b: "q0" }, q1: { a: "q0", b: "q1" } },
    inicial: "q0",
    finales: ["q0"],
    cadenas: ["", "aa", "aba", "bab", "abab"],
  },
  AFND: {
    descripcion: "Acepta las cadenas sobre {a, b} que terminan en abb.",
    simbolos: ["a", "b"],
    estados: ["q0", "q1", "q2", "q3"],
    tabla: {
      q0: { a: "q0, q1", b: "q0" },
      q1: { a: "", b: "q2" },
      q2: { a: "", b: "q3" },
      q3: { a: "", b: "" },
    },
    inicial: "q0",
    finales: ["q3"],
    cadenas: ["abb", "aabb", "ab", "babb"],
  },
  "AFND-ε": {
    descripcion: "a* seguido de b*: la transición λ pasa de la parte de a's a la de b's.",
    simbolos: ["a", "b"],
    estados: ["q0", "q1"],
    tabla: { q0: { a: "q0", b: "", λ: "q1" }, q1: { a: "", b: "q1", λ: "" } },
    inicial: "q0",
    finales: ["q1"],
    cadenas: ["", "aab", "abb", "ba", "bbb"],
  },
};

export const ALGORITMOS_RUTA = [
  { clave: "bfs", nombre: "BFS (anchura)", nota: "No informada · menos aristas", sinDestino: true },
  { clave: "dfs", nombre: "DFS (profundidad)", nota: "No informada · primera rama", sinDestino: true },
  { clave: "hill-climbing", nombre: "Hill-Climbing", nota: "Local · puede atorarse" },
  { clave: "greedy", nombre: "Voraz (Greedy)", nota: "Informada · f = h" },
  { clave: "astar", nombre: "A*", nota: "Informada · f = g + h · óptima" },
  { clave: "dijkstra", nombre: "Dijkstra", nota: "P · costo mínimo" },
];

export const ALGORITMOS_ORDEN = [
  { clave: "burbuja", nombre: "Burbuja", complejidad: "O(n²)", max: 3000 },
  { clave: "seleccion", nombre: "Selección", complejidad: "O(n²)", max: 3000 },
  { clave: "insercion", nombre: "Inserción", complejidad: "O(n²)", max: 3000 },
  { clave: "merge", nombre: "Merge sort", complejidad: "O(n log n)", max: 50000 },
  { clave: "quick", nombre: "Quick sort", complejidad: "O(n log n) prom.", max: 50000 },
  { clave: "heap", nombre: "Heap sort", complejidad: "O(n log n)", max: 50000 },
  { clave: "counting", nombre: "Counting sort", complejidad: "O(n + k) · enteros", max: 50000 },
  { clave: "permutaciones", nombre: "Permutaciones", complejidad: "O(n · n!) · fuerza bruta", max: 8 },
];

// Paleta para distinguir algoritmos en tablas, grafo y gráficas.
export const COLORES = {
  bfs: "#2563eb",
  dfs: "#9333ea",
  "hill-climbing": "#d97706",
  greedy: "#db2777",
  astar: "#059669",
  dijkstra: "#0891b2",
  burbuja: "#ef4444",
  seleccion: "#f97316",
  insercion: "#eab308",
  merge: "#22c55e",
  quick: "#06b6d4",
  heap: "#3b82f6",
  counting: "#a855f7",
  permutaciones: "#64748b",
};
