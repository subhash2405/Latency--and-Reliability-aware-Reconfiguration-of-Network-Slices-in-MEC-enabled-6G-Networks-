
# output_file = open('../entity/simulation_output.txt', 'w')


adj_matrix = [
    [(1, 2), (3, 2)],
    [(0, 2), (2, 2), (3, 3), (4, 2), (5, 3)],
    [(1, 2), (5, 2)],
    [(0, 2), (1, 3), (4, 2)],
    [(1, 2), (3, 2), (5, 2), (7, 2)],
    [(1, 3), (2, 2), (4, 2), (7, 3), (8, 2)],
    [(3, 2), (7, 2)],
    [(3, 3), (4, 2), (5, 3), (6, 2), (8, 2)],
    [(7, 2), (5, 2)]
]

num_nodes = len(adj_matrix)


def floyd_warshall(adj_matrix, num_nodes):

    dist = [[float('inf')] * num_nodes for _ in range(num_nodes)]

    for i in range(num_nodes):
        dist[i][i] = 0

    for i in range(num_nodes):
        for neighbor, weight in adj_matrix[i]:
            dist[i][neighbor] = weight

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


distances = floyd_warshall(adj_matrix, num_nodes)

for i in range(num_nodes):
    print(f"Shortest distances from node {i}: {distances[i]}")

# output_file.close()
