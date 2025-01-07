import dgl
import torch
import torch.nn.functional as F
import torch.nn as nn
from load_dataset import *

torch.ops.load_library("../build/libgat.so")

from utils import *
import sys
import time
from perf_time import * 

import rabbit

import os

os.environ["CUDA_VISIBLE_DEVICES"] = '0'
torch.manual_seed(970702)

if (len(sys.argv) < 2 or len(sys.argv) > 4):
    print("Usage: python test_dgl_gcn.py [dataset] [outcsv_name | optional] [fullcsv_name | optional]")
    exit(1)

dataset_dir = sys.argv[1]
if len(sys.argv) >= 3:
    outcsv_name = sys.argv[2]
else:
    outcsv_name = None

if len(sys.argv) == 4:
    fullcsv_name = sys.argv[3]
else:
    fullcsv_name = None

# Load and initialize input data
if ('.pt' in dataset_dir):
    graph_data = dataset_load(dataset_dir)
    in_dim, out_dim = dataset_prop(graph_data)
    num_nodes = graph_data.num_nodes
elif ('.mtx' in dataset_dir):
    graph_coo = read_mtx(dataset_dir)
    num_nodes = graph_coo.get_shape()[0]
    in_dim = 32
elif ('.csr' in dataset_dir):
    graph_csr = read_csr(dataset_dir)
    num_nodes = graph_csr.get_shape()[0]
    in_dim = 32
else:
    exit

# test setup
gcn_hidden = 64
out_dim = 32
# out_dim = int((out_dim + 31) / 32) * 32

print("layer feature: ", in_dim, gcn_hidden, out_dim)

weight_init = True

if (weight_init):
    random_seed = 123
    torch.manual_seed(random_seed)
    weight0 = torch.randn(in_dim, gcn_hidden)
    weight1 = torch.randn(gcn_hidden, out_dim)
    att_src0 = torch.randn(1, 1, gcn_hidden)
    att_dst0 = torch.randn(1, 1, gcn_hidden)
    att_src1 = torch.randn(1, 1, out_dim)
    att_dst1 = torch.randn(1, 1, out_dim)
    bias0 = torch.randn(gcn_hidden)
    bias1 = torch.randn(out_dim)
    paras = {'w0': weight0, 'w1': weight1, 'b0': bias0, 'b1': bias1, \
    'as0': att_src0, 'ad0': att_dst0, 'as1': att_src1, 'ad1':att_dst1}
else:
    paras = None

input_feature = torch.randn(num_nodes, in_dim)

# Set device and move data
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
input_feature = input_feature.to(device)
perf_time_init(dataset_dir)

reorder = True

# Transform to CSR format
if ('.pt' in dataset_dir):
    #graph_data = graph_data.to(device)
    graph_csr = graph_to_csr(graph_data, reorder = reorder, show_degree = True)
elif ('.mtx' in dataset_dir):
    graph_csr = coo_to_csr(num_nodes, graph_coo, reorder = reorder, show_degree = True)
elif ('.csr' in dataset_dir):
    graph_csr = csr_transform(graph_csr, add_self_loop = True, reorder = reorder, show_degree = True)
    pass
else:
    exit

# graph_coo = graph_csr.tocoo()

# coorow = graph_coo.row.astype(int)
# coocol = graph_coo.col.astype(int)
# edge_index = np.array([coocol, coorow])
# graph_data.edge_index = torch.tensor(edge_index, dtype=torch.long).to(device)

in_dim = 64
fd = 32
# prepare data
m = len(graph_csr.indptr) - 1
nnz = len(graph_csr.indices)
avg_rnz = 1.0 * nnz / m
max_rnz = max(graph_csr.indptr[1: m+1] - graph_csr.indptr[0: m])

rowptr = torch.tensor(graph_csr.indptr).to(device)
indices = torch.tensor(graph_csr.indices).to(device)
f_ori = torch.randn(m, in_dim).to(device)
w_ori = torch.randn(in_dim, fd).to(device)
f = torch.randn(m, fd).to(device)
fo = torch.zeros(m, fd).to(device)
we = torch.randn(fd, 2).to(device)
lr = torch.randn(1, 1).to(device)
e =  torch.randn(m, 2).to(device)
em = torch.zeros(m, 1).to(device)
es = torch.zeros(m, 1).to(device)
h = torch.zeros(nnz, 1).to(device)
ho = torch.zeros(nnz, 1).to(device)

perf_time_start("preprocessing")
info = torch.ops.gatlib.preprocessing(rowptr, indices, 1)
perf_time_end()

perf_time_start("warmup")
# torch.ops.gatlib.gat_kernel_0(info, rowptr, indices, fd, f, fo, we, lr, e, em, es, h, ho)
perf_time_end()

# print(h, em)

if (outcsv_name):
    f1 = open(outcsv_name, "a")
if (fullcsv_name):
    f2 = open(fullcsv_name, "a")

best_layer_time = -1
best_i = -1
for i in range(24):
    # em2 = torch.zeros(m, 1).to(device)
    # ho2 = torch.zeros(nnz, 1).to(device)
    # h2 = torch.zeros(nnz, 1).to(device)
    # es2 = torch.zeros(m, 1).to(device)
    # fo2 = torch.zeros(m, fd).to(device)

    func_name = "torch.ops.gatlib.gat_kernel_{:d}(info, rowptr, indices, fd, f, fo, we, lr, e, em, es, h, ho)".format(i)

    eval(func_name)

    h.zero_()
    fo.zero_()

    perf_time_start("test_kernel{:d}".format(i))
    torch.mm(f_ori, w_ori)
    eval(func_name)
    layer_time = perf_time_end()

    if (best_layer_time == -1 or layer_time < best_layer_time):
        best_i = i
        best_layer_time = layer_time

    # print(torch.norm(h - h2))
    # print(h2)
    
    # print(es2)
    # print(torch.norm(es2 - es))
    # print(torch.norm(fo2 - fo))
    # print(torch.max(es2 - es))
    # maxi = torch.argmax(es2 - es)
    # print(es2[maxi], es[maxi])
    # # maxi = 115359
    # print(maxi, rowptr[maxi], rowptr[maxi+1])
    # print(em[maxi])
    # print(em2[maxi])
    # print(em2)
    # print(torch.norm(ho2 - ho))
    # print(em2)
    first_idx = dataset_dir.rfind('/') + 1
    last_idx = dataset_dir.rfind('.')

    if (fullcsv_name):
        f2.write("{},{:d},{:f}\n".format(dataset_dir[first_idx: last_idx], i, layer_time))

print("best i", best_i, "best time:", best_layer_time)

if (outcsv_name):
    f1.write("{},{:d},{:f}\n".format(dataset_dir[first_idx: last_idx], best_i, best_layer_time))

# print(em2, em)

# fo2 = torch.zeros(m, 32).to(device)

# perf_time_start("nd parallel")
# torch.ops.gatlib.gat_kernel_0(info, rowptr, indices, f, fo, we, e, em, es, h)
# perf_time_end()

# perf_time_start("ed parallel")
# torch.ops.gatlib.gat_kernel_1(info, rowptr, indices, f, fo2, we, e, em, es, h)
# perf_time_end()

# print(torch.norm(fo - fo2))