cmake_minimum_required(VERSION 3.14.0)

project(KGGNN LANGUAGES CXX CUDA)

find_package(CUDA REQUIRED)
find_package(Torch REQUIRED)
find_library(TORCH_PYTHON_LIBRARY torch_python PATHS "${TORCH_INSTALL_PREFIX}/lib")

set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -rdc=true -gencode=arch=compute_86,code=sm_86 -lcudadevrt")

include_directories(/root/anaconda3/envs/gnnadvisor/include/python3.6m)
include_directories(${PROJECT_SOURCE_DIR}/core/include)

set(SRC_DIR ${PROJECT_SOURCE_DIR}/core/src)
set(SRC_FILE ${SRC_DIR}/KG_GNN.cpp
${SRC_DIR}/gnn_run.cpp
${SRC_DIR}/gnn_analysis.cpp
${SRC_DIR}/aggregate.cu
${SRC_DIR}/aggregate_sddmm.cu
${SRC_DIR}/aggregate_gat.cu
${SRC_DIR}/flash_partition.cu
${SRC_DIR}/aggregate_gin.cu
${SRC_DIR}/preprocessing.cu
${SRC_DIR}/bin_pack.cu
${SRC_DIR}/gnn_mm.cpp
${SRC_DIR}/mm.cu
${SRC_DIR}/mm_pipeline.cu
${SRC_DIR}/spmm_mm_pipeline.cu
${SRC_DIR}/spmm_mm_pipeline_new.cu
${SRC_DIR}/spmm_mm_pipeline_final_new.cu
)

message("${TORCH_LIBRARIES}")
message("${TORCH_PYTHON_LIBRARY}")


add_library(KGGNN SHARED ${SRC_FILE})
target_link_libraries(KGGNN "${TORCH_LIBRARIES}" "${TORCH_PYTHON_LIBRARY}")
