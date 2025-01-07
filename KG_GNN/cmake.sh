rm -rf build
mkdir build
cd build
cmake -DCMAKE_PREFIX_PATH="/root/anaconda3/envs/gnnadvisor/lib/python3.6/site-packages/torch/" ..
make -j 4

# export DIR=core/src

# nvcc -Wall -shared -std=c++11 -fPIC -Lbuild/  -lKGGNN \
#     -I/root/anaconda3/envs/gnnadvisor/lib/python3.6/site-packages/torch/include/pybind11 \
#     `cd /root/anaconda3/envs/gnnadvisor/lib/python3.6/site-packages/torch/include/pybind11 && python -mpybind11 --includes`  \
#     ${DIR}/KG_GNN.cpp ${DIR}/gnn_run.cpp ${DIR}/gnn_mm.cpp ${DIR}/gnn_analysis.cpp \
#     -o  KGGNN`python3-config --extension-suffix`