#include <vector>
#include <queue>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <algorithm>

using namespace std;

#define MAX 10005
#define Node pair<int,int>
#define INF (1<<30)

static vector<Node> ady[MAX]; 
static int V = 0;
static int distancia[MAX];
static bool visitado[MAX];
static int previo[MAX];

struct cmp {
    bool operator()(const Node &a, const Node &b) const {
        return a.second > b.second;
    }
};

static priority_queue<Node, vector<Node>, cmp> Q;

static void init(){
    if (V <= 0) return;
    for (int i = 0; i <= V && i < MAX; ++i){
        distancia[i] = INF;
        visitado[i] = false;
        previo[i] = -1;
    }
    Q = priority_queue<Node, vector<Node>, cmp>();
}

static void relajacion(int actual, int adyacente, int peso){
    if (distancia[actual] + peso < distancia[adyacente]){
        distancia[adyacente] = distancia[actual] + peso;
        previo[adyacente] = actual;
        Q.push(Node(adyacente, distancia[adyacente]));
    }
}

static void dijkstra(int inicial){
    init();
    Q.push(Node(inicial, 0));
    distancia[inicial] = 0;
    int actual, adyacente, peso;
    while (!Q.empty()){
        actual = Q.top().first;
        Q.pop();
        if (visitado[actual]) continue;
        visitado[actual] = true;
        for (size_t i = 0; i < ady[actual].size(); ++i){
            adyacente = ady[actual][i].first;
            peso = ady[actual][i].second;
            if (!visitado[adyacente]){
                relajacion(actual, adyacente, peso);
            }
        }
    }
}

extern "C" {

// Crea el grafo con V vértices (1..V)
__declspec(dllexport) void create_graph(int vertices){
    if (vertices < 1) return;
    V = vertices;
    // limpiar estructuras
    for (int i = 0; i <= V && i < MAX; ++i){
        ady[i].clear();
    }
    init();
}

// Agrega una arista (u,v,peso). El grafo será tratado como no-dirigido
__declspec(dllexport) void add_edge(int u, int v, int peso){
    if (u <= 0 || v <= 0 || u >= MAX || v >= MAX) return;
    ady[u].push_back(Node(v, peso));
    ady[v].push_back(Node(u, peso));
}

// Ejecuta Dijkstra desde 'inicial'
__declspec(dllexport) void run_dijkstra(int inicial){
    if (inicial <= 0 || inicial >= MAX) return;
    dijkstra(inicial);
}

// Obtiene la distancia calculada al nodo 'node'.
// Si node fuera inválido devuelve -1.
__declspec(dllexport) int get_distance(int node){
    if (node <= 0 || node >= MAX) return -1;
    if (V == 0) return -1;
    int d = distancia[node];
    if (d >= INF/2) return -1; // considerar no alcanzable
    return d;
}

// Obtiene el camino desde el origen usado en el último run_dijkstra hasta 'dest'.
// buffer: puntero a memoria donde se escribirá una cadena C (por ejemplo "1,4,2,3").
// bufsize: tamaño del buffer.
// Devuelve 0 en éxito, -1 en error (p.ej. destino inválido o buffer muy pequeño).
__declspec(dllexport) int get_path_csv(int dest, char* buffer, int bufsize){
    if (dest <= 0 || dest >= MAX) return -1;
    if (V == 0) return -1;
    if (buffer == nullptr || bufsize <= 0) return -1;

    // reconstruir camino usando previo
    vector<int> path;
    int cur = dest;
    
    // si destino no fue alcanzado previo puede ser -1 AND distance INF
    if (distancia[dest] >= INF/2 && previo[dest] == -1){
        // inalcanzable
        const char* noalc = "UNREACHABLE";
        size_t len = strlen(noalc);
        if ((int)len + 1 > bufsize) return -1;
        strncpy(buffer, noalc, bufsize - 1);
        buffer[bufsize - 1] = '\0'; // asegurar terminación
        return 0;
    }

    while (cur != -1){
        path.push_back(cur);
        cur = previo[cur];
    }
    reverse(path.begin(), path.end());

    // construir CSV
    stringstream ss;
    for (size_t i = 0; i < path.size(); ++i){
        if (i) ss << ",";
        ss << path[i];
    }
    string s = ss.str();
    if ((int)s.size() + 1 > bufsize) return -1;
    
    strncpy(buffer, s.c_str(), bufsize - 1);
    buffer[bufsize - 1] = '\0'; // asegurar terminación
    return 0;
}

// Limpia grafo/estado interno
__declspec(dllexport) void clear_graph(){
    if (V == 0) return;
    for (int i = 0; i <= V && i < MAX; ++i){
        ady[i].clear();
    }
    V = 0;
    init();
}

}