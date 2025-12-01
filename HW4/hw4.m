clc; clear; close all;
K = 4; % clusters

% step 1
E = csvread('example1.dat');
col1 = E(:,1);
col2 = E(:,2);
max_ids = max(max(col1,col2));
As= sparse(col1, col2, 1, max_ids, max_ids); 
A = full(adjacency(graph(As)));
G = graph(A);
figure(1);
spy(A);

% step 2
D = diag(sum(A, 2));
L = D^(-1/2)*A*D^(-1/2);
%L = D - A;

% step 3
[VK, DK] = eigs(L, K, 'largestabs');
%[VK, DK] = eigs(L, K, 'smallestabs');

X = VK;

% step 4
Y = X ./ sqrt(sum(X.^2, 2));  

% step 5
clusters = kmeans(Y, K);

% step 6
colors = lines(K); % 4 distinct colors
figure;
h = plot(G, "MarkerSize", 6);

for i = 1:K
    highlight(h, find(clusters == i), 'NodeColor', colors(i,:));
end

[vecs, vals] = eigs(L, 2, 'smallestreal');
fiedler_vector = vecs(:, 2);
sorted_fiedler = sort(fiedler_vector);
figure(4);
plot(sorted_fiedler, 'LineWidth', 1.5);
xlabel('Node index (sorted by Fiedler value)');
ylabel('Fiedler vector value');
grid on;
